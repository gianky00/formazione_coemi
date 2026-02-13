import logging
import os
import shutil
from typing import Any

from sqlalchemy.orm import Session, selectinload

from app.core.config import get_user_data_dir, settings
from app.db.models import Certificato, Dipendente
from app.services import certificate_logic, matcher
from app.services.document_locator import construct_certificate_path, find_document
from app.utils.date_parser import parse_date_flexible

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DATE_FORMAT_DMY: str = "%d/%m/%Y"


def remove_empty_folders(path: str, root_path: str | None = None) -> None:
    """
    Recursively removes empty folders starting from the given path and moving upwards.
    """
    if not os.path.isdir(path):
        return

    if root_path and os.path.normpath(path) == os.path.normpath(root_path):
        return

    if len(path) < 4:
        return

    try:
        os.rmdir(path)
        remove_empty_folders(os.path.dirname(path), root_path=root_path)
    except OSError:
        return


def clean_all_empty_folders(root_path: str) -> None:
    """
    Recursively scans the directory tree and removes empty directories.
    """
    if not os.path.isdir(root_path):
        return

    logging.info(f"Cleaning empty folders in {root_path}...")
    removed_count = 0

    for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
        try:
            if not os.listdir(dirpath):
                if os.path.normpath(dirpath) == os.path.normpath(root_path):
                    continue

                os.rmdir(dirpath)
                removed_count += 1
        except OSError:
            pass

    logging.info(f"Cleaned {removed_count} empty folders.")


def get_unique_filename(directory: str, filename: str) -> str:
    """
    Generates a unique filename if the target already exists to prevent overwrites.
    """
    if not os.path.exists(os.path.join(directory, filename)):
        return filename

    name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = f"{name}_{counter}{ext}"

    while os.path.exists(os.path.join(directory, new_filename)):
        counter += 1
        new_filename = f"{name}_{counter}{ext}"

    return new_filename


def _move_file_safely(current_path: str, expected_path: str, database_path: str) -> bool:
    """Helper to move file with overwrite protection and folder cleanup."""
    if os.path.normpath(current_path) == os.path.normpath(expected_path):
        return False

    try:
        dest_dir = os.path.dirname(expected_path)
        os.makedirs(dest_dir, exist_ok=True)

        filename = os.path.basename(expected_path)
        unique_filename = get_unique_filename(dest_dir, filename)
        final_path = os.path.join(dest_dir, unique_filename)

        if os.path.exists(final_path):
            logging.warning(f"Destination {final_path} appeared suddenly. Regenerating name.")
            unique_filename = get_unique_filename(dest_dir, filename)  # Retry once
            final_path = os.path.join(dest_dir, unique_filename)

        if os.path.exists(final_path):
            logging.error(f"Cannot move file, destination occupied: {final_path}")
            return False

        shutil.move(current_path, final_path)
        remove_empty_folders(os.path.dirname(current_path), root_path=database_path)
        logging.info(f"Moved file to: {final_path}")
        return True
    except PermissionError as e:
        logging.warning(f"File locked, skipping move: {e}")
        return False
    except Exception as e:
        logging.error(f"Failed to move file: {e}")
        return False


def archive_certificate_file(db: Session, cert: Certificato) -> bool:
    """
    Moves a certificate's file to the STORICO folder.
    """
    database_path = settings.DOCUMENTS_FOLDER or str(get_user_data_dir())
    if not database_path or not os.path.exists(database_path):
        return False

    if not cert.corso:
        return False

    cert_data = {
        "nome": f"{cert.dipendente.cognome} {cert.dipendente.nome}"
        if cert.dipendente
        else cert.nome_dipendente_raw,
        "matricola": cert.dipendente.matricola if cert.dipendente else None,
        "categoria": cert.corso.categoria_corso,
        "data_scadenza": cert.data_scadenza_calcolata.strftime(DATE_FORMAT_DMY)
        if cert.data_scadenza_calcolata
        else None,
    }

    current_path = find_document(database_path, cert_data)

    if current_path and os.path.exists(current_path):
        expected_path = construct_certificate_path(database_path, cert_data, status="STORICO")
        return _move_file_safely(current_path, expected_path, database_path)

    return False


