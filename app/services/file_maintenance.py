import os
import shutil
import logging
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from app.db.models import Certificato, AuditLog, Dipendente
from app.services import certificate_logic, matcher
from app.utils.date_parser import parse_date_flexible
from app.services.document_locator import find_document, construct_certificate_path
from app.core.config import settings, get_user_data_dir
from app.utils.audit import log_security_action
from datetime import date, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def organize_expired_files(db: Session):
    """
    Checks for expired certificates and moves their files to the 'STORICO' folder.
    This should be run on application startup if the database is writable.
    """
    logging.info("Starting file maintenance: organizing expired files...")

    database_path = settings.DATABASE_PATH or str(get_user_data_dir())
    if not database_path or not os.path.exists(database_path):
        logging.warning(f"Database path not found or invalid: {database_path}. Skipping maintenance.")
        return

    # Optimization: Frequency Check - Run only once per day
    today = date.today()
    existing_log = db.query(AuditLog).filter(
        AuditLog.action == "SYSTEM_MAINTENANCE",
        func.date(AuditLog.timestamp) == today
    ).first()

    if existing_log:
        logging.info("Maintenance task already ran today. Skipping.")
        return

    # Optimization: Filter at DB level for potential candidates (expired dates)
    # This avoids iterating thousands of active certificates and triggering 'get_certificate_status' N+1 queries for them.
    certificates = db.query(Certificato).filter(
        Certificato.data_scadenza_calcolata.isnot(None),
        Certificato.data_scadenza_calcolata < today
    ).all()

    moved_count = 0

    for cert in certificates:
        status = certificate_logic.get_certificate_status(db, cert)

        if status in ["scaduto", "archiviato"]:
            if archive_certificate_file(db, cert):
                moved_count += 1

    # Daily Cleanup: Remove empty folders in DOCUMENTI DIPENDENTI
    docs_path = os.path.join(database_path, "DOCUMENTI DIPENDENTI")
    if os.path.exists(docs_path):
        clean_all_empty_folders(docs_path)

    # Log Rotation (1 year retention)
    cleanup_audit_logs(db, retention_days=365)

    log_security_action(db, None, "SYSTEM_MAINTENANCE", f"File maintenance completed. Moved {moved_count} files.", category="SYSTEM")
    logging.info(f"File maintenance completed. Moved {moved_count} files to STORICO.")

def clean_all_empty_folders(root_path):
    """
    Recursively scans the directory tree and removes empty directories.
    Uses bottom-up walk to ensure parent directories become empty if all children are removed.
    """
    if not os.path.isdir(root_path):
        return

    logging.info(f"Cleaning empty folders in {root_path}...")
    removed_count = 0

    for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
        # Check actual content as os.walk list might be stale
        try:
            if not os.listdir(dirpath):
                # Don't delete the root itself
                if os.path.normpath(dirpath) == os.path.normpath(root_path):
                    continue

                os.rmdir(dirpath)
                removed_count += 1
        except OSError:
            pass

    logging.info(f"Cleaned {removed_count} empty folders.")

def remove_empty_folders(path):
    """
    Recursively removes empty folders starting from the given path and moving upwards.
    Stops if a folder is not empty or if it reaches the database root.
    """
    if not os.path.isdir(path):
        return

    # Try to remove the leaf
    try:
        os.rmdir(path)
        # Recurse up
        remove_empty_folders(os.path.dirname(path))
    except OSError:
        # Directory not empty or other error
        return

def synchronize_all_files(db: Session):
    """
    Scans all certificates and ensures their PDF files are located in the correct
    path according to current naming conventions and status.
    Also cleans up empty folders.
    """
    logging.info("Starting Mass File Synchronization...")
    database_path = settings.DATABASE_PATH or str(get_user_data_dir())

    if not database_path or not os.path.exists(database_path):
        return {"error": "Database path invalid"}

    certs = db.query(Certificato).options(selectinload(Certificato.dipendente), selectinload(Certificato.corso)).all()

    moved = 0
    missing = 0

    for cert in certs:
        # Skip if no course (corrupted data)
        if not cert.corso: continue

        cert_data = {
            'nome': f"{cert.dipendente.cognome} {cert.dipendente.nome}" if cert.dipendente else cert.nome_dipendente_raw,
            'matricola': cert.dipendente.matricola if cert.dipendente else None,
            'categoria': cert.corso.categoria_corso,
            'data_scadenza': cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else None
        }

        status = certificate_logic.get_certificate_status(db, cert)

        if status in ["attivo", "in_scadenza"]:
            target_status = "ATTIVO"
        else: # scaduto, archiviato
            target_status = "STORICO"

        expected_path = construct_certificate_path(database_path, cert_data, status=target_status)

        # Check current location
        current_path = find_document(database_path, cert_data)

        if current_path and os.path.exists(current_path):
            # Normalize for comparison
            if os.path.normpath(current_path) != os.path.normpath(expected_path):
                try:
                    os.makedirs(os.path.dirname(expected_path), exist_ok=True)
                    shutil.move(current_path, expected_path)
                    moved += 1
                    # Clean up old folder
                    remove_empty_folders(os.path.dirname(current_path))
                except Exception as e:
                    logging.error(f"Failed to sync file for cert {cert.id}: {e}")
        else:
            missing += 1

    logging.info(f"Sync complete. Moved: {moved}, Missing: {missing}")
    return {"moved": moved, "missing": missing}

