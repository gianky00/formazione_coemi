from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import CorsiMaster, Attestati, ValidationStatus, Dipendenti
import logging
from app.services import ai_extraction
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
        from_attributes = True

class CertificatoCreateSchema(BaseModel):
    nome: str
    corso: str
    data_rilascio: str
    data_scadenza: Optional[str] = None

from app.db.session import SessionLocal

router = APIRouter()

def seed_database():
    db = SessionLocal()
    try:
        corsi = [
            {"nome_corso": "ANTINCENDIO", "validita_mesi": 60, "categoria_corso": "ANTINCENDIO"},
            {"nome_corso": "PRIMO SOCCORSO", "validita_mesi": 36, "categoria_corso": "PRIMO SOCCORSO"},
            {"nome_corso": "ASPP", "validita_mesi": 60, "categoria_corso": "ASPP"},
            {"nome_corso": "RSPP", "validita_mesi": 60, "categoria_corso": "RSPP"},
            {"nome_corso": "ATEX", "validita_mesi": 60, "categoria_corso": "ATEX"},
            {"nome_corso": "BLSD", "validita_mesi": 12, "categoria_corso": "BLSD"},
            {"nome_corso": "CARROPONTE", "validita_mesi": 60, "categoria_corso": "CARROPONTE"},
            {"nome_corso": "DIRETTIVA SEVESO", "validita_mesi": 60, "categoria_corso": "DIRETTIVA SEVESO"},
            {"nome_corso": "DIRIGENTI E FORMATORI", "validita_mesi": 60, "categoria_corso": "DIRIGENTI E FORMATORI"},
            {"nome_corso": "GRU A TORRE E PONTE", "validita_mesi": 60, "categoria_corso": "GRU A TORRE E PONTE"},
            {"nome_corso": "H2S", "validita_mesi": 60, "categoria_corso": "H2S"},
            {"nome_corso": "IMBRACATORE", "validita_mesi": 60, "categoria_corso": "IMBRACATORE"},
            {"nome_corso": "FORMAZIONE GENERICA ART.37", "validita_mesi": 60, "categoria_corso": "FORMAZIONE GENERICA ART.37"},
            {"nome_corso": "PREPOSTO", "validita_mesi": 24, "categoria_corso": "PREPOSTO"},
            {"nome_corso": "GRU SU AUTOCARRO", "validita_mesi": 60, "categoria_corso": "GRU SU AUTOCARRO"},
            {"nome_corso": "PLE", "validita_mesi": 60, "categoria_corso": "PLE"},
            {"nome_corso": "PES PAV PEI C CANTIERE", "validita_mesi": 60, "categoria_corso": "PES PAV PEI C CANTIERE"},
            {"nome_corso": "LAVORI IN QUOTA", "validita_mesi": 60, "categoria_corso": "LAVORI IN QUOTA"},
            {"nome_corso": "MACCHINE OPERATRICI", "validita_mesi": 60, "categoria_corso": "MACCHINE OPERATRICI"},
            {"nome_corso": "MANITOU P.ROTATIVE", "validita_mesi": 60, "categoria_corso": "MANITOU P.ROTATIVE"},
            {"nome_corso": "MEDICO COMPETENTE", "validita_mesi": 0, "categoria_corso": "MEDICO COMPETENTE"},
            {"nome_corso": "MULETTO CARRELISTI", "validita_mesi": 60, "categoria_corso": "MULETTO CARRELISTI"},
            {"nome_corso": "SOPRAVVIVENZA E SALVATAGGIO IN MARE", "validita_mesi": 60, "categoria_corso": "SOPRAVVIVENZA E SALVATAGGIO IN MARE"},
            {"nome_corso": "SPAZI CONFINATI DPI III E AUTORESPIRATORI", "validita_mesi": 60, "categoria_corso": "SPAZI CONFINATI DPI III E AUTORESPIRATORI"},
            {"nome_corso": "HLO", "validita_mesi": 0, "categoria_corso": "HLO"},
            {"nome_corso": "ALTRO", "validita_mesi": 0, "categoria_corso": "ALTRO"},
        ]

        for corso_data in corsi:
            db_corso = db.query(CorsiMaster).filter(CorsiMaster.nome_corso == corso_data["nome_corso"]).first()
            if not db_corso:
                new_corso = CorsiMaster(**corso_data)
                db.add(new_corso)

        db.commit()
    finally:
        db.close()

@router.on_event("startup")
async def startup_event():
    seed_database()
    logging.info("Database seeded successfully.")

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
                CorsiMaster.nome_corso.ilike(f"%{categoria_estratta}%")
            ).first()

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

    # 1. Leggi i bytes del PDF direttamente dalla richiesta
    pdf_bytes = await file.read()

    # 2. Chiama il servizio AI con i bytes del PDF
    extracted_data = ai_extraction.extract_entities_with_ai(pdf_bytes)

    if "error" in extracted_data:
        raise HTTPException(status_code=500, detail=extracted_data["error"])

    # 3. Applica la logica di business e formatta i dati
    final_entities = calculate_expiration_date(extracted_data, db)

    # 4. Restituisci il risultato
    return {"filename": file.filename, "text": "Estrazione PDF Diretta Eseguita", "entities": final_entities}

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
        stato = "attivo"
        if attestato.data_scadenza_calcolata and attestato.data_scadenza_calcolata < date.today():
            stato = "scaduto"

        result.append(CertificatoSchema(
            id=attestato.id,
            nome=f"{attestato.dipendente.nome} {attestato.dipendente.cognome}",
            corso=attestato.corso.nome_corso,
            categoria=attestato.corso.categoria_corso or "General",
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

    stato = "attivo"
    if db_attestato.data_scadenza_calcolata and db_attestato.data_scadenza_calcolata < date.today():
        stato = "scaduto"

    return CertificatoSchema(
        id=db_attestato.id,
        nome=f"{db_attestato.dipendente.nome} {db_attestato.dipendente.cognome}",
        corso=db_attestato.corso.nome_corso,
        categoria=db_attestato.corso.categoria_corso or "General",
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

    stato = "attivo"
    if db_certificato.data_scadenza_calcolata and db_certificato.data_scadenza_calcolata < date.today():
        stato = "scaduto"

    return CertificatoSchema(
        id=db_certificato.id,
        nome=f"{db_certificato.dipendente.nome} {db_certificato.dipendente.cognome}",
        corso=db_certificato.corso.nome_corso,
        categoria=db_certificato.corso.categoria_corso or "General",
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
