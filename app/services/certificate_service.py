import os
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import get_user_data_dir, settings
from app.db.models import Certificato, Corso
from app.services import certificate_file_service, certificate_logic, matcher
from app.services.document_locator import find_document
from app.services.sync_service import archive_certificate_file
from app.utils.date_parser import parse_date_flexible

DATE_FORMAT_DMY: str = "%d/%m/%Y"


def get_orphan_cert_data(cert: Certificato) -> dict[str, Any]:
    """Helper to extract data from an orphan certificate for file lookup."""
    return {
        "nome": cert.nome_dipendente_raw,
        "matricola": None,
        "categoria": cert.corso.categoria_corso if cert.corso else None,
        "data_scadenza": cert.data_scadenza_calcolata.strftime(DATE_FORMAT_DMY)
        if cert.data_scadenza_calcolata
        else None,
    }


def validate_cert_input(cert_in: Any) -> None:
    """Validates certificate input data."""
    nome = getattr(cert_in, "nome", None)
    corso = getattr(cert_in, "corso", None)
    categoria = getattr(cert_in, "categoria", None)
    data_rilascio = getattr(cert_in, "data_rilascio", None)

    if not nome or not corso or not categoria or not data_rilascio:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Dati obbligatori mancanti.")

    # Validate name format
    if nome and len(str(nome).strip().split()) < 2:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Formato nome non valido")


def get_or_create_course(db: Session, categoria: str, nome_corso: str) -> Corso:
    """Retrieves an existing course or creates a new one."""
    course = (
        db.query(Corso)
        .filter(Corso.nome_corso.ilike(nome_corso))
        .filter(Corso.categoria_corso.ilike(categoria))
        .first()
    )
    if not course:
        course = Corso(nome_corso=nome_corso, categoria_corso=categoria, validita_mesi=0)
        db.add(course)
        db.commit()
        db.refresh(course)
    return course


def check_duplicate_cert(
    db: Session, course_id: int, data_rilascio: Any, dipendente_id: int | None, nome: str
) -> bool:
    """Checks if a certificate already exists."""
    from datetime import date

    if isinstance(data_rilascio, date):
        rilascio_dt = data_rilascio
    else:
        parsed = parse_date_flexible(str(data_rilascio))
        if not parsed:
            return False  # Or handle error
        rilascio_dt = parsed

    query = db.query(Certificato).filter(
        Certificato.corso_id == course_id, Certificato.data_rilascio == rilascio_dt
    )
    if dipendente_id:
        query = query.filter(Certificato.dipendente_id == dipendente_id)
    else:
        query = query.filter(Certificato.nome_dipendente_raw == nome)
    return query.first() is not None


def archive_obsolete_certs(db: Session, new_cert: Certificato) -> None:
    """Identifies and archives older certificates of the same type for the same employee."""
    if not new_cert.dipendente_id or not new_cert.corso:
        return

    # Find older certificates for same employee and same course category
    older_certs = (
        db.query(Certificato)
        .join(Corso)
        .filter(
            Certificato.dipendente_id == new_cert.dipendente_id,
            Corso.categoria_corso == new_cert.corso.categoria_corso,
            Certificato.id != new_cert.id,
            Certificato.data_rilascio < new_cert.data_rilascio,
        )
        .all()
    )

    for old_cert in older_certs:
        # Archive file
        archive_certificate_file(db, old_cert)
        # Note: We don't necessarily delete from DB, but the status logic will now see them as 'archiviato'


def update_cert_fields(db_cert: Certificato, update_data: dict[str, Any], db: Session) -> None:
    """Updates certificate model fields from a dictionary."""
    if "nome" in update_data:
        db_cert.nome_dipendente_raw = update_data["nome"]
    if "data_nascita" in update_data:
        db_cert.data_nascita_raw = update_data["data_nascita"]
    if "corso" in update_data or "categoria" in update_data:
        categoria = update_data.get(
            "categoria", db_cert.corso.categoria_corso if db_cert.corso else "ALTRO"
        )
        nome_corso = update_data.get(
            "corso", db_cert.corso.nome_corso if db_cert.corso else "Corso"
        )
        course = get_or_create_course(db, categoria, nome_corso)
        db_cert.corso_id = course.id
    if "data_rilascio" in update_data:
        parsed_r = parse_date_flexible(update_data["data_rilascio"])
        if parsed_r:
            db_cert.data_rilascio = parsed_r
    if "data_scadenza" in update_data:
        parsed_s = parse_date_flexible(update_data["data_scadenza"])
        if parsed_s:
            db_cert.data_scadenza_manuale = parsed_s

    certificate_logic.calculate_combined_data(db_cert)
    matcher.match_certificate_to_employee(db, db_cert)


