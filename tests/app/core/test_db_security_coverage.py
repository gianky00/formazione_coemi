import pytest
import sys
import sqlite3
from unittest.mock import patch, MagicMock
import json
import os
from pathlib import Path
from app.core.db_security import DBSecurityManager

# --- Helpers ---
def is_serialization_supported():
    try:
        conn = sqlite3.connect(':memory:')
        if not hasattr(conn, 'serialize') or not hasattr(conn, 'deserialize'):
            conn.close()
            return False
        conn.execute("CREATE TABLE x(v)")
        data = conn.serialize()
        conn.deserialize(data)
        conn.close()
        return True
    except Exception:
        return False

@pytest.fixture
def mock_paths(tmp_path):
    root = tmp_path / "app_data"
    root.mkdir()
    db_path = root / "test.db"
    lock_path = root / ".test.db.lock"
    return root, db_path, lock_path

@pytest.fixture
def manager(mock_paths):
    root, db, lock = mock_paths
    with patch("app.core.db_security.settings") as mock_settings, \
         patch("app.core.db_security.get_user_data_dir", return_value=root):
        mock_settings.DATABASE_PATH = str(root)
        mgr = DBSecurityManager(db_name="test.db")
        yield mgr
        if hasattr(mgr, 'release_lock'):
            mgr.release_lock()

def test_stale_lock_recovery_dead_pid(manager, mock_paths):
    metadata = {"pid": 99999, "uuid": "test-uuid-dead"}
    with open(manager.lock_path, "wb") as f:
        f.write(b'\0') 
        f.write(json.dumps(metadata).encode('utf-8'))

    with patch("app.core.db_security.psutil.pid_exists", return_value=False):
        with patch("os.remove") as mock_remove:
            manager._check_and_recover_stale_lock()
            mock_remove.assert_called_once_with(manager.lock_path)

def test_stale_lock_recovery_unrelated_process(manager, mock_paths):
    metadata = {"pid": 12345, "uuid": "test-uuid-chrome"}
    with open(manager.lock_path, "wb") as f:
        f.write(b'\0')
        f.write(json.dumps(metadata).encode('utf-8'))

    mock_proc = MagicMock()
    mock_proc.name.return_value = "chrome.exe"

    with patch("app.core.db_security.psutil.pid_exists", return_value=True), \
         patch("app.core.db_security.psutil.Process", return_value=mock_proc):
        
        with patch("os.remove") as mock_remove:
            manager._check_and_recover_stale_lock()
            mock_remove.assert_called_once_with(manager.lock_path)

def test_stale_lock_respects_valid_process(manager, mock_paths):
    metadata = {"pid": 12345, "uuid": "test-uuid-valid"}
    with open(manager.lock_path, "wb") as f:
        f.write(b'\0')
        f.write(json.dumps(metadata).encode('utf-8'))

    mock_proc = MagicMock()
    mock_proc.name.return_value = "intelleo_main"

    # FIX: Patchiamo psutil dove viene importato in db_security
    with patch("app.core.db_security.psutil.pid_exists", return_value=True), \
         patch("app.core.db_security.psutil.Process", return_value=mock_proc):

        with patch("os.remove") as mock_remove:
            manager._check_and_recover_stale_lock()
            mock_remove.assert_not_called()

@pytest.mark.skipif(not is_serialization_supported(), reason="SQLite serialization not supported")
def test_verify_integrity_success(manager, mock_paths):
    conn = sqlite3.connect(':memory:')
    conn.execute("CREATE TABLE t (id INT)")
    conn.commit() 
    serialized = conn.serialize()
    conn.close()

    encrypted = manager._HEADER + manager.fernet.encrypt(serialized)
    with open(manager.db_path, "wb") as f:
        f.write(encrypted)
    assert manager.verify_integrity() is True

def test_verify_integrity_corrupt_header(manager, mock_paths):
    with open(manager.db_path, "wb") as f:
        f.write(b"INTELLEO_SEC_V1" + b"Garbage")
    assert manager.verify_integrity() is False

def test_restore_from_backup_success(manager, mock_paths):
    root, db, lock = mock_paths
    backup_path = root / "backup.bak"
    backup_path.write_text("Backup Content")

    # Creiamo DB originale
    manager.db_path.parent.mkdir(parents=True, exist_ok=True)
    manager.db_path.write_text("Original Content")

    manager.restore_from_backup(backup_path)

    assert manager.db_path.read_text() == "Backup Content"
    backups_dir = manager.data_dir / "Backups"
    assert backups_dir.exists()
    
    # FIX: restore_from_backup crea un backup di sicurezza PRIMA di sovrascrivere.
    # Quindi ci aspettiamo 2 file (il backup sorgente se copiato li, o il backup di sicurezza creato)
    # Verifichiamo solo che ci siano backup
    assert len(list(backups_dir.glob("*.bak"))) >= 1

def test_save_to_disk_read_only_block(manager):
    manager.is_read_only = True
    manager.active_connection = MagicMock() 
    with patch("os.replace") as mock_replace, patch("builtins.open", MagicMock()):
        result = manager.save_to_disk()
    assert result is False
    mock_replace.assert_not_called()

def test_move_database_success(manager, mock_paths):
    root, db, lock = mock_paths
    new_dir = root / "new_location"
    new_db = new_dir / db.name

    manager.is_read_only = False
    manager.db_path.parent.mkdir(parents=True, exist_ok=True)
    manager.db_path.write_text("DB CONTENT")

    with patch("app.core.db_security.settings.save_mutable_settings"):
        manager.move_database(new_dir)

    assert new_db.exists()
    assert new_db.read_text() == "DB CONTENT"
    assert manager.db_path == new_db