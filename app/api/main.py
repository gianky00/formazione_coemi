import csv
import io
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from app.db.session import get_db
from app.db.models import Corso, Certificato, ValidationStatus, Dipendente
from app.services import ai_extraction, certificate_logic
from datetime import datetime
from typing import Optional, List
from app.schemas.schemas import CertificatoSchema, CertificatoCreazioneSchema, CertificatoAggiornamentoSchema, DipendenteSchema

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
        if not cert.corso:
            continue

        ragione_fallimento = None
        if cert.dipendente:
            nome_completo = f"{cert.dipendente.cognome} {cert.dipendente.nome}"
            data_nascita = cert.dipendente.data_nascita.strftime('%d/%m/%Y') if cert.dipendente.data_nascita else None
            matricola = cert.dipendente.matricola
        else:
            nome_completo = cert.nome_dipendente_raw or "DA ASSEGNARE"
            data_nascita = cert.data_nascita_raw
            matricola = None
            ragione_fallimento = "Dipendente non trovato in anagrafica (matricola mancante)."

        status = certificate_logic.get_certificate_status(db, cert)
        result.append(CertificatoSchema(
            id=cert.id,
            nome=nome_completo,
            data_nascita=data_nascita,
            matricola=matricola,
            corso=cert.corso.nome_corso,
            categoria=cert.corso.categoria_corso or "General",
            data_rilascio=cert.data_rilascio.strftime('%d/%m/%Y'),
            data_scadenza=cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else None,
            stato_certificato=status,
            assegnazione_fallita_ragione=ragione_fallimento
        ))
    return result

@router.get("/certificati/{certificato_id}", response_model=CertificatoSchema)
def get_certificato(certificato_id: int, db: Session = Depends(get_db)):
    db_cert = db.get(Certificato, certificato_id)
    if not db_cert:
        raise HTTPException(status_code=404, detail="Certificato non trovato")

    status = certificate_logic.get_certificate_status(db, db_cert)

    if db_cert.dipendente:
        nome_completo = f"{db_cert.dipendente.cognome} {db_cert.dipendente.nome}"
        data_nascita = db_cert.dipendente.data_nascita.strftime('%d/%m/%Y') if db_cert.dipendente.data_nascita else None
        matricola = db_cert.dipendente.matricola
    else:
        nome_completo = db_cert.nome_dipendente_raw or "DA ASSEGNARE"
        data_nascita = db_cert.data_nascita_raw
        matricola = None

    return CertificatoSchema(
        id=db_cert.id,
        nome=nome_completo,
        data_nascita=data_nascita,
        matricola=matricola,
        corso=db_cert.corso.nome_corso,
        categoria=db_cert.corso.categoria_corso or "General",
        data_rilascio=db_cert.data_rilascio.strftime('%d/%m/%Y'),
        data_scadenza=db_cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if db_cert.data_scadenza_calcolata else None,
        stato_certificato=status
    )

