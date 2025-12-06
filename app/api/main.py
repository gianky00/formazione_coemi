import csv
import io
import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from app.db.session import get_db
from app.db.models import Corso, Certificato, ValidationStatus, Dipendente, User as UserModel
from app.services import ai_extraction, certificate_logic, matcher
from app.services.document_locator import find_document, construct_certificate_path
from app.services.sync_service import archive_certificate_file, link_orphaned_certificates, get_unique_filename
from app.core.config import settings, get_user_data_dir
from app.utils.date_parser import parse_date_flexible
from app.utils.file_security import verify_file_signature
from app.utils.audit import log_security_action
from app.api import deps
from datetime import datetime
from typing import Optional, List
import charset_normalizer
from app.schemas.schemas import (
    CertificatoSchema,
    CertificatoCreazioneSchema,
    CertificatoAggiornamentoSchema,
    DipendenteSchema,
    DipendenteCreateSchema,
    DipendenteUpdateSchema,
    DipendenteDetailSchema
)

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Welcome to the Scadenziario IA API"}

@router.get("/corsi")
def get_corsi(db: Session = Depends(get_db), license: bool = Depends(deps.verify_license)):
    return db.query(Corso).all()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/upload-pdf/", dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE

    # Read file with size limit check
    pdf_bytes = bytearray()
    while True:
        chunk = await file.read(1024 * 1024)  # Read 1MB chunks
        if not chunk:
            break
        pdf_bytes.extend(chunk)
        if len(pdf_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"Il file supera il limite massimo di {MAX_FILE_SIZE // (1024*1024)}MB.")

    if not verify_file_signature(bytes(pdf_bytes), 'pdf'):
         raise HTTPException(status_code=400, detail="File non valido: firma digitale PDF non riconosciuta.")

    extracted_data = ai_extraction.extract_entities_with_ai(bytes(pdf_bytes))
    if "error" in extracted_data:
        if extracted_data.get("is_rejected"):
             log_security_action(db, current_user, "AI_REJECT", f"File rejected by AI: {file.filename}. Reason: {extracted_data['error']}", category="AI_ANALYSIS", severity="MEDIUM")
             raise HTTPException(status_code=422, detail=extracted_data["error"])
        if extracted_data.get("status_code") == 429:
            raise HTTPException(status_code=429, detail=extracted_data["error"])
        raise HTTPException(status_code=500, detail=extracted_data["error"])

    # Flexible Date Parsing and Correction
    for date_field in ["data_scadenza", "data_rilascio", "data_nascita"]:
        if extracted_data.get(date_field):
            parsed_date = parse_date_flexible(extracted_data[date_field])
            if parsed_date:
                extracted_data[date_field] = parsed_date.strftime('%d/%m/%Y')
            # If parsing fails, we leave it as is (or could set to None/warn)

    # Logic to calculate expiration if missing
    if not extracted_data.get("data_scadenza") and extracted_data.get("data_rilascio"):
        try:
            issue_date = datetime.strptime(extracted_data["data_rilascio"], '%d/%m/%Y').date()
            category = extracted_data.get("categoria")
            course = db.query(Corso).filter(Corso.categoria_corso.ilike(f"%{category}%")).first()
            if course:
                expiration_date = certificate_logic.calculate_expiration_date(issue_date, course.validita_mesi)
                if expiration_date:
                    extracted_data["data_scadenza"] = expiration_date.strftime('%d/%m/%Y')
        except (ValueError, TypeError):
            pass

    return {"filename": file.filename, "entities": extracted_data}

@router.get("/certificati/", response_model=List[CertificatoSchema], dependencies=[Depends(deps.verify_license)])
def get_certificati(validated: Optional[bool] = Query(None), db: Session = Depends(get_db)):
    query = db.query(Certificato).options(selectinload(Certificato.dipendente), selectinload(Certificato.corso))
    if validated is not None:
        query = query.filter(Certificato.stato_validazione == (ValidationStatus.MANUAL if validated else ValidationStatus.AUTOMATIC))

    certificati = query.all()

    # Optimize: Calculate statuses in bulk to avoid N+1 queries
    status_map = certificate_logic.get_bulk_certificate_statuses(db, certificati)

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
            ragione_fallimento = "Non trovato in anagrafica (matricola mancante)."

        status = status_map.get(cert.id, "attivo")
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

@router.get("/certificati/{certificato_id}", response_model=CertificatoSchema, dependencies=[Depends(deps.verify_license)])
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

