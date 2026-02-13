import logging
import os
import shutil

from app.services.document_locator import construct_certificate_path
from app.services.sync_service import (
    get_unique_filename,
)


def handle_file_rename(database_path, status, old_file_path, new_cert_data):
    """Helper to handle file renaming during certificate update."""
    if status in ["attivo", "in_scadenza"]:
        target_status = "ATTIVO"
    else:
        target_status = "STORICO"

    new_file_path = construct_certificate_path(database_path, new_cert_data, status=target_status)

    if old_file_path != new_file_path:
        dest_dir = os.path.dirname(new_file_path)
        os.makedirs(dest_dir, exist_ok=True)

        filename = os.path.basename(new_file_path)
        unique_filename = get_unique_filename(dest_dir, filename)
        new_file_path = os.path.join(dest_dir, unique_filename)

        shutil.move(old_file_path, new_file_path)
        return True, new_file_path

    return False, None


def rollback_file_move(file_moved, old_file_path, new_file_path, certificato_id):
    """Rolls back a file move operation if the DB transaction fails."""
    if file_moved and old_file_path and new_file_path and os.path.exists(new_file_path):
        try:
            shutil.move(new_file_path, old_file_path)
        except Exception as rollback_err:
            logging.error(
                f"CRITICAL: Failed to rollback file move for cert {certificato_id}: {rollback_err}"
            )
