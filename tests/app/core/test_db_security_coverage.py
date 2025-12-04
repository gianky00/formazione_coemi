import pytest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
from pathlib import Path
from app.core.db_security import DBSecurityManager

@pytest.fixture
def mock_paths(tmp_path):
    """Setup temp paths for the manager."""
    db_path = tmp_path / "test.db"
    lock_path = tmp_path / ".test.db.lock"
    return tmp_path, db_path, lock_path

@pytest.fixture
def manager(mock_paths):
    """
    Creates a fresh DBSecurityManager instance for each test.
    We patch the global settings and user data dir to isolate it.
    """
    root, db, lock = mock_paths

    with patch("app.core.db_security.settings") as mock_settings, \
         patch("app.core.db_security.get_user_data_dir", return_value=root):

        mock_settings.DATABASE_PATH = str(root)

        # Prevent auto-recovery during init so we can test it manually if needed,
        # or let it run on empty dir (safe).
        mgr = DBSecurityManager(db_name="test.db")
        return mgr

def test_stale_lock_recovery_dead_pid(manager, mock_paths):
    """Test that a lock file pointing to a dead PID is removed."""
    root, db, lock_path = mock_paths

    # Create a stale lock file
    metadata = {"pid": 99999, "uuid": "test-uuid"}
    with open(lock_path, "wb") as f:
        f.write(b'L') # Lock byte
        f.write(json.dumps(metadata).encode('utf-8'))

    # Mock psutil to say PID 99999 is DEAD
    with patch("app.core.db_security.psutil.pid_exists", return_value=False):
        # Trigger recovery
        manager._check_and_recover_stale_lock()

    # Lock should be gone
    assert not lock_path.exists()

def test_stale_lock_recovery_unrelated_process(manager, mock_paths):
    """Test that a lock file pointing to an unrelated process (e.g. Chrome) is removed."""
    root, db, lock_path = mock_paths

    metadata = {"pid": 12345, "uuid": "test-uuid"}
    with open(lock_path, "wb") as f:
        f.write(b'L')
        f.write(json.dumps(metadata).encode('utf-8'))

    # Mock psutil: PID exists but is 'chrome.exe'
    mock_proc = MagicMock()
    mock_proc.name.return_value = "chrome.exe"

    with patch("app.core.db_security.psutil.pid_exists", return_value=True), \
         patch("app.core.db_security.psutil.Process", return_value=mock_proc):

        manager._check_and_recover_stale_lock()

    assert not lock_path.exists()

def test_stale_lock_respects_valid_process(manager, mock_paths):
    """Test that a lock file pointing to a valid Intelleo process is PRESERVED."""
    root, db, lock_path = mock_paths

    metadata = {"pid": 12345, "uuid": "test-uuid"}
    with open(lock_path, "wb") as f:
        f.write(b'L')
        f.write(json.dumps(metadata).encode('utf-8'))

    # Mock psutil: PID exists and is 'intelleo'
    mock_proc = MagicMock()
    mock_proc.name.return_value = "intelleo_main"

    with patch("app.core.db_security.psutil.pid_exists", return_value=True), \
         patch("app.core.db_security.psutil.Process", return_value=mock_proc):

        manager._check_and_recover_stale_lock()

    assert lock_path.exists()

def test_verify_integrity_success(manager, mock_paths):
    """Test integrity check on a valid encrypted file."""
    root, db, lock = mock_paths

    # 1. Create a fake encrypted DB file
    # We need to simulate a valid SQLite structure inside
    import sqlite3
    conn = sqlite3.connect(':memory:')
    conn.execute("CREATE TABLE t (id INT)")
    serialized = conn.serialize()
    conn.close()

    encrypted = manager._HEADER + manager.fernet.encrypt(serialized)
    with open(db, "wb") as f:
        f.write(encrypted)

    # 2. Run verification
    assert manager.verify_integrity() is True

def test_verify_integrity_corrupt_header(manager, mock_paths):
    """Test integrity check fails on bad header/decryption."""
    root, db, lock = mock_paths

    # Write garbage
    with open(db, "wb") as f:
        f.write(b"INTELLEO_SEC_V1" + b"GarbageDataThatFailsDecryption")

    assert manager.verify_integrity() is False

def test_restore_from_backup_success(manager, mock_paths):
    """Test restoring from a backup file."""
    root, db, lock = mock_paths

    backup_path = root / "backup.bak"
    backup_path.write_text("Backup Content")

    # Ensure DB exists so backup logic works
    db.write_text("Original Content")

    manager.restore_from_backup(backup_path)

    # Check DB now has backup content
    assert db.read_text() == "Backup Content"
    # Check a backup of the original was created
    backups_dir = root / "Backups"
    assert backups_dir.exists()
    assert len(list(backups_dir.glob("*.bak"))) == 1

def test_save_to_disk_read_only_block(manager):
    """Test that save_to_disk is blocked in read-only mode."""
    manager.is_read_only = True
    manager.active_connection = MagicMock() # Simulate active DB

    with patch("builtins.open") as mock_file:
        result = manager.save_to_disk()

    assert result is False
    mock_file.assert_not_called()

def test_optimize_database(manager):
    manager.active_connection = MagicMock()
    manager.is_read_only = False

    with patch.object(manager, "save_to_disk") as mock_save:
        manager.optimize_database()

    manager.active_connection.execute.assert_any_call("VACUUM")
    manager.active_connection.execute.assert_any_call("ANALYZE")
    mock_save.assert_called_once()

def test_move_database_success(manager, mock_paths):
    root, db, lock = mock_paths
    new_dir = root / "new_location"
    new_db = new_dir / db.name

    # Setup
    manager.is_read_only = False
    with open(db, "w") as f: f.write("DB CONTENT")

    with patch("app.core.db_security.settings.save_mutable_settings") as mock_save_settings:
        manager.move_database(new_dir)

    assert new_db.exists()
    assert new_db.read_text() == "DB CONTENT"
    assert not db.exists() # Moved
    assert manager.db_path == new_db
    mock_save_settings.assert_called_with({"DATABASE_PATH": str(new_dir)})
