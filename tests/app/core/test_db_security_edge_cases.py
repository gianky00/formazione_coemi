import pytest
from unittest.mock import patch, MagicMock, mock_open
import json
from app.core.db_security import DBSecurityManager

@pytest.fixture
def manager(tmp_path):
    with patch("app.core.db_security.settings") as mock_settings, \
         patch("app.core.db_security.get_user_data_dir", return_value=tmp_path):
        mock_settings.DATABASE_PATH = str(tmp_path)
        return DBSecurityManager(db_name="test.db")

def test_stale_lock_empty_file(manager, tmp_path):
    lock = tmp_path / ".test.db.lock"
    lock.write_bytes(b"") # Empty

    manager._check_and_recover_stale_lock()
    assert lock.exists() # Should ignore empty files (not stale logic) or return early

def test_stale_lock_corrupt_json(manager, tmp_path):
    lock = tmp_path / ".test.db.lock"
    lock.write_bytes(b"L{bad_json")

    with patch.object(manager, "_force_remove_lock") as mock_rem:
        manager._check_and_recover_stale_lock()
        mock_rem.assert_called()

def test_stale_lock_psutil_exception(manager, tmp_path):
    lock = tmp_path / ".test.db.lock"
    lock.write_bytes(b"L" + json.dumps({"pid": 123}).encode())

    with patch("app.core.db_security.psutil.pid_exists", side_effect=Exception("Psutil fail")):
         # Should catch and log
         manager._check_and_recover_stale_lock()

def test_restore_backup_not_found(manager, tmp_path):
    with pytest.raises(FileNotFoundError):
        manager.restore_from_backup(tmp_path / "missing.bak")

def test_restore_backup_copy_fail(manager, tmp_path):
    backup = tmp_path / "backup.bak"
    backup.write_text("content")

    with patch("shutil.copy2", side_effect=Exception("Copy fail")):
        with pytest.raises(Exception, match="Copy fail"):
            manager.restore_from_backup(backup)

from tenacity import RetryError

def test_safe_write_permission_retry(manager, tmp_path):
    # Mock safe_write retries
    manager.db_path = tmp_path / "db.db"

    # We mock open to verify retries
    # But safe_write uses retry decorator. Testing decorator needs checking delay.
    # Instead, let's verify it raises after attempts.

    with patch("builtins.open", side_effect=PermissionError("Locked")), \
         patch("time.sleep"): # Speed up

        # Tenacity raises RetryError wrapping the exception
        with pytest.raises(RetryError):
             manager._safe_write(b"data")

def test_verify_integrity_decrypt_fail(manager, tmp_path):
    db = tmp_path / "test.db"
    db.write_bytes(manager._HEADER + b"bad_encrypted_data")

    assert manager.verify_integrity() is False

def test_verify_integrity_sqlite_fail(manager, tmp_path):
    # Decrypts fine (mock fernet) but invalid sqlite
    db = tmp_path / "test.db"

    manager.fernet = MagicMock()
    manager.fernet.decrypt.return_value = b"Not SQLite"

    db.write_bytes(manager._HEADER + b"any")

    assert manager.verify_integrity() is False

def test_move_database_same_path(manager, tmp_path):
    manager.is_read_only = False
    current = manager.db_path
    manager.move_database(current) # Should do nothing
    assert manager.db_path == current

def test_create_backup_failure(manager, tmp_path):
    manager.db_path = tmp_path / "test.db"
    manager.db_path.write_text("data")

    with patch("shutil.copy2", side_effect=Exception("Backup Fail")):
        # Should catch and log, not raise
        manager.create_backup()

def test_rotate_backups_failure(manager, tmp_path):
    b_dir = tmp_path / "Backups"
    b_dir.mkdir()

    with patch("pathlib.Path.glob", side_effect=Exception("Glob Fail")):
        manager.rotate_backups(b_dir)

def test_optimize_failure(manager):
    manager.active_connection = MagicMock()
    manager.is_read_only = False
    manager.active_connection.execute.side_effect = Exception("Vacuum Fail")

    with pytest.raises(Exception, match="Vacuum Fail"):
        manager.optimize_database()

def test_move_database_failure(manager, tmp_path):
    manager.is_read_only = False
    manager.db_path = tmp_path / "src.db"
    manager.db_path.write_text("data")

    with patch("shutil.move", side_effect=OSError("Move Fail")):
        # The method re-raises
        with pytest.raises(OSError):
            manager.move_database(tmp_path / "dst")

def test_sync_db_alias(manager):
    with patch.object(manager, "save_to_disk") as mock_save:
        manager.sync_db()
        mock_save.assert_called_once()
