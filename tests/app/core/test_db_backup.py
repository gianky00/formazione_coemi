import pytest
from unittest.mock import patch, MagicMock
from app.core.db_security import DBSecurityManager
from pathlib import Path
import time
import shutil

def test_backup_filename_format(tmp_path):
    # Setup paths
    data_dir = tmp_path / "app_data"
    data_dir.mkdir()
    db_path = data_dir / "database_documenti.db"
    db_path.touch()

    # Instantiate Manager and FORCE paths to ensure test isolation
    manager = DBSecurityManager()
    manager.data_dir = data_dir
    manager.db_path = db_path

    # Ensure backups dir doesn't exist yet
    backup_dir = data_dir / "Backups"
    if backup_dir.exists():
        shutil.rmtree(backup_dir)

    # Run action
    manager.create_backup()

    # Verify
    assert backup_dir.exists(), f"Backup directory {backup_dir} not created"

    backups = list(backup_dir.glob("database_documenti_*.bak"))
    assert len(backups) > 0, "No backup file found"

    backup_name = backups[0].name
    assert "database_documenti_" in backup_name
    assert "_ore_" in backup_name
    assert backup_name.endswith(".bak")
