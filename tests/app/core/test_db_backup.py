from unittest.mock import patch
from app.core.db_security import DBSecurityManager

def test_backup_filename_format(tmp_path):
    # Mocking environment
    with patch("app.core.db_security.settings") as mock_settings, \
         patch("app.core.db_security.get_user_data_dir", return_value=tmp_path):

        mock_settings.DATABASE_PATH = None # Ensure default path logic uses user_data_dir (tmp_path)

        manager = DBSecurityManager()
        # Mock db path existence
        manager.db_path = tmp_path / "database_documenti.db"
        manager.db_path.touch()

        # Override time to a known value for testing? Or just check regex
        # Using time.strftime inside the method, so patching time.strftime is best
        with patch("app.core.db_security.time.strftime") as mock_time:
            mock_time.return_value = "01-12-2025_ore_22-37"

            manager.create_backup()

            # Check file created
            expected_name = "database_documenti_01-12-2025_ore_22-37.bak"
            expected_path = tmp_path / "Backups" / expected_name

            assert expected_path.exists()

            # Verify the call was made with correct format string
            # We check call_args_list because logging also calls strftime
            calls = [args[0] for args, _ in mock_time.call_args_list]
            assert "%d-%m-%Y_ore_%H-%M" in calls