def link_orphaned_certificates(db: Session, dipendente: Dipendente) -> int:
    """
    Scans for orphaned certificates that match the given employee and links them.
    """
    orphans = (
        db.query(Certificato)
        .options(selectinload(Certificato.corso))
        .filter(Certificato.dipendente_id.is_(None))
        .all()
    )
    linked_count = 0
    database_path = settings.DOCUMENTS_FOLDER or str(get_user_data_dir())

    for cert in orphans:
        if not cert.nome_dipendente_raw:
            continue

        dob_raw = parse_date_flexible(str(cert.data_nascita_raw)) if cert.data_nascita_raw else None
        if dob_raw and dipendente.data_nascita and dob_raw != dipendente.data_nascita:
            continue

        match = matcher.find_employee_by_name(db, str(cert.nome_dipendente_raw), dob_raw)

        if match and match.id == dipendente.id:
            _link_and_move_orphan(db, cert, dipendente, database_path)
            linked_count += 1

    return linked_count


def _link_and_move_orphan(
    db: Session, cert: Certificato, dipendente: Dipendente, database_path: str
) -> None:
    old_cert_data = {
        "nome": cert.nome_dipendente_raw,
        "matricola": None,
        "categoria": cert.corso.categoria_corso if cert.corso else None,
        "data_scadenza": cert.data_scadenza_calcolata.strftime(DATE_FORMAT_DMY)
        if cert.data_scadenza_calcolata
        else None,
    }

    cert.dipendente_id = dipendente.id

    if database_path and old_cert_data["categoria"]:
        try:
            old_path = find_document(database_path, old_cert_data)
            if old_path and os.path.exists(old_path):
                status = certificate_logic.get_certificate_status(db, cert)
                target_status = "ATTIVO"
                if status == "scaduto":
                    target_status = "SCADUTO"
                elif status == "archiviato":
                    target_status = "STORICO"

                new_cert_data = {
                    "nome": f"{dipendente.cognome} {dipendente.nome}",
                    "matricola": dipendente.matricola,
                    "categoria": old_cert_data["categoria"],
                    "data_scadenza": old_cert_data["data_scadenza"],
                }

                new_path = construct_certificate_path(
                    database_path, new_cert_data, status=target_status
                )
                _move_file_safely(old_path, new_path, database_path)
        except Exception as e:
            logging.error(f"Error moving linked orphan file: {e}")


def _process_sync_cert(
    cert: Certificato, database_path: str, status_map: dict[int, str]
) -> tuple[bool, bool]:
    """Helper to process a single certificate sync."""
    if not cert.corso:
        return False, False

    cert_data = {
        "nome": f"{cert.dipendente.cognome} {cert.dipendente.nome}"
        if cert.dipendente
        else cert.nome_dipendente_raw,
        "matricola": cert.dipendente.matricola if cert.dipendente else None,
        "categoria": cert.corso.categoria_corso,
        "data_scadenza": cert.data_scadenza_calcolata.strftime(DATE_FORMAT_DMY)
        if cert.data_scadenza_calcolata
        else None,
    }

    status = status_map.get(int(cert.id), "attivo")
    target_status = "ATTIVO" if status in ["attivo", "in_scadenza"] else "STORICO"

    expected_path = construct_certificate_path(database_path, cert_data, status=target_status)
    current_path = find_document(database_path, cert_data)

    if current_path and os.path.exists(current_path):
        return _move_file_safely(current_path, expected_path, database_path), False

    return False, True  # Missing


def synchronize_all_files(db: Session) -> dict[str, Any]:
    """
    Ensures PDF files are in correct paths according to current design.
    """
    logging.info("Starting Mass File Synchronization...")
    database_path = settings.DOCUMENTS_FOLDER or str(get_user_data_dir())

    if not database_path or not os.path.exists(database_path):
        return {"error": "Database path invalid"}

    certs = (
        db.query(Certificato)
        .options(selectinload(Certificato.dipendente), selectinload(Certificato.corso))
        .all()
    )
    status_map = certificate_logic.get_bulk_certificate_statuses(db, certs)

    moved = 0
    missing = 0

    for cert in certs:
        was_moved, was_missing = _process_sync_cert(cert, database_path, status_map)
        if was_moved:
            moved += 1
        if was_missing:
            missing += 1

    logging.info(f"Sync complete. Moved: {moved}, Missing: {missing}")
    return {"moved": moved, "missing": missing}