def archive_certificate_file(db: Session, cert: Certificato) -> bool:
    """
    Moves a certificate's file to the STORICO folder.
    Returns True if file was moved, False otherwise.
    """
    database_path = settings.DATABASE_PATH or str(get_user_data_dir())
    if not database_path or not os.path.exists(database_path):
        return False

    # Need course relation for category
    # Usually lazy loaded if attached to session
    if not cert.corso:
        return False

    cert_data = {
        'nome': f"{cert.dipendente.cognome} {cert.dipendente.nome}" if cert.dipendente else cert.nome_dipendente_raw,
        'matricola': cert.dipendente.matricola if cert.dipendente else None,
        'categoria': cert.corso.categoria_corso,
        'data_scadenza': cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else None
    }

    current_path = find_document(database_path, cert_data)

    if current_path and os.path.exists(current_path):
        # Check if already in STORICO?
        # find_document returns path. If it's already in STORICO, we don't need to move unless logic demands.
        # But construct_certificate_path(..., status="STORICO") will give target.

        expected_path = construct_certificate_path(database_path, cert_data, status="STORICO")

        if os.path.normpath(current_path) != os.path.normpath(expected_path):
            try:
                os.makedirs(os.path.dirname(expected_path), exist_ok=True)
                shutil.move(current_path, expected_path)
                remove_empty_folders(os.path.dirname(current_path))
                logging.info(f"Archived file to: {expected_path}")
                return True
            except Exception as e:
                logging.error(f"Failed to archive file for cert {cert.id}: {e}")
    return False

def cleanup_audit_logs(db: Session, retention_days: int = 365):
    """
    Deletes audit logs older than retention_days.
    """
    cutoff = date.today() - timedelta(days=retention_days)
    try:
        deleted = db.query(AuditLog).filter(func.date(AuditLog.timestamp) < cutoff).delete(synchronize_session=False)
        db.commit()
        if deleted > 0:
            logging.info(f"Cleaned up {deleted} old audit logs (older than {retention_days} days).")
            log_security_action(db, None, "LOG_CLEANUP", f"Deleted {deleted} logs older than {cutoff}", category="SYSTEM")
    except Exception as e:
        logging.error(f"Error cleaning audit logs: {e}")
        db.rollback()

def link_orphaned_certificates(db: Session, dipendente: Dipendente) -> int:
    """
    Scans for orphaned certificates that match the given employee and links them.
    Moves associated files from (N-A) folder to employee folder.
    """
    orphans = db.query(Certificato).options(selectinload(Certificato.corso)).filter(Certificato.dipendente_id.is_(None)).all()
    linked_count = 0

    database_path = settings.DATABASE_PATH or str(get_user_data_dir())

    for cert in orphans:
        if not cert.nome_dipendente_raw: continue

        dob_raw = parse_date_flexible(cert.data_nascita_raw) if cert.data_nascita_raw else None

        # Optimization: Only check if dob matches (if present)
        if dob_raw and dipendente.data_nascita and dob_raw != dipendente.data_nascita:
            continue

        match = matcher.find_employee_by_name(db, cert.nome_dipendente_raw, dob_raw)

        if match and match.id == dipendente.id:
            # Capture Old Data (Orphan state)
            old_cert_data = {
                'nome': cert.nome_dipendente_raw,
                'matricola': None,
                'categoria': cert.corso.categoria_corso if cert.corso else None,
                'data_scadenza': cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else None
            }

            cert.dipendente_id = dipendente.id
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

                        new_cert_data = {
                            'nome': f"{dipendente.cognome} {dipendente.nome}",
                            'matricola': dipendente.matricola,
                            'categoria': old_cert_data['categoria'],
                            'data_scadenza': old_cert_data['data_scadenza']
                        }

                        new_path = construct_certificate_path(database_path, new_cert_data, status=target_status)

                        if old_path != new_path:
                            os.makedirs(os.path.dirname(new_path), exist_ok=True)
                            shutil.move(old_path, new_path)
                            remove_empty_folders(os.path.dirname(old_path))
                except Exception as e:
                    logging.error(f"Error moving linked orphan file: {e}")

    return linked_count
