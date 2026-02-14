import os
import sqlite3
from unittest.mock import MagicMock, patch

import pytest

from app.core.config import settings
from app.core.db_security import DBSecurityManager


@pytest.fixture
def clean_db_settings():
    # Ensure settings don't interfere with path tests
    old_db_path = settings.mutable.get("DATABASE_PATH")
    settings.mutable.update({"DATABASE_PATH": None})
    yield
    settings.mutable.update({"DATABASE_PATH": old_db_path})


def test_db_security_init_paths(tmp_path, clean_db_settings):
    with patch("app.core.db_security.get_user_data_dir", return_value=tmp_path):
        manager = DBSecurityManager()
        # On Windows, path comparison might be tricky with slashes, but Path objects handle it
        assert manager.data_dir == tmp_path
        assert manager.db_path == tmp_path / "database_documenti.db"


def test_db_security_memory_db_fallback(tmp_path, clean_db_settings):
    with patch("app.core.db_security.get_user_data_dir", return_value=tmp_path):
        manager = DBSecurityManager()
        if manager.db_path.exists():
            os.remove(manager.db_path)

        conn = manager.get_connection()
        assert conn is not None
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test_mem (id INTEGER)")
        cursor.execute("INSERT INTO test_mem VALUES (1)")
        res = cursor.execute("SELECT * FROM test_mem").fetchone()
        assert res[0] == 1
        # No need to close if it's the manager's active_connection
        # but DBSecurityManager.active_connection is set by get_connection


def test_db_security_encryption_cycle(tmp_path, clean_db_settings):
    with patch("app.core.db_security.get_user_data_dir", return_value=tmp_path):
        manager = DBSecurityManager()
        manager.is_read_only = False  # IMPORTANT: allow saving

        test_data = b"SQLITE_DUMMY_DATA"
        # Mock serialize because real sqlite3 connection doesn't support it easily in tests without setup
        mock_conn = MagicMock()
        mock_conn.serialize.return_value = test_data
        manager.active_connection = mock_conn

        # Mock Fernet
        mock_fernet = MagicMock()
        mock_fernet.encrypt.side_effect = lambda x: b"ENC_" + x
        mock_fernet.decrypt.side_effect = lambda x: x[4:] if x.startswith(b"ENC_") else x
        manager.fernet = mock_fernet

        # Test toggle to encrypted (locked)
        manager.toggle_security_mode(enable_encryption=True)
        # Check file content (Header + Encrypted data)
        saved_bytes = manager.db_path.read_bytes()
        assert saved_bytes.startswith(manager._HEADER)
        assert b"ENC_" in saved_bytes

        # Test toggle to decrypted (unlocked)
        manager.toggle_security_mode(enable_encryption=False)
        assert manager.db_path.read_bytes() == test_data


def test_db_security_optimize(tmp_path, clean_db_settings):
    with patch("app.core.db_security.get_user_data_dir", return_value=tmp_path):
        manager = DBSecurityManager()
        manager.is_read_only = False

        # Use a real memory connection to avoid "execute is read-only" mock issues
        conn = sqlite3.connect(":memory:")
        manager.active_connection = conn

        # We can't easily assert execute was called on real object without wrapper
        # but we can check if it doesn't crash
        manager.optimize_database()

        # Verify save_to_disk was called (indirectly via file creation if we didn't mock save_to_disk)
        # Actually optimize_database calls self.save_to_disk()
        # Let's mock save_to_disk to verify it was called
        with patch.object(DBSecurityManager, "save_to_disk") as mock_save:
            manager.optimize_database()
            mock_save.assert_called()

        conn.close()
