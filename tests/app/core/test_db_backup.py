import pytest
from unittest.mock import patch
from app.core.db_security import DBSecurityManager
from pathlib import Path
import time

def test_backup_filename_format(tmp_path):
    # Setup ambiente mockato
    with patch("app.core.db_security.settings") as mock_settings, \
         patch("app.core.db_security.get_user_data_dir", return_value=tmp_path):

        mock_settings.DATABASE_PATH = None 

        manager = DBSecurityManager()
        # Simuliamo esistenza DB
        manager.db_path = tmp_path / "database_documenti.db"
        manager.db_path.touch()

        # Instead of patching time which is flaky with module imports,
        # we let it run and check if a file with the correct pattern exists.
        manager.create_backup()

        # Check in Backups folder
        backup_dir = tmp_path / "Backups"
        assert backup_dir.exists()

        # Look for any .bak file starting with database_documenti_
        backups = list(backup_dir.glob("database_documenti_*.bak"))
        assert len(backups) > 0, "Backup file was not created"

        # Verify the name format structure (roughly)
        # database_documenti_DD-MM-YYYY_ore_HH-MM.bak
        backup_name = backups[0].name
        assert "database_documenti_" in backup_name
        assert "_ore_" in backup_name
        assert backup_name.endswith(".bak")
