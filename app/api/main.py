from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import CorsiMaster, Attestati, ValidationStatus, Dipendenti
import logging
from app.services import ocr, ai_extraction
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel
from typing import Optional, List

class CertificatoSchema(BaseModel):
    id: int
    nome: str
    corso: str
    categoria: str
    data_rilascio: str
    data_scadenza: Optional[str] = None
    stato_certificato: str

    class Config:
        orm_mode = True

class CertificatoCreateSchema(BaseModel):
    nome: str
    corso: str
    data_rilascio: str
    data_scadenza: Optional[str] = None

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Welcome to the Scadenziario IA API"}

@router.get("/corsi")
def get_corsi(db: Session = Depends(get_db)):
    return db.query(CorsiMaster).all()

@router.get("/health")
def health_check():
    return {"status": "ok"}

def calculate_expiration_date(extracted_data: dict, db: Session) -> dict:
    """
    Applica la logica di business per calcolare la data di scadenza.
    Usa la 'categoria' estratta dall'AI per trovare la corrispondenza nel DB.
    """

    # Prendi i dati estratti dall'IA
    nome_estratto = extracted_data.get("nome")
    corso_estratto = extracted_data.get("corso")
    data_rilascio_str = extracted_data.get("data_rilascio")
    categoria_estratta = extracted_data.get("categoria") # <-- NUOVO CAMPO

    # Adatta i dati allo schema interno
    entities = {
        "nome": nome_estratto,
        "corso": corso_estratto,
        "categoria": categoria_estratta, # <-- Salviamo anche la categoria
        "data_rilascio": None,
        "data_scadenza": None
    }

    # 1. Parsing della data
    if data_rilascio_str:
        try:
            parsed_date = datetime.strptime(data_rilascio_str, '%d-%m-%Y').date()
            entities["data_rilascio"] = parsed_date
        except (ValueError, TypeError):
            entities["data_rilascio"] = None

    # 2. Logica di Business (Calcolo Scadenza con Fallback)
    if entities["data_rilascio"]:
        corso_obj = None
        # Prima tenta con la categoria esatta (case-insensitive)
        if categoria_estratta:
            corso_obj = db.query(CorsiMaster).filter(
                CorsiMaster.nome_corso.ilike(categoria_estratta)
            ).first()

        # Se non trova corrispondenze, prova il fallback basato su sottostringa
        if not corso_obj and corso_estratto:
            logging.warning(f"Categoria '{categoria_estratta}' non trovata. Tentativo di fallback su sottostringa.")
            tutti_i_corsi = db.query(CorsiMaster).all()
            for master_corso in tutti_i_corsi:
                if master_corso.nome_corso.lower() in corso_estratto.lower():
                    corso_obj = master_corso
                    logging.info(f"Fallback riuscito: '{corso_estratto}' associato a '{master_corso.nome_corso}'.")
                    break

        if corso_obj:
            if corso_obj.validita_mesi > 0:
                expiration_date = entities["data_rilascio"] + relativedelta(months=corso_obj.validita_mesi)
                entities["data_scadenza"] = expiration_date
        else:
            logging.warning(f"Nessun corso master corrispondente trovato per '{corso_estratto}'. Scadenza non calcolata.")


    # 3. Formatta le date come stringhe DD/MM/YYYY prima di restituirle
    if entities.get("data_rilascio"):
        entities["data_rilascio"] = entities["data_rilascio"].strftime('%d/%m/%Y')
    if entities.get("data_scadenza"):
        entities["data_scadenza"] = entities["data_scadenza"].strftime('%d/%m/%Y')

    return entities


@router.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = ocr.save_uploaded_file(file)
    text = ocr.extract_text_from_pdf(file_path)

    # Chiama il servizio AI (ora basato su Gemini)
    extracted_data = ai_extraction.extract_entities_with_ai(text)

    if "error" in extracted_data:
        return {"filename": file.filename, "text": text, "entities": {}, "error": extracted_data["error"]}

    # Applica la logica di business e formatta i dati
    final_entities = calculate_expiration_date(extracted_data, db)

    return {"filename": file.filename, "text": text, "entities": final_entities}

