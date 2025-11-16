from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from app.db.session import get_db
from app.db.models import Corso, Certificato, ValidationStatus, Dipendente
from app.services import ai_extraction, certificate_logic
from datetime import datetime
from typing import Optional, List
from app.schemas.schemas import CertificatoSchema, CertificatoCreazioneSchema, CertificatoAggiornamentoSchema

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Welcome to the Scadenziario IA API"}

@router.get("/corsi")
def get_corsi(db: Session = Depends(get_db)):
    return db.query(Corso).all()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    pdf_bytes = await file.read()
    extracted_data = ai_extraction.extract_entities_with_ai(pdf_bytes)
    if "error" in extracted_data:
        raise HTTPException(status_code=500, detail=extracted_data["error"])

    if extracted_data.get("data_scadenza"):
        extracted_data["data_scadenza"] = extracted_data["data_scadenza"].replace("-", "/")

    if not extracted_data.get("data_scadenza") and extracted_data.get("data_rilascio"):
        try:
            issue_date = datetime.strptime(extracted_data["data_rilascio"], '%d-%m-%Y').date()
            category = extracted_data.get("categoria")
            course = db.query(Corso).filter(Corso.categoria_corso.ilike(f"%{category}%")).first()
            if course:
                expiration_date = certificate_logic.calculate_expiration_date(issue_date, course.validita_mesi)
                if expiration_date:
                    extracted_data["data_scadenza"] = expiration_date.strftime('%d/%m/%Y')
        except (ValueError, TypeError):
            pass

    return {"filename": file.filename, "entities": extracted_data}

@router.get("/certificati/", response_model=List[CertificatoSchema])
def get_certificati(validated: Optional[bool] = Query(None), db: Session = Depends(get_db)):
    query = db.query(Certificato).options(selectinload(Certificato.dipendente), selectinload(Certificato.corso))
    if validated is not None:
        query = query.filter(Certificato.stato_validazione == (ValidationStatus.MANUAL if validated else ValidationStatus.AUTOMATIC))

    certificati = query.all()
    result = []
    for cert in certificati:
        if not cert.dipendente or not cert.corso:
            continue

        status = certificate_logic.get_certificate_status(db, cert)
        result.append(CertificatoSchema(
            id=cert.id,
            nome=f"{cert.dipendente.nome} {cert.dipendente.cognome}",
            corso=cert.corso.nome_corso,
            categoria=cert.corso.categoria_corso or "General",
            data_rilascio=cert.data_rilascio.strftime('%d/%m/%Y'),
            data_scadenza=cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else None,
            stato_certificato=status
        ))
    return result

@router.post("/certificati/", response_model=CertificatoSchema)
def create_certificato(certificato: CertificatoCreazioneSchema, db: Session = Depends(get_db)):
    if not certificato.data_rilascio:
        raise HTTPException(status_code=422, detail="La data di rilascio non può essere vuota.")

    nome_parts = certificato.nome.strip().split()
    if len(nome_parts) < 2:
        raise HTTPException(status_code=400, detail="Formato nome non valido. Inserire nome e cognome.")

    nome, cognome = nome_parts[0], " ".join(nome_parts[1:])
    dipendente = db.query(Dipendente).filter(Dipendente.nome.ilike(f"%{nome}%"), Dipendente.cognome.ilike(f"%{cognome}%")).first()

    if not dipendente:
        dipendente = Dipendente(nome=nome, cognome=cognome)
        db.add(dipendente)
        db.flush()

    master_course = db.query(Corso).filter(Corso.categoria_corso.ilike(f"%{certificato.categoria.strip()}%")).first()
    if not master_course:
        raise HTTPException(status_code=404, detail=f"Categoria '{certificato.categoria}' non trovata.")

    course = db.query(Corso).filter(Corso.nome_corso.ilike(f"%{certificato.corso}%")).first()
    if not course:
        course = Corso(
            nome_corso=certificato.corso,
            validita_mesi=master_course.validita_mesi,
            categoria_corso=master_course.categoria_corso
        )
        db.add(course)
        db.flush()

    existing_cert = db.query(Certificato).filter_by(
        dipendente_id=dipendente.id,
        corso_id=course.id,
        data_rilascio=datetime.strptime(certificato.data_rilascio, '%d/%m/%Y').date()
    ).first()
    if existing_cert:
        raise HTTPException(status_code=409, detail="Un certificato identico per questo dipendente e corso esiste già.")

    new_cert = Certificato(
        dipendente_id=dipendente.id,
        corso_id=course.id,
        data_rilascio=datetime.strptime(certificato.data_rilascio, '%d/%m/%Y').date(),
        data_scadenza_calcolata=datetime.strptime(certificato.data_scadenza, '%d/%m/%Y').date() if certificato.data_scadenza else None,
        stato_validazione=ValidationStatus.AUTOMATIC
    )
    db.add(new_cert)
    db.commit()
    db.refresh(new_cert)

    status = certificate_logic.get_certificate_status(db, new_cert)
    return CertificatoSchema(
        id=new_cert.id,
        nome=f"{new_cert.dipendente.nome} {new_cert.dipendente.cognome}",
        corso=new_cert.corso.nome_corso,
        categoria=new_cert.corso.categoria_corso or "General",
        data_rilascio=new_cert.data_rilascio.strftime('%d/%m/%Y'),
        data_scadenza=new_cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if new_cert.data_scadenza_calcolata else None,
        stato_certificato=status
    )

