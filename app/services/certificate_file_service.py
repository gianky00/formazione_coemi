import logging
import os
import shutil
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def handle_file_rename(
    database_path: Path, status: str, old_file_path: str, new_cert_data: dict[str, Any]
) -> tuple[bool, str | None]:
    """Rinomina o sposta il file fisico basandosi sui nuovi dati del certificato."""
    if not old_file_path or not os.path.exists(old_file_path):
        return False, None

    try:
        old_path = Path(old_file_path)
        ext = old_path.suffix

        # Build a descriptive name
        matricola = new_cert_data.get("matricola") or "N-A"
        nome = new_cert_data.get("nome", "certificato")
        categoria = new_cert_data.get("categoria", "corso")
        scadenza = new_cert_data.get("data_scadenza", "").replace("/", "")

        parts = []
        if matricola != "N-A":
            parts.append(str(matricola))
        parts.append(nome)
        parts.append(categoria)
        if scadenza:
            parts.append(scadenza)

        new_name = "_".join(parts) + ext

        # Sanitize filename
        from app.utils.file_security import sanitize_filename

        new_name = sanitize_filename(new_name).replace(" ", "_")

        # Organize in DOCUMENTI DIPENDENTI / Nome (Matricola) / Categoria / Stato
        # Standardize status to uppercase for folder consistency
        status_dir_name = status.upper()

        employee_folder = f"{sanitize_filename(nome)} ({sanitize_filename(str(matricola))})"
        target_dir = (
            database_path
            / "DOCUMENTI DIPENDENTI"
            / employee_folder
            / sanitize_filename(categoria)
            / status_dir_name
        )
        target_dir.mkdir(parents=True, exist_ok=True)

        new_path = target_dir / new_name

        # Evita sovrascritture se il nome esiste già
        counter = 1
        while new_path.exists():
            new_path = target_dir / f"{new_path.stem}_{counter}{ext}"
            counter += 1

        shutil.move(str(old_path), str(new_path))
        return True, str(new_path)
    except Exception as e:
        logger.error(f"Errore durante rinomina file: {e}")
        return False, None


def rollback_file_move(
    file_moved: bool, old_file_path: str, new_file_path: str | None, certificato_id: int
) -> None:
    """Annulla lo spostamento del file in caso di errore nel database."""
    if not file_moved or not new_file_path or not os.path.exists(new_file_path):
        return

    try:
        shutil.move(new_file_path, old_file_path)
        logger.info(f"Rollback file completato per certificato {certificato_id}")
    except Exception as e:
        logger.error(f"Errore durante rollback file per {certificato_id}: {e}")
