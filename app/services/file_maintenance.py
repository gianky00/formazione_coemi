import os
import shutil
import logging
from sqlalchemy.orm import Session
from app.db.models import Certificato
from app.services import certificate_logic
from app.services.document_locator import find_document
from app.core.config import settings, get_user_data_dir
from datetime import date

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

    # Optimization: Filter at DB level for potential candidates (expired dates)
    # This avoids iterating thousands of active certificates and triggering 'get_certificate_status' N+1 queries for them.
    today = date.today()
    certificates = db.query(Certificato).filter(
        Certificato.data_scadenza_calcolata.isnot(None),
        Certificato.data_scadenza_calcolata < today
    ).all()

    moved_count = 0

    for cert in certificates:
        status = certificate_logic.get_certificate_status(db, cert)

        if status == "scaduto":
            # Prepare data for locator
            cert_data = {
                'nome': f"{cert.dipendente.cognome} {cert.dipendente.nome}" if cert.dipendente else cert.nome_dipendente_raw,
                'matricola': cert.dipendente.matricola if cert.dipendente else None,
                'categoria': cert.corso.categoria_corso if cert.corso else None,
                'data_scadenza': cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else None
            }

            if not cert_data['categoria']:
                continue

            current_path = find_document(database_path, cert_data)

            if current_path and os.path.isfile(current_path):
                # Check if it is in ATTIVO or IN SCADENZA folder
                # Path structure: .../CATEGORY/STATUS/filename
                parent_dir = os.path.dirname(current_path)
                folder_name = os.path.basename(parent_dir)

                if folder_name in ["ATTIVO", "IN SCADENZA"]:
                    # Construct new path
                    # We want to replace the status folder with STORICO
                    # But we must be careful about the structure.
                    # Standard structure: DATABASE / DOCUMENTI DIPENDENTI / Name (Matr) / Cat / Status / File

                    # Let's verify structure by going up
                    cat_dir = os.path.dirname(parent_dir)

                    # Target: .../Category/STORICO/
                    target_dir = os.path.join(cat_dir, "STORICO")

                    if not os.path.exists(target_dir):
                        try:
                            os.makedirs(target_dir)
                        except OSError as e:
                            logging.error(f"Failed to create directory {target_dir}: {e}")
                            continue

                    filename = os.path.basename(current_path)
                    target_path = os.path.join(target_dir, filename)

                    try:
                        shutil.move(current_path, target_path)
                        logging.info(f"Moved expired file to STORICO: {filename}")
                        moved_count += 1
                    except Exception as e:
                        logging.error(f"Failed to move file {current_path} to {target_path}: {e}")

    logging.info(f"File maintenance completed. Moved {moved_count} files to STORICO.")
