import os
import shutil
import logging
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from app.db.models import Certificato, AuditLog
from app.services import certificate_logic
from app.core.config import settings, get_user_data_dir
from app.utils.audit import log_security_action
from app.services.sync_service import clean_all_empty_folders, archive_certificate_file
from app.services.document_locator import find_document
from datetime import date, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scan_and_archive_orphans(db: Session, database_path: str):
    """
    Bug 8 Fix: Identify files in 'DOCUMENTI DIPENDENTI' that are NOT in the database.
    Move them to 'DOCUMENTI DIPENDENTI/ORFANI' instead of deleting them.
    This helps in identifying data drift.
    """
    logging.info("Starting orphan file scan...")
    docs_path = os.path.join(database_path, "DOCUMENTI DIPENDENTI")
    if not os.path.exists(docs_path):
        return 0

    # 1. Gather all known file paths from DB
    known_files = set()
    certs = db.query(Certificato).options(selectinload(Certificato.dipendente), selectinload(Certificato.corso)).all()

    for cert in certs:
        # Construct expected path logic is complex due to multiple status folders.
        # Instead, we rely on 'find_document' logic or simpler: we know the files exist if find_document returns something.
        # But find_document scans. We need the reverse: for every file on disk, does it belong to a cert?

        # To be efficient: we build a set of expected filenames or partial paths?
        # No, duplicate filenames are possible in different folders.
        # We need to canonicalize paths.

        cert_data = {
            'nome': f"{cert.dipendente.cognome} {cert.dipendente.nome}" if cert.dipendente else cert.nome_dipendente_raw,
            'matricola': cert.dipendente.matricola if cert.dipendente else None,
            'categoria': cert.corso.categoria_corso if cert.corso else None,
            'data_scadenza': cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else None
        }

        if cert_data['categoria']:
            found_path = find_document(database_path, cert_data)
            if found_path:
                known_files.add(os.path.normpath(found_path))

    orphans_moved = 0
    orphan_dest_base = os.path.join(docs_path, "ORFANI")

    # 2. Walk the disk
    for root, dirs, files in os.walk(docs_path):
        # Skip special folders
        if "ORFANI" in root or "ERRORI ANALISI" in root or "CESTINO" in root:
            continue

        for file in files:
            if not file.lower().endswith('.pdf'):
                continue

            full_path = os.path.normpath(os.path.join(root, file))

            if full_path not in known_files:
                # Potential Orphan
                # Double check: maybe it's a "renamed" file or legacy format?
                # For safety, we move it to ORFANI preserving structure

                rel_path = os.path.relpath(full_path, docs_path)
                dest_path = os.path.join(orphan_dest_base, rel_path)

                try:
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.move(full_path, dest_path)
                    orphans_moved += 1
                    logging.warning(f"Orphan file detected and moved: {full_path} -> {dest_path}")
                except Exception as e:
                    logging.error(f"Failed to move orphan file {full_path}: {e}")

    if orphans_moved > 0:
        log_security_action(db, None, "ORPHAN_CLEANUP", f"Moved {orphans_moved} orphaned files to 'ORFANI' folder.", category="SYSTEM")

    return orphans_moved

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

    # Bug 8 Fix: Orphan Scan
    orphans = scan_and_archive_orphans(db, database_path)

    # Log Rotation (1 year retention)
    cleanup_audit_logs(db, retention_days=365)

    log_security_action(db, None, "SYSTEM_MAINTENANCE", f"File maintenance completed. Moved {moved_count} expired files. Archived {orphans} orphans.", category="SYSTEM")
    logging.info(f"File maintenance completed. Moved {moved_count} files to STORICO.")

def cleanup_audit_logs(db: Session, retention_days: int = 365, max_records: int = 100000):
    """
    Deletes audit logs older than retention_days AND ensures total count does not exceed max_records.
    """
    # 1. Time-based Cleanup
    cutoff = date.today() - timedelta(days=retention_days)
    try:
        deleted = db.query(AuditLog).filter(func.date(AuditLog.timestamp) < cutoff).delete(synchronize_session=False)
        db.commit()
        if deleted > 0:
            logging.info(f"Cleaned up {deleted} old audit logs (older than {retention_days} days).")
            log_security_action(db, None, "LOG_CLEANUP", f"Deleted {deleted} logs older than {cutoff}", category="SYSTEM")
    except Exception as e:
        logging.error(f"Error cleaning audit logs (time-based): {e}")
        db.rollback()

    # 2. Size-based Cleanup
    try:
        count = db.query(AuditLog).count()
        if count > max_records:
            excess = count - max_records
            # Delete oldest 'excess' records
            subquery = db.query(AuditLog.id).order_by(AuditLog.timestamp.asc()).limit(excess)
            deleted_excess = db.query(AuditLog).filter(AuditLog.id.in_(subquery)).delete(synchronize_session=False)
            db.commit()
            logging.info(f"Cleaned up {deleted_excess} excess audit logs (Limit: {max_records}).")
            log_security_action(db, None, "LOG_CLEANUP", f"Deleted {deleted_excess} excess logs", category="SYSTEM")
    except Exception as e:
        logging.error(f"Error cleaning audit logs (size-based): {e}")
        db.rollback()
