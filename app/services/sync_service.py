import os
import shutil
import logging
from sqlalchemy.orm import Session, selectinload
from app.db.models import Certificato, AuditLog, Dipendente
from app.services import certificate_logic, matcher
from app.services.document_locator import find_document, construct_certificate_path
from app.core.config import settings, get_user_data_dir
from app.utils.date_parser import parse_date_flexible

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def remove_empty_folders(path, root_path=None):
    """
    Recursively removes empty folders starting from the given path and moving upwards.
    Stops if a folder is not empty or if it reaches the database root.
    """
    if not os.path.isdir(path):
        return
    
    # Bug 7 Fix: Safety check to prevent deleting root DB folder
    if root_path and os.path.normpath(path) == os.path.normpath(root_path):
        return
    
    # Also hard stop at drive root or crazy short paths just in case
    if len(path) < 4: 
        return

    # Try to remove the leaf
    try:
        os.rmdir(path)
        # Recurse up
        remove_empty_folders(os.path.dirname(path), root_path=root_path)
    except OSError:
        # Directory not empty or other error
        return

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

def get_unique_filename(directory, filename):
    """
    Generates a unique filename if the target already exists to prevent overwrites.
    Appends _1, _2, etc.
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

def archive_certificate_file(db: Session, cert: Certificato) -> bool:
    """
    Moves a certificate's file to the STORICO folder.
    Returns True if file was moved, False otherwise.
    """
    database_path = settings.DATABASE_PATH or str(get_user_data_dir())
    if not database_path or not os.path.exists(database_path):
        return False

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
        expected_path = construct_certificate_path(database_path, cert_data, status="STORICO")

        if os.path.normpath(current_path) != os.path.normpath(expected_path):
            try:
                dest_dir = os.path.dirname(expected_path)
                os.makedirs(dest_dir, exist_ok=True)

                # Prevent overwrite
                filename = os.path.basename(expected_path)
                unique_filename = get_unique_filename(dest_dir, filename)
                final_path = os.path.join(dest_dir, unique_filename)

                # Bug 4 Fix: Handle PermissionError (File Locked) gracefully
                shutil.move(current_path, final_path)
                remove_empty_folders(os.path.dirname(current_path), root_path=database_path)
                logging.info(f"Archived file to: {final_path}")
                return True
            except PermissionError as e:
                logging.warning(f"File locked, skipping archive for cert {cert.id}: {e}")
                return False
            except Exception as e:
                logging.error(f"Failed to archive file for cert {cert.id}: {e}")
    return False

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

        if dob_raw and dipendente.data_nascita and dob_raw != dipendente.data_nascita:
            continue

        match = matcher.find_employee_by_name(db, cert.nome_dipendente_raw, dob_raw)

        if match and match.id == dipendente.id:
            old_cert_data = {
                'nome': cert.nome_dipendente_raw,
                'matricola': None,
                'categoria': cert.corso.categoria_corso if cert.corso else None,
                'data_scadenza': cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else None
            }

            cert.dipendente_id = dipendente.id
            linked_count += 1

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
                            dest_dir = os.path.dirname(new_path)
                            os.makedirs(dest_dir, exist_ok=True)

                            filename = os.path.basename(new_path)
                            unique_filename = get_unique_filename(dest_dir, filename)
                            final_path = os.path.join(dest_dir, unique_filename)

                            # Bug 4 Fix: Handle PermissionError
                            shutil.move(old_path, final_path)
                            remove_empty_folders(os.path.dirname(old_path), root_path=database_path)
                except PermissionError as e:
                    logging.warning(f"File locked, could not move orphan file: {e}")
                except Exception as e:
                    logging.error(f"Error moving linked orphan file: {e}")

    return linked_count

def synchronize_all_files(db: Session):
    """
    Scans all certificates and ensures their PDF files are located in the correct
    path according to current naming conventions and status.
    """
    logging.info("Starting Mass File Synchronization...")
    database_path = settings.DATABASE_PATH or str(get_user_data_dir())

    if not database_path or not os.path.exists(database_path):
        return {"error": "Database path invalid"}

    certs = db.query(Certificato).options(selectinload(Certificato.dipendente), selectinload(Certificato.corso)).all()

    # Bug 3 Fix: Bulk Status Calculation (Optimization)
    status_map = certificate_logic.get_bulk_certificate_statuses(db, certs)

    moved = 0
    missing = 0

    for cert in certs:
        if not cert.corso: continue

        cert_data = {
            'nome': f"{cert.dipendente.cognome} {cert.dipendente.nome}" if cert.dipendente else cert.nome_dipendente_raw,
            'matricola': cert.dipendente.matricola if cert.dipendente else None,
            'categoria': cert.corso.categoria_corso,
            'data_scadenza': cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else None
        }

        status = status_map.get(cert.id, "attivo")

        if status in ["attivo", "in_scadenza"]:
            target_status = "ATTIVO"
        else:
            target_status = "STORICO"

        expected_path = construct_certificate_path(database_path, cert_data, status=target_status)
        current_path = find_document(database_path, cert_data)

        if current_path and os.path.exists(current_path):
            if os.path.normpath(current_path) != os.path.normpath(expected_path):
                try:
                    dest_dir = os.path.dirname(expected_path)
                    os.makedirs(dest_dir, exist_ok=True)

                    filename = os.path.basename(expected_path)
                    unique_filename = get_unique_filename(dest_dir, filename)
                    final_path = os.path.join(dest_dir, unique_filename)

                    # Bug 4 Fix: Handle PermissionError
                    shutil.move(current_path, final_path)
                    moved += 1
                    remove_empty_folders(os.path.dirname(current_path), root_path=database_path)
                except PermissionError as e:
                    logging.warning(f"File locked, skipping sync for cert {cert.id}: {e}")
                except Exception as e:
                    logging.error(f"Failed to sync file for cert {cert.id}: {e}")
        else:
            missing += 1

    logging.info(f"Sync complete. Moved: {moved}, Missing: {missing}")
    return {"moved": moved, "missing": missing}