@router.post("/certificati/", response_model=CertificatoSchema)
def create_certificato(certificato: CertificatoCreazioneSchema, db: Session = Depends(get_db)):
    if not certificato.data_rilascio:
        raise HTTPException(status_code=422, detail="La data di rilascio non può essere vuota.")

    if not certificato.nome or not certificato.nome.strip():
        raise HTTPException(status_code=400, detail="Il nome non può essere vuoto.")

    nome_parts = certificato.nome.strip().split()
    if len(nome_parts) < 2:
        raise HTTPException(status_code=400, detail="Formato nome non valido. Inserire nome e cognome.")

    nome, cognome = nome_parts[0], " ".join(nome_parts[1:])

    # Cerca una corrispondenza esatta nei dati anagrafici
    dipendente_trovato = None
    query = db.query(Dipendente).filter(
        or_(
            (Dipendente.nome.ilike(nome)) & (Dipendente.cognome.ilike(cognome)),
            (Dipendente.nome.ilike(cognome)) & (Dipendente.cognome.ilike(nome))
        )
    )

    dipendenti = query.all()
    if len(dipendenti) == 1:
        dipendente_trovato = dipendenti[0]

    dipendente_id = dipendente_trovato.id if dipendente_trovato else None

    master_course = db.query(Corso).filter(Corso.categoria_corso.ilike(f"%{certificato.categoria.strip()}%")).first()
    if not master_course:
        master_course = Corso(
            nome_corso=certificato.categoria.strip().upper(),
            validita_mesi=60,  # Default validity
            categoria_corso=certificato.categoria.strip().upper()
        )
        db.add(master_course)
        db.flush()

    course = db.query(Corso).filter(
        Corso.nome_corso.ilike(f"%{certificato.corso}%"),
        Corso.categoria_corso.ilike(f"%{certificato.categoria}%")
    ).first()
    if not course:
        course = Corso(
            nome_corso=certificato.corso,
            validita_mesi=master_course.validita_mesi,
            categoria_corso=master_course.categoria_corso
        )
        db.add(course)
        db.flush()

    # Controllo duplicati
    existing_cert_query = db.query(Certificato).filter(
        Certificato.corso_id == course.id,
        Certificato.data_rilascio == datetime.strptime(certificato.data_rilascio, '%d/%m/%Y').date()
    )

    if dipendente_id:
        existing_cert_query = existing_cert_query.filter(Certificato.dipendente_id == dipendente_id)
    else:
        # Per gli orfani, controlla anche il nome raw per evitare duplicati per la stessa persona non mappata
        existing_cert_query = existing_cert_query.filter(
            Certificato.dipendente_id.is_(None),
            Certificato.nome_dipendente_raw.ilike(f"%{certificato.nome.strip()}%")
        )

    if existing_cert_query.first():
        raise HTTPException(status_code=409, detail="Un certificato identico per questo dipendente e corso esiste già.")

    new_cert = Certificato(
        dipendente_id=dipendente_id,
        nome_dipendente_raw=certificato.nome.strip(),
        data_nascita_raw=certificato.data_nascita,
        corso_id=course.id,
        data_rilascio=datetime.strptime(certificato.data_rilascio, '%d/%m/%Y').date(),
        data_scadenza_calcolata=datetime.strptime(certificato.data_scadenza, '%d/%m/%Y').date() if certificato.data_scadenza else None,
        stato_validazione=ValidationStatus.AUTOMATIC
    )
    db.add(new_cert)
    db.commit()
    db.refresh(new_cert)

    status = certificate_logic.get_certificate_status(db, new_cert)

    dipendente_info = db.get(Dipendente, new_cert.dipendente_id) if new_cert.dipendente_id else None
    ragione_fallimento = None
    if not dipendente_info:
        ragione_fallimento = "Dipendente non trovato in anagrafica (matricola mancante)."

    return CertificatoSchema(
        id=new_cert.id,
        nome=f"{dipendente_info.cognome} {dipendente_info.nome}" if dipendente_info else new_cert.nome_dipendente_raw or "Da Assegnare",
        data_nascita=dipendente_info.data_nascita.strftime('%d/%m/%Y') if dipendente_info and dipendente_info.data_nascita else new_cert.data_nascita_raw,
        matricola=dipendente_info.matricola if dipendente_info else None,
        corso=new_cert.corso.nome_corso,
        categoria=new_cert.corso.categoria_corso or "General",
        data_rilascio=new_cert.data_rilascio.strftime('%d/%m/%Y'),
        data_scadenza=new_cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if new_cert.data_scadenza_calcolata else None,
        stato_certificato=status,
        assegnazione_fallita_ragione=ragione_fallimento
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

    if db_cert.dipendente:
        nome_completo = f"{db_cert.dipendente.cognome} {db_cert.dipendente.nome}"
        data_nascita = db_cert.dipendente.data_nascita.strftime('%d/%m/%Y') if db_cert.dipendente.data_nascita else None
        matricola = db_cert.dipendente.matricola
    else:
        nome_completo = db_cert.nome_dipendente_raw or "DA ASSEGNARE"
        data_nascita = db_cert.data_nascita_raw
        matricola = None

    return CertificatoSchema(
        id=db_cert.id,
        nome=nome_completo,
        data_nascita=data_nascita,
        matricola=matricola,
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

    update_data = certificato.model_dump(exclude_unset=True)

    if 'nome' in update_data:
        if not update_data['nome'] or not update_data['nome'].strip():
            raise HTTPException(status_code=400, detail="Il nome non può essere vuoto.")
        nome_parts = update_data['nome'].strip().split()
        if len(nome_parts) < 2:
            raise HTTPException(status_code=400, detail="Formato nome non valido. Inserire nome e cognome.")

        nome, cognome = nome_parts[0], " ".join(nome_parts[1:])

        # Logica di matching robusta
        query = db.query(Dipendente).filter(
            or_(
                (Dipendente.nome.ilike(nome)) & (Dipendente.cognome.ilike(cognome)),
                (Dipendente.nome.ilike(cognome)) & (Dipendente.cognome.ilike(nome))
            )
        )
        dipendenti = query.all()

        if len(dipendenti) == 1:
            db_cert.dipendente_id = dipendenti[0].id
        else:
            # Se non trovato o ambiguo, disassocia o gestisci come errore
            db_cert.dipendente_id = None

    if 'categoria' in update_data or 'corso' in update_data:
        categoria = update_data.get('categoria', db_cert.corso.categoria_corso)
        master_course = db.query(Corso).filter(Corso.categoria_corso.ilike(f"%{categoria}%")).first()
        if not master_course:
            raise HTTPException(status_code=404, detail=f"Categoria '{categoria}' non trovata.")

        corso_nome = update_data.get('corso', db_cert.corso.nome_corso)
        course = db.query(Corso).filter(
            Corso.nome_corso.ilike(f"%{corso_nome}%"),
            Corso.categoria_corso.ilike(f"%{categoria}%")
        ).first()
        if not course:
            course = Corso(
                nome_corso=corso_nome,
                validita_mesi=master_course.validita_mesi,
                categoria_corso=master_course.categoria_corso
            )
            db.add(course)
            db.flush()
        db_cert.corso_id = course.id

    if 'data_rilascio' in update_data:
        db_cert.data_rilascio = datetime.strptime(update_data['data_rilascio'], '%d/%m/%Y').date()

    if 'data_scadenza' in update_data:
        scadenza = update_data['data_scadenza']
        db_cert.data_scadenza_calcolata = datetime.strptime(scadenza, '%d/%m/%Y').date() if scadenza and scadenza.strip() and scadenza.lower() != 'none' else None

    db_cert.stato_validazione = ValidationStatus.MANUAL
    db.commit()
    db.refresh(db_cert)
    status = certificate_logic.get_certificate_status(db, db_cert)

    dipendente_info = db_cert.dipendente  # Reload the relationship

    return CertificatoSchema(
        id=db_cert.id,
        nome=f"{dipendente_info.cognome} {dipendente_info.nome}" if dipendente_info else "Da Assegnare",
        data_nascita=dipendente_info.data_nascita.strftime('%d/%m/%Y') if dipendente_info and dipendente_info.data_nascita else None,
        matricola=dipendente_info.matricola if dipendente_info else None,
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

@router.post("/dipendenti/import-csv")
async def import_dipendenti_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Il file deve essere in formato CSV.")

    content = await file.read()
    stream = io.StringIO(content.decode("utf-8"))
    reader = csv.DictReader(stream, delimiter=';')

    for row in reader:
        cognome = row.get('Cognome')
        nome = row.get('Nome')
        data_nascita = row.get('Data_nascita')
        badge = row.get('Badge')

        if not all([cognome, nome, badge]):
            continue

        parsed_data_nascita = None
        if data_nascita:
            try:
                parsed_data_nascita = datetime.strptime(data_nascita, '%d/%m/%Y').date()
            except ValueError:
                pass  # Gestisce date non valide o formati diversi

        # Upsert: aggiorna se esiste, altrimenti crea
        dipendente = db.query(Dipendente).filter(Dipendente.matricola == badge).first()
        if dipendente:
            dipendente.cognome = cognome
            dipendente.nome = nome
            dipendente.data_nascita = parsed_data_nascita
        else:
            dipendente = Dipendente(
                cognome=cognome,
                nome=nome,
                matricola=badge,
                data_nascita=parsed_data_nascita
            )
            db.add(dipendente)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Errore di integrità del database. Controlla i dati del CSV.")

    return {"message": "Importazione completata con successo."}

@router.get("/dipendenti", response_model=List[DipendenteSchema])
def get_dipendenti(db: Session = Depends(get_db)):
    return db.query(Dipendente).all()
