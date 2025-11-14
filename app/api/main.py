from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import CorsiMaster, Attestati, ValidationStatus, Dipendenti
from app.services import ocr, ai_extraction
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel
from typing import Optional, List

class CertificatoSchema(BaseModel):
    id: int
    nome: str
    corso: str
    data_rilascio: str
    data_scadenza: str

    class Config:
        orm_mode = True

class CertificatoCreateSchema(BaseModel):
    nome: str
    corso: str
    data_rilascio: str
    data_scadenza: str

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
    """
    # Adatta i dati estratti allo schema interno
    entities = {
        "nome": extracted_data.get("nome"),
        "corso": extracted_data.get("corso"),
        "data_rilascio": None,
        "data_scadenza": None
    }

    data_rilascio_str = extracted_data.get("data_rilascio")

    # 1. Parsing della data
    if data_rilascio_str:
        try:
            # Gemini dovrebbe restituire DD-MM-YYYY, facciamo il parsing
            parsed_date = datetime.strptime(data_rilascio_str, '%d-%m-%Y').date()
            entities["data_rilascio"] = parsed_date
        except (ValueError, TypeError):
            entities["data_rilascio"] = None

    # 2. Logica di Business (Calcolo Scadenza)
    if entities["corso"] and entities["data_rilascio"]:
        corsi = db.query(CorsiMaster).all()
        course_names = {corso.nome_corso.lower(): corso for corso in corsi}
        extracted_course_lower = entities["corso"].lower()

        for course_name, corso_obj in course_names.items():
            if course_name in extracted_course_lower:
                if corso_obj.validita_mesi > 0:
                    expiration_date = entities["data_rilascio"] + relativedelta(months=corso_obj.validita_mesi)
                    entities["data_scadenza"] = expiration_date
                break

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
        result.append(CertificatoSchema(
            id=attestato.id,
            nome=f"{attestato.dipendente.nome} {attestato.dipendente.cognome}",
            corso=attestato.corso.nome_corso,
            data_rilascio=attestato.data_rilascio.strftime('%d/%m/%Y'),
            data_scadenza=attestato.data_scadenza_calcolata.strftime('%d/%m/%Y')
        ))
    return result

@router.post("/certificati/", response_model=CertificatoSchema)
def create_certificato(certificato: CertificatoCreateSchema, db: Session = Depends(get_db)):
    try:
        nome_parts = certificato.nome.split()
        db_dipendente = db.query(Dipendenti).filter(Dipendenti.nome == nome_parts[0], Dipendenti.cognome == nome_parts[1]).first()
        if not db_dipendente:
            raise HTTPException(status_code=404, detail="Dipendente non trovato")
    except IndexError:
        raise HTTPException(status_code=400, detail="Formato nome non valido. Inserire nome e cognome.")

    db_corso = db.query(CorsiMaster).filter(CorsiMaster.nome_corso == certificato.corso).first()
    if not db_corso:
        raise HTTPException(status_code=404, detail="Corso non trovato")

    db_attestato = Attestati(
        id_dipendente=db_dipendente.id,
        id_corso=db_corso.id,
        data_rilascio=datetime.strptime(certificato.data_rilascio, '%d/%m/%Y').date(),
        data_scadenza_calcolata=datetime.strptime(certificato.data_scadenza, '%d/%m/%Y').date(),
        stato_validazione=ValidationStatus.MANUAL
    )
    db.add(db_attestato)
    db.commit()
    db.refresh(db_attestato)

    return CertificatoSchema(
        id=db_attestato.id,
        nome=f"{db_attestato.dipendente.nome} {db_attestato.dipendente.cognome}",
        corso=db_attestato.corso.nome_corso,
        data_rilascio=db_attestato.data_rilascio.strftime('%d/%m/%Y'),
        data_scadenza=db_attestato.data_scadenza_calcolata.strftime('%d/%m/%Y')
    )

@router.put("/certificati/{certificato_id}", response_model=CertificatoSchema)
def update_certificato(certificato_id: int, nome: str, corso: str, data_rilascio: str, data_scadenza: str, db: Session = Depends(get_db)):
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
    db_certificato.data_scadenza_calcolata = datetime.strptime(data_scadenza, '%d/%m/%Y').date()
    db.commit()
    db.refresh(db_certificato)
    return CertificatoSchema(
        id=db_certificato.id,
        nome=f"{db_certificato.dipendente.nome} {db_certificato.dipendente.cognome}",
        corso=db_certificato.corso.nome_corso,
        data_rilascio=db_certificato.data_rilascio.strftime('%d/%m/%Y'),
        data_scadenza=db_certificato.data_scadenza_calcolata.strftime('%d/%m/%Y')
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
