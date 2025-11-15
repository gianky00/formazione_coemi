from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from app.db.session import get_db
from app.db.models import Corso, Certificato, ValidationStatus, Dipendente
import logging
from app.services import ai_extraction, certificate_logic
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

class CertificatoSchema(BaseModel):
    id: int
    dipendente: str
    corso: str
    categoria: str
    data_rilascio: str
    data_scadenza: Optional[str] = None
    stato_certificato: str

    model_config = {"from_attributes": True}

class CertificatoCreazioneSchema(BaseModel):
    nome: str = Field(..., min_length=1, description="Nome e cognome del dipendente")
    corso: str = Field(..., min_length=1, description="Nome del corso")
    categoria: str = Field(..., min_length=1, description="Categoria del corso")
    data_rilascio: str = Field(..., description="Data di rilascio in formato DD/MM/YYYY")
    data_scadenza: Optional[str] = Field(None, description="Data di scadenza in formato DD/MM/YYYY")

    @field_validator('data_rilascio')
    def valida_formato_data_rilascio(cls, v):
        if not v:
            raise ValueError("La data non può essere vuota.")
        try:
            datetime.strptime(v, '%d/%m/%Y')
        except ValueError:
            raise ValueError("Formato data non valido. Usare DD/MM/YYYY.")
        return v

    @field_validator('data_scadenza')
    def valida_formato_data_scadenza(cls, v):
        if v is None or not v.strip() or v.strip().lower() == 'none':
            return None
        try:
            datetime.strptime(v, '%d/%m/%Y')
        except ValueError:
            raise ValueError("Formato data non valido. Usare DD/MM/YYYY.")
        return v

class CertificatoAggiornamentoSchema(BaseModel):
    nome: str = Field(..., min_length=1, description="Nome e cognome del dipendente")
    corso: str = Field(..., min_length=1, description="Nome del corso")
    categoria: str = Field(..., min_length=1, description="Categoria del corso")
    data_rilascio: str = Field(..., description="Data di rilascio in formato DD/MM/YYYY")
    data_scadenza: Optional[str] = Field(None, description="Data di scadenza in formato DD/MM/YYYY")

    @field_validator('data_rilascio')
    def valida_formato_data_rilascio(cls, v):
        if not v:
            raise ValueError("La data non può essere vuota.")
        try:
            datetime.strptime(v, '%d/%m/%Y')
        except ValueError:
            raise ValueError("Formato data non valido. Usare DD/MM/YYYY.")
        return v

    @field_validator('data_scadenza')
    def valida_formato_data_scadenza(cls, v):
        if v is None or not v.strip() or v.strip().lower() == 'none':
            return None
        try:
            datetime.strptime(v, '%d/%m/%Y')
        except ValueError:
            raise ValueError("Formato data non valido. Usare DD/MM/YYYY.")
        return v

from app.db.session import SessionLocal

router = APIRouter()

def seed_database():
    """
    Popola il database con i corsi master predefiniti all'avvio dell'applicazione.
    Se un corso esiste già, viene saltato.
    """
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
            db_corso = db.query(Corso).filter(Corso.nome_corso == corso_data["nome_corso"]).first()
            if not db_corso:
                new_corso = Corso(**corso_data)
                db.add(new_corso)

        db.commit()
    finally:
        db.close()

@router.get("/")
def read_root():
    """Endpoint principale che restituisce un messaggio di benvenuto."""
    return {"message": "Welcome to the Scadenziario IA API"}

@router.get("/corsi")
def get_corsi(db: Session = Depends(get_db)):
    """Restituisce l'elenco di tutti i corsi master presenti nel database."""
    return db.query(Corso).all()

@router.get("/health")
def health_check():
    """Endpoint di health check per verificare lo stato dell'API."""
    return {"status": "ok"}