def update_certificato_logic(
    db: Session, db_cert: Certificato, cert_in: Any
) -> tuple[bool, str | None, str | None, str]:
    """Business logic for updating a certificate and its physical file."""
    # 1. Capture old data for file synchronization
    old_cert_data = {
        "nome": f"{db_cert.dipendente.cognome} {db_cert.dipendente.nome}"
        if db_cert.dipendente
        else db_cert.nome_dipendente_raw,
        "matricola": db_cert.dipendente.matricola if db_cert.dipendente else None,
        "categoria": db_cert.corso.categoria_corso if db_cert.corso else None,
        "data_scadenza": db_cert.data_scadenza_calcolata.strftime(DATE_FORMAT_DMY)
        if db_cert.data_scadenza_calcolata
        else None,
    }

    # 2. Update database record
    if cert_in.nome:
        db_cert.nome_dipendente_raw = cert_in.nome
    if cert_in.data_nascita:
        db_cert.data_nascita_raw = cert_in.data_nascita

    if cert_in.corso:
        # Try to find matching course
        course = (
            db.query(Corso)
            .filter(Corso.nome_corso.ilike(f"%{cert_in.corso}%"))
            .filter(Corso.categoria_corso.ilike(f"%{cert_in.categoria}%"))
            .first()
        )
        if course:
            db_cert.corso_id = course.id

    if cert_in.data_rilascio:
        val_rilascio = parse_date_flexible(cert_in.data_rilascio)
        if val_rilascio:
            db_cert.data_rilascio = val_rilascio
    if cert_in.data_scadenza:
        db_cert.data_scadenza_manuale = parse_date_flexible(cert_in.data_scadenza)

    # Re-calculate automated fields
    certificate_logic.calculate_combined_data(db_cert)

    # 3. Match with employee if possible
    matcher.match_certificate_to_employee(db, db_cert)

    db.commit()
    db.refresh(db_cert)

    # 4. Sync File System
    return sync_cert_file_system(db_cert, old_cert_data, db)


def create_certificato_logic(db: Session, cert_in: Any) -> Certificato:
    """Business logic for creating a new certificate."""
    # Logic moved from main router
    db_cert = Certificato(
        nome_dipendente_raw=cert_in.nome,
        data_nascita_raw=cert_in.data_nascita,
        data_rilascio=parse_date_flexible(cert_in.data_rilascio) or date.today(),
        data_scadenza_manuale=parse_date_flexible(cert_in.data_scadenza),
    )

    # Try to find matching course
    course = (
        db.query(Corso)
        .filter(Corso.nome_corso.ilike(f"%{cert_in.corso}%"))
        .filter(Corso.categoria_corso.ilike(f"%{cert_in.categoria}%"))
        .first()
    )
    if course:
        db_cert.corso_id = course.id

    # Smart matching
    matcher.match_certificate_to_employee(db, db_cert)
    certificate_logic.calculate_combined_data(db_cert)

    db.add(db_cert)
    db.commit()
    db.refresh(db_cert)

    # Attempt to find physical file
    database_path = settings.DOCUMENTS_FOLDER or str(get_user_data_dir())
    if database_path:
        # Standard matching logic for finding files
        cert_data = {
            "nome": cert_in.nome,
            "matricola": db_cert.dipendente.matricola if db_cert.dipendente else None,
            "categoria": course.categoria_corso if course else cert_in.categoria,
            "data_scadenza": db_cert.data_scadenza_calcolata.strftime(DATE_FORMAT_DMY)
            if db_cert.data_scadenza_calcolata
            else None,
        }
        found_path = find_document(database_path, cert_data)
        if found_path:
            db_cert.file_path = found_path
            db.commit()

    return db_cert


def delete_certificato_logic(db: Session, db_cert: Certificato) -> None:
    """Safely deletes a certificate and archives its file."""
    # 1. Archive file
    archive_certificate_file(db, db_cert)

    # 2. Delete from DB
    db.delete(db_cert)
    db.commit()


def sync_cert_file_system(
    db_cert: Certificato, old_cert_data: dict[str, Any], db: Session
) -> tuple[bool, str | None, str | None, str]:
    """Synchronizes file system changes after certificate update."""
    file_moved = False
    old_file_path = None
    new_file_path = None

    new_cert_data = {
        "nome": f"{db_cert.dipendente.cognome} {db_cert.dipendente.nome}"
        if db_cert.dipendente
        else db_cert.nome_dipendente_raw,
        "matricola": db_cert.dipendente.matricola if db_cert.dipendente else None,
        "categoria": db_cert.corso.categoria_corso if db_cert.corso else None,
        "data_scadenza": db_cert.data_scadenza_calcolata.strftime(DATE_FORMAT_DMY)
        if db_cert.data_scadenza_calcolata
        else None,
    }

    status = certificate_logic.get_certificate_status(db, db_cert)

    if old_cert_data != new_cert_data:
        database_path_str = settings.DOCUMENTS_FOLDER or str(get_user_data_dir())
        if database_path_str:
            database_path = Path(database_path_str)
            old_file_path = find_document(str(database_path), old_cert_data)

            # Fallback to existing DB path if find_document fails
            if not old_file_path and db_cert.file_path and os.path.exists(db_cert.file_path):
                old_file_path = db_cert.file_path

            if old_file_path and os.path.exists(old_file_path):
                file_moved, new_file_path = certificate_file_service.handle_file_rename(
                    database_path, status, old_file_path, new_cert_data
                )
    return file_moved, old_file_path, new_file_path, status