@router.post("/certificati/", response_model=CertificatoSchema, dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
def create_certificato(
    certificato: CertificatoCreazioneSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    if not certificato.data_rilascio:
        raise HTTPException(status_code=422, detail="La data di rilascio non può essere vuota.")

    if not certificato.nome or not certificato.nome.strip():
        raise HTTPException(status_code=400, detail="Il nome non può essere vuoto.")

    nome_parts = certificato.nome.strip().split()
    if len(nome_parts) < 2:
        raise HTTPException(status_code=400, detail="Formato nome non valido. Inserire nome e cognome.")

    # Cerca una corrispondenza esatta nei dati anagrafici
    dob = parse_date_flexible(certificato.data_nascita) if certificato.data_nascita else None
    dipendente_trovato = matcher.find_employee_by_name(db, certificato.nome, dob)
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
        # Bug 7 Fix: Reverted to AUTOMATIC to ensure proper validation workflow and orphans visibility
        stato_validazione=ValidationStatus.AUTOMATIC
    )
    db.add(new_cert)
    try:
        db.commit()
        db.refresh(new_cert)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Un certificato identico per questo dipendente e corso esiste già.")

    status = certificate_logic.get_certificate_status(db, new_cert)

    dipendente_info = db.get(Dipendente, new_cert.dipendente_id) if new_cert.dipendente_id else None
    ragione_fallimento = None
    if not dipendente_info:
        ragione_fallimento = "Non trovato in anagrafica (matricola mancante)."

    matricola_log = dipendente_info.matricola if dipendente_info else "N/A"
    scadenza_log = certificato.data_scadenza if certificato.data_scadenza else "nessuna scadenza"
    log_msg = f"creato certificato per {certificato.nome.upper()} ({matricola_log}) - {certificato.categoria.upper()} - {scadenza_log} (data scadenza)"
    # Real-time Archiving: Check if this new certificate obsoletes older ones
    try:
        older_certs = db.query(Certificato).join(Corso).filter(
            Certificato.dipendente_id == new_cert.dipendente_id,
            Corso.categoria_corso == new_cert.corso.categoria_corso,
            Certificato.id != new_cert.id,
            Certificato.data_rilascio < new_cert.data_rilascio
        ).all()

        for old_cert in older_certs:
            # Check if it is now archiviato
            if certificate_logic.get_certificate_status(db, old_cert) == "archiviato":
                archive_certificate_file(db, old_cert)
    except Exception as e:
        print(f"Error archiving older certificates: {e}")

    log_security_action(db, current_user, "CERTIFICATE_CREATE", log_msg, category="CERTIFICATE")

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

@router.put("/certificati/{certificato_id}/valida", response_model=CertificatoSchema, dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
def valida_certificato(
    certificato_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    db_cert = db.get(Certificato, certificato_id)
    if not db_cert:
        raise HTTPException(status_code=404, detail="Certificato non trovato")
    db_cert.stato_validazione = ValidationStatus.MANUAL
    db.commit()
    db.refresh(db_cert)
    status = certificate_logic.get_certificate_status(db, db_cert)

    empl_name = (f"{db_cert.dipendente.cognome} {db_cert.dipendente.nome}" if db_cert.dipendente else db_cert.nome_dipendente_raw) or "Sconosciuto"
    course_name = db_cert.corso.nome_corso
    log_msg = f"validato certificato per {empl_name} - {course_name} (ID: {certificato_id})"

    log_security_action(db, current_user, "CERTIFICATE_VALIDATE", log_msg, category="CERTIFICATE")

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

@router.put("/certificati/{certificato_id}", response_model=CertificatoSchema, dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
def update_certificato(
    certificato_id: int,
    certificato: CertificatoAggiornamentoSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    db_cert = db.get(Certificato, certificato_id)
    if not db_cert:
        raise HTTPException(status_code=404, detail="Certificato non trovato")

    # Capture old state for file renaming
    old_cert_data = {
        'nome': f"{db_cert.dipendente.cognome} {db_cert.dipendente.nome}" if db_cert.dipendente else db_cert.nome_dipendente_raw,
        'matricola': db_cert.dipendente.matricola if db_cert.dipendente else None,
        'categoria': db_cert.corso.categoria_corso if db_cert.corso else None,
        'data_scadenza': db_cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if db_cert.data_scadenza_calcolata else None
    }

    update_data = certificato.model_dump(exclude_unset=True)

    if 'data_nascita' in update_data:
        db_cert.data_nascita_raw = update_data['data_nascita']

    if 'nome' in update_data or 'data_nascita' in update_data:
        if 'nome' in update_data:
            if not update_data['nome'] or not update_data['nome'].strip():
                raise HTTPException(status_code=400, detail="Il nome non può essere vuoto.")

            db_cert.nome_dipendente_raw = update_data['nome'].strip()

            nome_parts = update_data['nome'].strip().split()
            if len(nome_parts) < 2:
                raise HTTPException(status_code=400, detail="Formato nome non valido. Inserire nome e cognome.")

        search_name = db_cert.nome_dipendente_raw
        dob_str = db_cert.data_nascita_raw
        dob = parse_date_flexible(dob_str) if dob_str else None

        # Logica di matching robusta
        if search_name:
            match = matcher.find_employee_by_name(db, search_name, dob)

            if match:
                db_cert.dipendente_id = match.id
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

    # Check constraints before file move
    try:
        db.flush()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Errore di integrità: {e}")

    # File Synchronization: Rename/Move file if data changed
    file_moved = False
    old_file_path = None
    new_file_path = None

    try:
        # We construct new data from db_cert.
        # Ensure relations are loaded.
        if not db_cert.dipendente and db_cert.dipendente_id:
             db_cert.dipendente = db.get(Dipendente, db_cert.dipendente_id)
        if not db_cert.corso:
             db_cert.corso = db.query(Corso).get(db_cert.corso_id)

        new_cert_data = {
            'nome': f"{db_cert.dipendente.cognome} {db_cert.dipendente.nome}" if db_cert.dipendente else db_cert.nome_dipendente_raw,
            'matricola': db_cert.dipendente.matricola if db_cert.dipendente else None,
            'categoria': db_cert.corso.categoria_corso if db_cert.corso else None,
            'data_scadenza': db_cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if db_cert.data_scadenza_calcolata else None
        }

        status = certificate_logic.get_certificate_status(db, db_cert)

        if old_cert_data != new_cert_data:
            database_path = settings.DATABASE_PATH or str(get_user_data_dir())
            if database_path:
                old_file_path = find_document(database_path, old_cert_data)

                if old_file_path and os.path.exists(old_file_path):
                    # Determine target status folder
                    if status in ["attivo", "in_scadenza"]:
                        target_status = "ATTIVO"
                    else:
                        target_status = "STORICO"

                    new_file_path = construct_certificate_path(database_path, new_cert_data, status=target_status)

                    if old_file_path != new_file_path:
                        # Bug 5 Fix: Prevent Overwrite
                        dest_dir = os.path.dirname(new_file_path)
                        os.makedirs(dest_dir, exist_ok=True)

                        filename = os.path.basename(new_file_path)
                        unique_filename = get_unique_filename(dest_dir, filename)
                        new_file_path = os.path.join(dest_dir, unique_filename)

                        shutil.move(old_file_path, new_file_path)
                        file_moved = True
    except PermissionError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Impossibile spostare il file: File in uso o permessi negati.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore durante la sincronizzazione del file: {e}")

    # Commit Transaction
    try:
        db.commit()
        db.refresh(db_cert)
    except Exception as e:
        db.rollback()
        # Rollback File Move if needed
        if file_moved and old_file_path and new_file_path:
            try:
                shutil.move(new_file_path, old_file_path)
            except Exception as rollback_err:
                print(f"CRITICAL: Failed to rollback file move for cert {certificato_id}: {rollback_err}")
        raise HTTPException(status_code=500, detail=f"Errore durante il salvataggio nel database: {e}")

    log_security_action(db, current_user, "CERTIFICATE_UPDATE", f"aggiornato certificato ID {certificato_id}. Campi: {', '.join(update_data.keys())}", category="CERTIFICATE")

    dipendente_info = db_cert.dipendente  # Reload the relationship

    return CertificatoSchema(
        id=db_cert.id,
        nome=f"{dipendente_info.cognome} {dipendente_info.nome}" if dipendente_info else db_cert.nome_dipendente_raw or "Da Assegnare",
        data_nascita=dipendente_info.data_nascita.strftime('%d/%m/%Y') if dipendente_info and dipendente_info.data_nascita else None,
        matricola=dipendente_info.matricola if dipendente_info else None,
        corso=db_cert.corso.nome_corso,
        categoria=db_cert.corso.categoria_corso or "General",
        data_rilascio=db_cert.data_rilascio.strftime('%d/%m/%Y'),
        data_scadenza=db_cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if db_cert.data_scadenza_calcolata else None,
        stato_certificato=status
    )

@router.delete("/certificati/{certificato_id}", dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
def delete_certificato(
    certificato_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    db_cert = db.get(Certificato, certificato_id)
    if not db_cert:
        raise HTTPException(status_code=404, detail="Certificato non trovato")

    # Snapshot for logging
    log_details = f"eliminato certificato ID {certificato_id} - {db_cert.nome_dipendente_raw or 'Sconosciuto'} - {db_cert.corso.nome_corso}"

    # Try to delete the physical file
    try:
        cert_data = {
            'nome': f"{db_cert.dipendente.cognome} {db_cert.dipendente.nome}" if db_cert.dipendente else db_cert.nome_dipendente_raw,
            'matricola': db_cert.dipendente.matricola if db_cert.dipendente else None,
            'categoria': db_cert.corso.categoria_corso if db_cert.corso else None,
            'data_scadenza': db_cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if db_cert.data_scadenza_calcolata else None
        }

        # Only proceed if we have enough info to find the file
        if cert_data['categoria']:
            database_path = settings.DATABASE_PATH or str(get_user_data_dir())
            if database_path:
                file_path = find_document(database_path, cert_data)
                if file_path and os.path.exists(file_path):
                    # Move to Trash (CESTINO) instead of deleting
                    trash_dir = os.path.join(database_path, "DOCUMENTI DIPENDENTI", "CESTINO")
                    os.makedirs(trash_dir, exist_ok=True)

                    filename = os.path.basename(file_path)
                    root, ext = os.path.splitext(filename)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_filename = f"{root}_deleted_{timestamp}{ext}"
                    dest_path = os.path.join(trash_dir, new_filename)

                    shutil.move(file_path, dest_path)
    except Exception as e:
        print(f"Error deleting file for certificate {certificato_id}: {e}")
        # Proceed with DB deletion regardless of file error

    db.delete(db_cert)
    db.commit()

    log_security_action(db, current_user, "CERTIFICATE_DELETE", log_details, category="CERTIFICATE")

    return {"message": "Certificato cancellato con successo"}

@router.post("/dipendenti/import-csv", dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
async def import_dipendenti_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    MAX_CSV_SIZE = settings.MAX_CSV_SIZE

    # Read content with size check
    content_bytes = bytearray()
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        content_bytes.extend(chunk)
        if len(content_bytes) > MAX_CSV_SIZE:
            raise HTTPException(status_code=413, detail=f"Il file CSV supera il limite massimo di {MAX_CSV_SIZE // (1024*1024)}MB.")

    content = bytes(content_bytes)

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Il file deve essere in formato CSV.")

    if not verify_file_signature(content, 'csv'):
         raise HTTPException(status_code=400, detail="File non valido: contenuto non riconosciuto come CSV/Testo.")

    # Strategy: Try UTF-8 -> CP1252 -> Auto-detect -> Latin-1 Fallback
    try:
        decoded_content = content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            # CP1252 is very common in Western Europe/Italy for legacy Excel
            decoded_content = content.decode('cp1252')
        except UnicodeDecodeError:
            # Try auto-detection
            matches = charset_normalizer.from_bytes(content).best()
            encoding = matches.encoding if matches else 'latin-1'
            try:
                decoded_content = content.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                decoded_content = content.decode('latin-1', errors='replace')

    stream = io.StringIO(decoded_content)
    reader = csv.DictReader(stream, delimiter=';')

    warnings = []

    for row in reader:
        cognome = row.get('Cognome')
        nome = row.get('Nome')
        data_nascita = row.get('Data_nascita')
        badge = row.get('Badge')
        data_assunzione = row.get('Data_assunzione')

        if not all([cognome, nome, badge]):
            continue

        parsed_data_nascita = parse_date_flexible(data_nascita) if data_nascita else None
        parsed_data_assunzione = parse_date_flexible(data_assunzione) if data_assunzione else None

        # Step 1: Cerca per Matricola (Upsert standard)
        dipendente = db.query(Dipendente).filter(Dipendente.matricola == badge).first()

        if dipendente:
            # Trovato per matricola -> Aggiorna dati anagrafici
            dipendente.cognome = cognome
            dipendente.nome = nome
            dipendente.data_nascita = parsed_data_nascita
            if parsed_data_assunzione:
                dipendente.data_assunzione = parsed_data_assunzione
        else:
            # Step 2: Matricola non trovata. Cerca per Cognome + Nome + Data Nascita (Gestione Riassunzione/Cambio Matricola)
            found_by_identity = False
            if parsed_data_nascita:
                # Cerca corrispondenza esatta di identità
                matches = db.query(Dipendente).filter(
                    Dipendente.nome.ilike(nome),
                    Dipendente.cognome.ilike(cognome),
                    Dipendente.data_nascita == parsed_data_nascita
                ).all()

                if len(matches) == 1:
                    # Persona trovata univocamente -> Aggiorna la matricola
                    dipendente = matches[0]
                    dipendente.matricola = badge
                    # Aggiorna anche anagrafica per uniformità (es. correzione nome)
                    dipendente.nome = nome
                    dipendente.cognome = cognome
                    if parsed_data_assunzione:
                        dipendente.data_assunzione = parsed_data_assunzione
                    found_by_identity = True
                elif len(matches) > 1:
                    # Duplicati nel DB -> Ambiguo -> Skip e Warning
                    warnings.append(f"Duplicato rilevato per {cognome} {nome} ({data_nascita}). Impossibile assegnare matricola {badge} automaticamente.")
                    continue

            if not found_by_identity:
                # Nessuna corrispondenza o dati insufficienti -> Crea nuovo
                dipendente = Dipendente(
                    cognome=cognome,
                    nome=nome,
                    matricola=badge,
                    data_nascita=parsed_data_nascita,
                    data_assunzione=parsed_data_assunzione
                )
                db.add(dipendente)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Errore di integrità del database: {str(e)}")

    # Re-link orphaned certificates
    orphaned_certs = db.query(Certificato).options(selectinload(Certificato.corso)).filter(Certificato.dipendente_id.is_(None)).all()
    linked_count = 0

    database_path = settings.DATABASE_PATH or str(get_user_data_dir())

    for cert in orphaned_certs:
        if cert.nome_dipendente_raw:
            dob_raw = parse_date_flexible(cert.data_nascita_raw) if cert.data_nascita_raw else None
            match = matcher.find_employee_by_name(db, cert.nome_dipendente_raw, dob_raw)
            if match:
                # Capture Old Data (Orphan state) for file logic
                old_cert_data = {
                    'nome': cert.nome_dipendente_raw,
                    'matricola': None,
                    'categoria': cert.corso.categoria_corso if cert.corso else None,
                    'data_scadenza': cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else None
                }

                # Link Employee
                cert.dipendente_id = match.id
                linked_count += 1

                # Move File
                if database_path and old_cert_data['categoria']:
                    try:
                        old_path = find_document(database_path, old_cert_data)
                        if old_path and os.path.exists(old_path):
                            status = certificate_logic.get_certificate_status(db, cert)
                            target_status = "ATTIVO"
                            if status == "scaduto": target_status = "SCADUTO"
                            elif status == "archiviato": target_status = "STORICO"

                            # Prepare new data
                            new_cert_data = {
                                'nome': f"{match.cognome} {match.nome}",
                                'matricola': match.matricola,
                                'categoria': old_cert_data['categoria'],
                                'data_scadenza': old_cert_data['data_scadenza']
                            }

                            new_path = construct_certificate_path(database_path, new_cert_data, status=target_status)

                            if old_path != new_path:
                                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                                shutil.move(old_path, new_path)
                    except Exception as e:
                        print(f"Error moving orphan file {old_cert_data}: {e}")

    if linked_count > 0:
        db.commit()

    log_security_action(db, current_user, "DIPENDENTE_CREATE", f"Importato CSV: {file.filename}. Orfani collegati: {linked_count}", category="DATA")

    return {
        "message": f"Importazione completata con successo. {linked_count} certificati orfani collegati.",
        "warnings": warnings
    }

@router.get("/dipendenti", response_model=List[DipendenteSchema], dependencies=[Depends(deps.verify_license)])
def get_dipendenti(db: Session = Depends(get_db)):
    return db.query(Dipendente).all()

@router.get("/dipendenti/{dipendente_id}", response_model=DipendenteDetailSchema, dependencies=[Depends(deps.verify_license)])
def get_dipendente_detail(dipendente_id: int, db: Session = Depends(get_db)):
    dipendente = db.query(Dipendente).options(
        selectinload(Dipendente.certificati).selectinload(Certificato.corso)
    ).filter(Dipendente.id == dipendente_id).first()

    if not dipendente:
        raise HTTPException(status_code=404, detail="Dipendente non trovato")

    # Calculate status for all certs
    status_map = certificate_logic.get_bulk_certificate_statuses(db, dipendente.certificati)

    cert_schemas = []
    for cert in dipendente.certificati:
        if not cert.corso:
            continue

        status = status_map.get(cert.id, "attivo")

        cert_schemas.append(CertificatoSchema(
            id=cert.id,
            nome=f"{dipendente.cognome} {dipendente.nome}",
            data_nascita=dipendente.data_nascita.strftime('%d/%m/%Y') if dipendente.data_nascita else None,
            matricola=dipendente.matricola,
            corso=cert.corso.nome_corso,
            categoria=cert.corso.categoria_corso or "General",
            data_rilascio=cert.data_rilascio.strftime('%d/%m/%Y'),
            data_scadenza=cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else None,
            stato_certificato=status
        ))

    return DipendenteDetailSchema(
        id=dipendente.id,
        matricola=dipendente.matricola,
        nome=dipendente.nome,
        cognome=dipendente.cognome,
        data_nascita=dipendente.data_nascita,
        email=dipendente.email,
        categoria_reparto=dipendente.categoria_reparto,
        data_assunzione=dipendente.data_assunzione,
        certificati=cert_schemas
    )

@router.post("/dipendenti/", response_model=DipendenteSchema, dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
def create_dipendente(
    dipendente: DipendenteCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    if dipendente.matricola:
        if not dipendente.matricola.strip():
             raise HTTPException(status_code=400, detail="La matricola non può essere vuota o solo spazi.")
        existing = db.query(Dipendente).filter(Dipendente.matricola == dipendente.matricola).first()
        if existing:
            raise HTTPException(status_code=400, detail="Matricola già esistente.")

    if dipendente.email:
        existing_email = db.query(Dipendente).filter(Dipendente.email == dipendente.email).first()
        if existing_email:
             raise HTTPException(status_code=400, detail="Email già esistente.")

    new_dipendente = Dipendente(
        matricola=dipendente.matricola,
        nome=dipendente.nome,
        cognome=dipendente.cognome,
        data_nascita=dipendente.data_nascita,
        email=dipendente.email,
        categoria_reparto=dipendente.categoria_reparto,
        data_assunzione=dipendente.data_assunzione
    )
    db.add(new_dipendente)
    db.commit()
    db.refresh(new_dipendente)

    # Link potential orphan certificates
    link_orphaned_certificates(db, new_dipendente)
    db.commit()

    log_security_action(db, current_user, "DIPENDENTE_CREATE", f"Creato dipendente {dipendente.cognome} {dipendente.nome}", category="DATA")
    return new_dipendente

@router.put("/dipendenti/{dipendente_id}", response_model=DipendenteSchema, dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
def update_dipendente(
    dipendente_id: int,
    dipendente_data: DipendenteUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    dipendente = db.get(Dipendente, dipendente_id)
    if not dipendente:
        raise HTTPException(status_code=404, detail="Dipendente non trovato")

    update_dict = dipendente_data.model_dump(exclude_unset=True)

    if "matricola" in update_dict and update_dict["matricola"] != dipendente.matricola:
        if not update_dict["matricola"].strip():
             raise HTTPException(status_code=400, detail="La matricola non può essere vuota o solo spazi.")
        existing = db.query(Dipendente).filter(Dipendente.matricola == update_dict["matricola"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Matricola già esistente.")

    if "email" in update_dict and update_dict["email"] != dipendente.email:
         if update_dict["email"]:
            existing_email = db.query(Dipendente).filter(Dipendente.email == update_dict["email"]).first()
            if existing_email:
                 raise HTTPException(status_code=400, detail="Email già esistente.")

    for key, value in update_dict.items():
        setattr(dipendente, key, value)

    db.commit()
    db.refresh(dipendente)

    # Link potential orphan certificates (if name changed)
    link_orphaned_certificates(db, dipendente)
    db.commit()

    log_security_action(db, current_user, "DIPENDENTE_UPDATE", f"Aggiornato dipendente ID {dipendente_id}", category="DATA")
    return dipendente

@router.delete("/dipendenti/{dipendente_id}", dependencies=[Depends(deps.check_write_permission), Depends(deps.verify_license)])
def delete_dipendente(
    dipendente_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    dipendente = db.get(Dipendente, dipendente_id)
    if not dipendente:
        raise HTTPException(status_code=404, detail="Dipendente non trovato")

    log_details = f"Eliminato dipendente {dipendente.cognome} {dipendente.nome} (ID {dipendente_id})"
    db.delete(dipendente)
    db.commit()

    log_security_action(db, current_user, "DIPENDENTE_DELETE", log_details, category="DATA")
    return {"message": "Dipendente eliminato con successo"}