@router.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Carica un file PDF, estrae le entità tramite AI e calcola la data di scadenza.

    Args:
        file: Il file PDF da caricare.
        db: La sessione del database.

    Returns:
        Un dizionario con le entità estratte e la data di scadenza calcolata.
    """
    # 1. Leggi i bytes del PDF direttamente dalla richiesta
    pdf_bytes = await file.read()

    # 2. Chiama il servizio AI con i bytes del PDF
    extracted_data = ai_extraction.extract_entities_with_ai(pdf_bytes)

    if "error" in extracted_data:
        raise HTTPException(status_code=500, detail=extracted_data["error"])

    # 3. Applica la logica di business e formatta i dati
    final_entities = {}
    data_rilascio_str = extracted_data.get("data_rilascio")
    if data_rilascio_str:
        try:
            data_rilascio = datetime.strptime(data_rilascio_str, '%d-%m-%Y').date()
            categoria_estratta = extracted_data.get("categoria")
            corso_obj = db.query(Corso).filter(Corso.nome_corso.ilike(f"%{categoria_estratta}%")).first()
            if corso_obj:
                data_scadenza = certificate_logic.calculate_expiration_date(data_rilascio, corso_obj.validita_mesi)
                final_entities["data_scadenza"] = data_scadenza.strftime('%d/%m/%Y') if data_scadenza else None
            final_entities["data_rilascio"] = data_rilascio.strftime('%d/%m/%Y')
        except (ValueError, TypeError):
            pass

    final_entities.update({
        "nome": extracted_data.get("nome"),
        "corso": extracted_data.get("corso"),
        "categoria": extracted_data.get("categoria"),
    })


    # 4. Restituisci il risultato
    return {"filename": file.filename, "text": "Estrazione PDF Diretta Eseguita", "entities": final_entities}

@router.get("/certificati/", response_model=List[CertificatoSchema])
def get_certificati(validated: Optional[bool] = Query(None), db: Session = Depends(get_db)):
    """
    Recupera un elenco di certificati, con la possibilità di filtrare per stato di validazione.

    Args:
        validated: Se True, restituisce solo i certificati validati manualmente.
                   Se False, restituisce solo quelli con validazione automatica.
                   Se None, restituisce tutti i certificati.
        db: La sessione del database.

    Returns:
        Una lista di certificati che soddisfano i criteri di filtro.
    """
    query = db.query(Certificato).options(
        selectinload(Certificato.dipendente),
        selectinload(Certificato.corso)
    )
    if validated is not None:
        if validated:
            query = query.filter(Certificato.stato_validazione == ValidationStatus.MANUAL)
        else:
            query = query.filter(Certificato.stato_validazione == ValidationStatus.AUTOMATIC)

    certificati = query.all()
    result = []
    for certificato in certificati:
        stato = certificate_logic.get_certificate_status(certificato.data_scadenza_calcolata)
        result.append(CertificatoSchema(
            id=certificato.id,
            dipendente=f"{certificato.dipendente.nome} {certificato.dipendente.cognome}",
            corso=certificato.corso.nome_corso,
            categoria=certificato.corso.categoria_corso or "General",
            data_rilascio=certificato.data_rilascio.strftime('%d/%m/%Y'),
            data_scadenza=certificato.data_scadenza_calcolata.strftime('%d/%m/%Y') if certificato.data_scadenza_calcolata else None,
            stato_certificato=stato
        ))
    return result

@router.post("/certificati/", response_model=CertificatoSchema)
def create_certificato(certificato: CertificatoCreazioneSchema, db: Session = Depends(get_db)):
    """
    Crea un nuovo certificato nel database. Se il dipendente o il corso non esistono,
    vengono creati automaticamente (logica "Get or Create").

    Args:
        certificato: I dati del certificato da creare.
        db: La sessione del database.

    Returns:
        Il certificato appena creato.
    """
    nome_parts = certificato.nome.split()
    if len(nome_parts) < 2:
        raise HTTPException(status_code=400, detail="Formato nome non valido. Inserire nome e cognome.")

    # Try Lastname Firstname
    db_dipendente = db.query(Dipendente).filter(Dipendente.nome == nome_parts[1], Dipendente.cognome == nome_parts[0]).first()
    # Try Firstname Lastname
    if not db_dipendente:
        db_dipendente = db.query(Dipendente).filter(Dipendente.nome == nome_parts[0], Dipendente.cognome == nome_parts[1]).first()

    if not db_dipendente:
        print(f"Dipendente '{certificato.nome}' non trovato, lo creo...")
        db_dipendente = Dipendente(
            nome=nome_parts[0],
            cognome=nome_parts[1]
        )
        db.add(db_dipendente)
        db.flush()

    db_master_course = db.query(Corso).filter(Corso.categoria_corso.ilike(f"%{certificato.categoria}%")).first()
    if not db_master_course:
        raise HTTPException(status_code=404, detail=f"Categoria '{certificato.categoria}' non trovata.")

    db_corso = db.query(Corso).filter(Corso.nome_corso.ilike(f"%{certificato.corso}%")).first()
    if not db_corso:
        db_corso = Corso(
            nome_corso=certificato.corso,
            validita_mesi=db_master_course.validita_mesi,
            categoria_corso=db_master_course.categoria_corso
        )
        db.add(db_corso)
        db.flush()

    db_certificato = Certificato(
        dipendente_id=db_dipendente.id,
        corso_id=db_corso.id,
        data_rilascio=datetime.strptime(certificato.data_rilascio, '%d/%m/%Y').date(),
        data_scadenza_calcolata=datetime.strptime(certificato.data_scadenza, '%d/%m/%Y').date() if certificato.data_scadenza else None,
        stato_validazione=ValidationStatus.AUTOMATIC
    )
    try:
        db.add(db_certificato)
        db.commit()
        db.refresh(db_certificato)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Errore di integrità: il certificato potrebbe già esistere.")

    stato = certificate_logic.get_certificate_status(db_certificato.data_scadenza_calcolata)
    return CertificatoSchema(
        id=db_certificato.id,
        dipendente=f"{db_certificato.dipendente.nome} {db_certificato.dipendente.cognome}",
        corso=db_certificato.corso.nome_corso,
        categoria=db_certificato.corso.categoria_corso or "General",
        data_rilascio=db_certificato.data_rilascio.strftime('%d/%m/%Y'),
        data_scadenza=db_certificato.data_scadenza_calcolata.strftime('%d/%m/%Y') if db_certificato.data_scadenza_calcolata else None,
        stato_certificato=stato
    )

@router.put("/certificati/{certificato_id}", response_model=CertificatoSchema)
def update_certificato(certificato_id: int, certificato: CertificatoAggiornamentoSchema, db: Session = Depends(get_db)):
    """
    Aggiorna un certificato esistente.

    Args:
        certificato_id: L'ID del certificato da aggiornare.
        certificato: I dati del certificato da aggiornare.
        db: La sessione del database.

    Returns:
        Il certificato aggiornato.
    """
    db_certificato = db.query(Certificato).filter(Certificato.id == certificato_id).first()
    if not db_certificato:
        raise HTTPException(status_code=404, detail="Certificato non trovato")

    # Handle name and course changes
    try:
        nome_parts = certificato.nome.split()
        # Try Lastname Firstname
        db_dipendente = db.query(Dipendente).filter(Dipendente.nome == nome_parts[1], Dipendente.cognome == nome_parts[0]).first()
        # Try Firstname Lastname
        if not db_dipendente:
            db_dipendente = db.query(Dipendente).filter(Dipendente.nome == nome_parts[0], Dipendente.cognome == nome_parts[1]).first()

        if not db_dipendente:
            print(f"Dipendente '{certificato.nome}' non trovato, lo creo...")
            db_dipendente = Dipendente(
                nome=nome_parts[0],
                cognome=nome_parts[1]
            )
            db.add(db_dipendente)
            db.flush()
        db_certificato.dipendente_id = db_dipendente.id
    except IndexError:
        raise HTTPException(status_code=400, detail="Formato nome non valido. Inserire nome e cognome.")

    db_master_course = db.query(Corso).filter(Corso.categoria_corso.ilike(f"%{certificato.categoria}%")).first()
    if not db_master_course:
        raise HTTPException(status_code=404, detail=f"Categoria '{certificato.categoria}' non trovata.")

    db_corso = db.query(Corso).filter(Corso.nome_corso.ilike(f"%{certificato.corso}%")).first()
    if not db_corso:
        db_corso = Corso(
            nome_corso=certificato.corso,
            validita_mesi=db_master_course.validita_mesi,
            categoria_corso=db_master_course.categoria_corso
        )
        db.add(db_corso)
        db.flush()
    db_certificato.corso_id = db_corso.id

    db_certificato.data_rilascio = datetime.strptime(certificato.data_rilascio, '%d/%m/%Y').date()
    db_certificato.data_scadenza_calcolata = (
        datetime.strptime(certificato.data_scadenza, '%d/%m/%Y').date()
        if certificato.data_scadenza
        else None
    )

    db_certificato.stato_validazione = ValidationStatus.MANUAL
    try:
        db.commit()
        db.refresh(db_certificato)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Errore di integrità durante l'aggiornamento.")

    stato = certificate_logic.get_certificate_status(db_certificato.data_scadenza_calcolata)
    return CertificatoSchema(
        id=db_certificato.id,
        dipendente=f"{db_certificato.dipendente.nome} {db_certificato.dipendente.cognome}",
        corso=db_certificato.corso.nome_corso,
        categoria=db_certificato.corso.categoria_corso or "General",
        data_rilascio=db_certificato.data_rilascio.strftime('%d/%m/%Y'),
        data_scadenza=db_certificato.data_scadenza_calcolata.strftime('%d/%m/%Y') if db_certificato.data_scadenza_calcolata else None,
        stato_certificato=stato
    )


@router.put("/certificati/{certificato_id}/valida", response_model=CertificatoSchema)
def valida_certificato(certificato_id: int, db: Session = Depends(get_db)):
    """
    Imposta lo stato di validazione di un certificato su 'MANUAL'.
    Args:
        certificato_id: L'ID del certificato da validare.
        db: La sessione del database.
    Returns:
        Il certificato aggiornato.
    """
    db_certificato = db.query(Certificato).filter(Certificato.id == certificato_id).first()
    if not db_certificato:
        raise HTTPException(status_code=404, detail="Certificato non trovato")

    db_certificato.stato_validazione = ValidationStatus.MANUAL
    db.commit()
    db.refresh(db_certificato)

    stato = certificate_logic.get_certificate_status(db_certificato.data_scadenza_calcolata)
    return CertificatoSchema(
        id=db_certificato.id,
        dipendente=f"{db_certificato.dipendente.nome} {db_certificato.dipendente.cognome}",
        corso=db_certificato.corso.nome_corso,
        categoria=db_certificato.corso.categoria_corso or "General",
        data_rilascio=db_certificato.data_rilascio.strftime('%d/%m/%Y'),
        data_scadenza=db_certificato.data_scadenza_calcolata.strftime('%d/%m/%Y') if db_certificato.data_scadenza_calcolata else None,
        stato_certificato=stato
    )

@router.delete("/certificati/{certificato_id}")
def delete_certificato(certificato_id: int, db: Session = Depends(get_db)):
    """
    Elimina un certificato dal database.

    Args:
        certificato_id: L'ID del certificato da eliminare.
        db: La sessione del database.

    Returns:
        Un messaggio di conferma.
    """
    db_certificato = db.query(Certificato).filter(Certificato.id == certificato_id).first()
    if not db_certificato:
        raise HTTPException(status_code=404, detail="Certificato non trovato")
    db.delete(db_certificato)
    db.commit()
    return {"message": "Certificato cancellato con successo"}
