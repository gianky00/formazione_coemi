import logging
import os
import shutil
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


def handle_file_rename(
    database_path: Path, status: str, old_file_path: str, new_cert_data: dict[str, Any]
) -> tuple[bool, Optional[str]]:
    """Rinomina o sposta il file fisico basandosi sui nuovi dati del certificato."""
    if not old_file_path or not os.path.exists(old_file_path):
        return False, None

    try:
        old_path = Path(old_file_path)
        ext = old_path.suffix
        new_name = f"{new_cert_data.get('nome', 'certificato')}_{new_cert_data.get('corso', 'corso')}{ext}"
        new_name = "".join(c for h in new_name if (c := h if h.isalnum() or h in "._-" else "_"))

        target_dir = database_path / status
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
    file_moved: bool, old_file_path: str, new_file_path: Optional[str], certificato_id: int
) -> None:
    """Annulla lo spostamento del file in caso di errore nel database."""
    if not file_moved or not new_file_path or not os.path.exists(new_file_path):
        return

    try:
        shutil.move(new_file_path, old_file_path)
        logger.info(f"Rollback file completato per certificato {certificato_id}")
    except Exception as e:
        logger.error(f"Errore durante rollback file per {certificato_id}: {e}")
