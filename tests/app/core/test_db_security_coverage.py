import pytest
import json
import logging
from unittest.mock import patch, MagicMock
from app.core.db_security import DBSecurityManager

@pytest.fixture
def manager(tmp_path):
    # Setup base per i test di coverage
    with patch("app.core.db_security.settings") as mock_settings, \
         patch("app.core.db_security.get_user_data_dir", return_value=tmp_path):

        mock_settings.DATABASE_PATH = None
        mgr = DBSecurityManager()
        # Setup paths
        mgr.db_path = tmp_path / "database_documenti.db"
        mgr.lock_path = tmp_path / ".test.db.lock"
        return mgr

@pytest.fixture
def mock_paths(manager, tmp_path):
    # Setup cartelle
    manager.data_dir = tmp_path / "app_data"
    manager.data_dir.mkdir()
    manager.db_path = manager.data_dir / "database_documenti.db"
    manager.lock_path = manager.data_dir / ".test.db.lock"
    return manager.data_dir, manager.db_path, manager.lock_path

def test_stale_lock_respects_valid_process(manager, mock_paths):
    metadata = {"pid": 12345, "uuid": "test-uuid-valid"}
    with open(manager.lock_path, "wb") as f:
        f.write(b'\0')
        f.write(json.dumps(metadata).encode('utf-8'))

    mock_proc = MagicMock()
    mock_proc.name.return_value = "intelleo_main"

    # FIX: Patchiamo psutil globalmente per intercettare le chiamate dal modulo db_security
    with patch("psutil.pid_exists", return_value=True), \
         patch("psutil.Process", return_value=mock_proc):

        with patch("os.remove") as mock_remove:
            manager._check_and_recover_stale_lock()
            mock_remove.assert_not_called()

def test_stale_lock_removes_dead_process(manager, mock_paths):
    metadata = {"pid": 99999, "uuid": "test-uuid-dead"}
    with open(manager.lock_path, "wb") as f:
        f.write(b'\0')
        f.write(json.dumps(metadata).encode('utf-8'))

    # Caso: PID non esiste
    with patch("psutil.pid_exists", return_value=False):
        with patch("os.remove") as mock_remove:
            manager._check_and_recover_stale_lock()
            mock_remove.assert_called_once_with(manager.lock_path)

def test_stale_lock_removes_unrelated_process(manager, mock_paths):
    metadata = {"pid": 55555, "uuid": "test-uuid-chrome"}
    with open(manager.lock_path, "wb") as f:
        f.write(b'\0')
        f.write(json.dumps(metadata).encode('utf-8'))

    mock_proc = MagicMock()
    mock_proc.name.return_value = "chrome.exe" # Nome non valido

    with patch("psutil.pid_exists", return_value=True), \
         patch("psutil.Process", return_value=mock_proc):

        with patch("os.remove") as mock_remove:
            manager._check_and_recover_stale_lock()
            mock_remove.assert_called_once_with(manager.lock_path)

def test_deserialize_failure(manager, mock_paths):
    manager.initial_bytes = b"header_ok_but_bad_data"
    manager.active_connection = None
    
    # Mock sqlite3.connect per restituire una connessione che fallisce su deserialize
    mock_conn = MagicMock()
    mock_conn.deserialize.side_effect = Exception("Deserialize error")

    with patch("sqlite3.connect", return_value=mock_conn):
        with pytest.raises(RuntimeError, match="Failed to deserialize database"):
            manager.get_connection()

def test_deserialize_not_supported(manager, mock_paths):
    manager.initial_bytes = b"data"
    manager.active_connection = None

    mock_conn = MagicMock()
    del mock_conn.deserialize # Simula mancanza metodo (vecchio python/sqlite)

    with patch("sqlite3.connect", return_value=mock_conn):
        with pytest.raises(RuntimeError, match="does not support 'deserialize'"):
            manager.get_connection()