@router.get("/certificati/", response_model=List[CertificatoSchema])
def get_certificati(validated: Optional[bool] = Query(None), db: Session = Depends(get_db)):
    query = db.query(Attestati)
    if validated is not None:
        if validated:
            query = query.filter(Attestati.stato_validazione == ValidationStatus.MANUAL)
        else:
            query = query.filter(Attestati.stato_validazione == ValidationStatus.AUTOMATIC)

    attestati = query.all()
    result = []
    for attestato in attestati:
        stato = "Valido"
        if attestato.data_scadenza_calcolata:
            today = date.today()
            if attestato.data_scadenza_calcolata < today:
                stato = "Scaduto"
            elif (attestato.data_scadenza_calcolata - today).days <= 30:
                stato = "In Scadenza"

        # Handle cases where categoria_corso might be None
        categoria = attestato.corso.categoria_corso if attestato.corso.categoria_corso else "General"

        result.append(CertificatoSchema(
            id=attestato.id,
            nome=f"{attestato.dipendente.nome} {attestato.dipendente.cognome}",
            corso=attestato.corso.nome_corso,
            categoria=categoria,
            data_rilascio=attestato.data_rilascio.strftime('%d/%m/%Y'),
            data_scadenza=attestato.data_scadenza_calcolata.strftime('%d/%m/%Y') if attestato.data_scadenza_calcolata else None,
            stato_certificato=stato
        ))
    return result

@router.post("/certificati/", response_model=CertificatoSchema)
def create_certificato(certificato: CertificatoCreateSchema, db: Session = Depends(get_db)):
    nome_parts = certificato.nome.split()
    if len(nome_parts) < 2:
        raise HTTPException(status_code=400, detail="Formato nome non valido. Inserire nome e cognome.")

    # Try Lastname Firstname
    db_dipendente = db.query(Dipendenti).filter(Dipendenti.nome == nome_parts[1], Dipendenti.cognome == nome_parts[0]).first()
    # Try Firstname Lastname
    if not db_dipendente:
        db_dipendente = db.query(Dipendenti).filter(Dipendenti.nome == nome_parts[0], Dipendenti.cognome == nome_parts[1]).first()

    if not db_dipendente:
        print(f"Dipendente '{certificato.nome}' non trovato, lo creo...")
        db_dipendente = Dipendenti(
            cognome=nome_parts[0],
            nome=nome_parts[1]
        )
        db.add(db_dipendente)
        db.flush()

    db_corso = db.query(CorsiMaster).filter(CorsiMaster.nome_corso == certificato.corso).first()
    if not db_corso:
        print(f"Corso '{certificato.corso}' non trovato, lo creo...")
        db_corso = CorsiMaster(
            nome_corso=certificato.corso,
            validita_mesi=0,  # Default to 0 months validity
            categoria_corso="General"
        )
        db.add(db_corso)
        db.flush()

    db_attestato = Attestati(
        id_dipendente=db_dipendente.id,
        id_corso=db_corso.id,
        data_rilascio=datetime.strptime(certificato.data_rilascio, '%d/%m/%Y').date(),
        data_scadenza_calcolata=datetime.strptime(certificato.data_scadenza, '%d/%m/%Y').date() if certificato.data_scadenza else None,
        stato_validazione=ValidationStatus.AUTOMATIC
    )
    db.add(db_attestato)
    db.commit()
    db.refresh(db_attestato)

    stato = "Valido"
    if db_attestato.data_scadenza_calcolata:
        today = date.today()
        if db_attestato.data_scadenza_calcolata < today:
            stato = "Scaduto"
        elif (db_attestato.data_scadenza_calcolata - today).days <= 30:
            stato = "In Scadenza"

    return CertificatoSchema(
        id=db_attestato.id,
        nome=f"{db_attestato.dipendente.nome} {db_attestato.dipendente.cognome}",
        corso=db_attestato.corso.nome_corso,
        categoria=db_attestato.corso.categoria_corso,
        data_rilascio=db_attestato.data_rilascio.strftime('%d/%m/%Y'),
        data_scadenza=db_attestato.data_scadenza_calcolata.strftime('%d/%m/%Y') if db_attestato.data_scadenza_calcolata else None,
        stato_certificato=stato
    )

