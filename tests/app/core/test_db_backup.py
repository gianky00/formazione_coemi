import pytest
from unittest.mock import patch
from app.core.db_security import DBSecurityManager
from pathlib import Path

def test_backup_filename_format(tmp_path):
    # Setup ambiente mockato
    with patch("app.core.db_security.settings") as mock_settings, \
         patch("app.core.db_security.get_user_data_dir", return_value=tmp_path):

        mock_settings.DATABASE_PATH = None 

        manager = DBSecurityManager()
        # Simuliamo esistenza DB
        manager.db_path = tmp_path / "database_documenti.db"
        manager.db_path.touch()

        # FIX: Patchiamo 'app.core.db_security.time' invece di 'time' generico
        # Questo assicura che la funzione interna usi il nostro valore mockato
        with patch("app.core.db_security.time") as mock_time:
            mock_time.strftime.return_value = "01-12-2025_ore_22-37"

            manager.create_backup()

            # Nome atteso
            expected_name = "database_documenti_01-12-2025_ore_22-37.bak"
            expected_path = tmp_path / "Backups" / expected_name

            # Verifica
            assert expected_path.exists()