@router.put("/certificati/{certificato_id}/valida", response_model=CertificatoSchema)
def valida_certificato(certificato_id: int, db: Session = Depends(get_db)):
    db_cert = db.get(Certificato, certificato_id)
    if not db_cert:
        raise HTTPException(status_code=404, detail="Certificato non trovato")
    db_cert.stato_validazione = ValidationStatus.MANUAL
    db.commit()
    db.refresh(db_cert)
    status = certificate_logic.get_certificate_status(db, db_cert)
    return CertificatoSchema(
        id=db_cert.id,
        nome=f"{db_cert.dipendente.nome} {db_cert.dipendente.cognome}",
        corso=db_cert.corso.nome_corso,
        categoria=db_cert.corso.categoria_corso or "General",
        data_rilascio=db_cert.data_rilascio.strftime('%d/%m/%Y'),
        data_scadenza=db_cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if db_cert.data_scadenza_calcolata else None,
        stato_certificato=status
    )

@router.put("/certificati/{certificato_id}", response_model=CertificatoSchema)
def update_certificato(certificato_id: int, certificato: CertificatoAggiornamentoSchema, db: Session = Depends(get_db)):
    db_cert = db.get(Certificato, certificato_id)
    if not db_cert:
        raise HTTPException(status_code=404, detail="Certificato non trovato")

    nome_parts = certificato.nome.split()
    if len(nome_parts) < 2:
        raise HTTPException(status_code=400, detail="Formato nome non valido. Inserire nome e cognome.")

    dipendente = db.query(Dipendente).filter_by(nome=nome_parts[0], cognome=" ".join(nome_parts[1:])).first()
    if not dipendente:
        dipendente = Dipendente(nome=nome_parts[0], cognome=" ".join(nome_parts[1:]))
        db.add(dipendente)
        db.flush()
    db_cert.dipendente_id = dipendente.id

    master_course = db.query(Corso).filter(Corso.categoria_corso.ilike(f"%{certificato.categoria}%")).first()
    if not master_course:
        raise HTTPException(status_code=404, detail=f"Categoria '{certificato.categoria}' non trovata.")

    course = db.query(Corso).filter(Corso.nome_corso.ilike(f"%{certificato.corso}%")).first()
    if not course:
        course = Corso(
            nome_corso=certificato.corso,
            validita_mesi=master_course.validita_mesi,
            categoria_corso=master_course.categoria_corso
        )
        db.add(course)
        db.flush()
    db_cert.corso_id = course.id

    db_cert.data_rilascio = datetime.strptime(certificato.data_rilascio, '%d/%m/%Y').date()
    db_cert.data_scadenza_calcolata = datetime.strptime(certificato.data_scadenza, '%d/%m/%Y').date() if certificato.data_scadenza and certificato.data_scadenza.strip() and certificato.data_scadenza.lower() != 'none' else None
    db_cert.stato_validazione = ValidationStatus.MANUAL

    db.commit()
    db.refresh(db_cert)
    status = certificate_logic.get_certificate_status(db, db_cert)
    return CertificatoSchema(
        id=db_cert.id,
        nome=f"{db_cert.dipendente.nome} {db_cert.dipendente.cognome}",
        corso=db_cert.corso.nome_corso,
        categoria=db_cert.corso.categoria_corso or "General",
        data_rilascio=db_cert.data_rilascio.strftime('%d/%m/%Y'),
        data_scadenza=db_cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if db_cert.data_scadenza_calcolata else None,
        stato_certificato=status
    )

@router.delete("/certificati/{certificato_id}")
def delete_certificato(certificato_id: int, db: Session = Depends(get_db)):
    db_cert = db.get(Certificato, certificato_id)
    if not db_cert:
        raise HTTPException(status_code=404, detail="Certificato non trovato")
    db.delete(db_cert)
    db.commit()
    return {"message": "Certificato cancellato con successo"}