@router.put("/certificati/{certificato_id}", response_model=CertificatoSchema)
def update_certificato(certificato_id: int, nome: str, corso: str, data_rilascio: str, data_scadenza: Optional[str] = None, db: Session = Depends(get_db)):
    db_certificato = db.query(Attestati).filter(Attestati.id == certificato_id).first()
    if not db_certificato:
        raise HTTPException(status_code=404, detail="Certificato non trovato")

    # Handle name and course changes
    try:
        nome_parts = nome.split()
        db_dipendente = db.query(Dipendenti).filter(Dipendenti.nome == nome_parts[0], Dipendenti.cognome == nome_parts[1]).first()
        if not db_dipendente:
            raise HTTPException(status_code=404, detail="Dipendente non trovato")
        db_certificato.id_dipendente = db_dipendente.id
    except IndexError:
        raise HTTPException(status_code=400, detail="Formato nome non valido. Inserire nome e cognome.")

    db_corso = db.query(CorsiMaster).filter(CorsiMaster.nome_corso == corso).first()
    if not db_corso:
        raise HTTPException(status_code=404, detail="Corso non trovato")
    db_certificato.id_corso = db_corso.id

    db_certificato.data_rilascio = datetime.strptime(data_rilascio, '%d/%m/%Y').date()
    if data_scadenza and data_scadenza.lower() != 'none':
        db_certificato.data_scadenza_calcolata = datetime.strptime(data_scadenza, '%d/%m/%Y').date()
    else:
        db_certificato.data_scadenza_calcolata = None

    db_certificato.stato_validazione = ValidationStatus.MANUAL
    db.commit()
    db.refresh(db_certificato)

    stato = "Valido"
    if db_certificato.data_scadenza_calcolata:
        today = date.today()
        if db_certificato.data_scadenza_calcolata < today:
            stato = "Scaduto"
        elif (db_certificato.data_scadenza_calcolata - today).days <= 30:
            stato = "In Scadenza"

    return CertificatoSchema(
        id=db_certificato.id,
        nome=f"{db_certificato.dipendente.nome} {db_certificato.dipendente.cognome}",
        corso=db_certificato.corso.nome_corso,
        categoria=db_certificato.corso.categoria_corso,
        data_rilascio=db_certificato.data_rilascio.strftime('%d/%m/%Y'),
        data_scadenza=db_certificato.data_scadenza_calcolata.strftime('%d/%m/%Y') if db_certificato.data_scadenza_calcolata else None,
        stato_certificato=stato
    )

@router.put("/certificati/{certificato_id}/valida")
def valida_certificato(certificato_id: int, db: Session = Depends(get_db)):
    db_certificato = db.query(Attestati).filter(Attestati.id == certificato_id).first()
    if not db_certificato:
        raise HTTPException(status_code=404, detail="Certificato non trovato")

    db_certificato.stato_validazione = ValidationStatus.MANUAL
    db.commit()
    db.refresh(db_certificato)
    return {"message": "Certificato validato con successo"}

@router.delete("/certificati/{certificato_id}")
def delete_certificato(certificato_id: int, db: Session = Depends(get_db)):
    db_certificato = db.query(Attestati).filter(Attestati.id == certificato_id).first()
    if not db_certificato:
        raise HTTPException(status_code=404, detail="Certificato non trovato")
    db.delete(db_certificato)
    db.commit()
    return {"message": "Certificato cancellato con successo"}
