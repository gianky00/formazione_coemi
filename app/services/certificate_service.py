import os
from datetime import datetime
from typing import Any

from fastapi import HTTPException
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


def get_or_create_course(db: Session, categoria: str, corso_nome: str) -> Corso:
    """Gets or creates a course based on category and name."""
    master_course = (
        db.query(Corso).filter(Corso.categoria_corso.ilike(f"%{categoria.strip()}%")).first()
    )
    if not master_course:
        master_course = Corso(
            nome_corso=categoria.strip().upper(),
            validita_mesi=60,
            categoria_corso=categoria.strip().upper(),
        )
        db.add(master_course)
        db.flush()

    course = (
        db.query(Corso)
        .filter(
            Corso.nome_corso.ilike(f"%{corso_nome}%"), Corso.categoria_corso.ilike(f"%{categoria}%")
        )
        .first()
    )
    if not course:
        course = Corso(
            nome_corso=corso_nome,
            validita_mesi=master_course.validita_mesi,
            categoria_corso=master_course.categoria_corso,
        )
        db.add(course)
        db.flush()
    return course


def validate_cert_input(certificato: Any) -> None:
    """Validates certificate input data."""
    if not hasattr(certificato, "data_rilascio") or not certificato.data_rilascio:
        raise HTTPException(status_code=422, detail="La data di rilascio non può essere vuota.")
    if (
        not hasattr(certificato, "nome")
        or not certificato.nome
        or not str(certificato.nome).strip()
    ):
        raise HTTPException(status_code=400, detail="Il nome non può essere vuoto.")
    if len(str(certificato.nome).strip().split()) < 2:
        raise HTTPException(
            status_code=400, detail="Formato nome non valido. Inserire nome e cognome."
        )


def check_duplicate_cert(
    db: Session, course_id: int, data_rilascio: Any, dipendente_id: int | None, nome_raw: str
) -> bool:
    """Checks for duplicate certificates."""
    query = db.query(Certificato).filter(
        Certificato.corso_id == course_id, Certificato.data_rilascio == data_rilascio
    )
    if dipendente_id:
        query = query.filter(Certificato.dipendente_id == dipendente_id)
    else:
        query = query.filter(
            Certificato.dipendente_id.is_(None),
            Certificato.nome_dipendente_raw.ilike(f"%{nome_raw.strip()}%"),
        )
    return query.first() is not None


def archive_obsolete_certs(db: Session, new_cert: Certificato) -> None:
    """Archives older certificates of the same category for the employee."""
    if not new_cert.dipendente_id or not new_cert.corso:
        return
    try:
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
            if certificate_logic.get_certificate_status(db, old_cert) == "archiviato":
                archive_certificate_file(db, old_cert)
    except Exception as e:
        import logging

        logging.error(f"Error archiving older certificates: {e}")


def update_cert_fields(db_cert: Certificato, update_data: dict[str, Any], db: Session) -> None:
    """Updates certificate identity and dates."""
    if "data_nascita" in update_data:
        db_cert.data_nascita_raw = str(update_data["data_nascita"])
    if "nome" in update_data:
        nome = str(update_data["nome"]).strip()
        if not nome:
            raise HTTPException(status_code=400, detail="Il nome non può essere vuoto.")
        db_cert.nome_dipendente_raw = nome
        if len(nome.split()) < 2:
            raise HTTPException(status_code=400, detail="Inserire nome e cognome.")

    if "nome" in update_data or "data_nascita" in update_data:
        dob = (
            parse_date_flexible(str(db_cert.data_nascita_raw)) if db_cert.data_nascita_raw else None
        )
        if db_cert.nome_dipendente_raw:
            match = matcher.find_employee_by_name(db, str(db_cert.nome_dipendente_raw), dob)
            db_cert.dipendente_id = match.id if match else None

    if "data_rilascio" in update_data:
        db_cert.data_rilascio = datetime.strptime(
            str(update_data["data_rilascio"]), DATE_FORMAT_DMY
        ).date()
    if "data_scadenza" in update_data:
        scadenza = update_data["data_scadenza"]
        db_cert.data_scadenza_calcolata = (
            datetime.strptime(str(scadenza), DATE_FORMAT_DMY).date()
            if scadenza and str(scadenza).strip() and str(scadenza).lower() != "none"
            else None
        )


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
        database_path = settings.DOCUMENTS_FOLDER or str(get_user_data_dir())
        if database_path:
            old_file_path = find_document(database_path, old_cert_data)
            if old_file_path and os.path.exists(old_file_path):
                file_moved, new_file_path = certificate_file_service.handle_file_rename(
                    database_path, status, old_file_path, new_cert_data
                )
    return file_moved, old_file_path, new_file_path, status
