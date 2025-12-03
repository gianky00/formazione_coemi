import pytest
from unittest.mock import MagicMock, patch, mock_open
import os
import json
from pathlib import Path
from app.core.db_security import DBSecurityManager

# Mocking the settings to avoid creating real directories
@pytest.fixture
def mock_settings(monkeypatch):
    mock_settings_obj = MagicMock()
    mock_settings_obj.DATABASE_PATH = None
    monkeypatch.setattr("app.core.db_security.settings", mock_settings_obj)
    monkeypatch.setattr("app.core.db_security.get_user_data_dir", lambda: Path("/tmp/mock_user_data"))

@pytest.fixture
def db_manager(mock_settings, monkeypatch):
    # Mock LockManager inside DBSecurityManager
    mock_lock_manager_cls = MagicMock()
    monkeypatch.setattr("app.core.db_security.LockManager", mock_lock_manager_cls)

    # Mock os.path.exists to avoid real file checks
    monkeypatch.setattr(Path, "exists", lambda self: False)

    manager = DBSecurityManager()
    manager.lock_manager = mock_lock_manager_cls.return_value
    return manager

def test_acquire_session_lock_success(db_manager):
    """Test successful lock acquisition."""
    db_manager.lock_manager.acquire.return_value = (True, None)

    success, owner = db_manager.acquire_session_lock({"username": "test"})

    assert success is True
    assert db_manager.is_read_only is False
    assert db_manager.read_only_info is None

def test_acquire_session_lock_failure(db_manager):
    """Test failure to acquire lock (already locked)."""
    owner_info = {"username": "other"}
    db_manager.lock_manager.acquire.return_value = (False, owner_info)

    success, owner = db_manager.acquire_session_lock({"username": "test"})

    assert success is False
    assert owner == owner_info
    assert db_manager.is_read_only is True
    assert db_manager.read_only_info == owner_info

def test_save_to_disk_read_only_blocked(db_manager):
    """Test that saving is blocked in read-only mode."""
    db_manager.is_read_only = True
    db_manager.active_connection = MagicMock()

    result = db_manager.save_to_disk()

    assert result is False
    db_manager.active_connection.serialize.assert_not_called()

def test_save_to_disk_success(db_manager):
    """Test successful save when not read-only."""
    db_manager.is_read_only = False
    db_manager.active_connection = MagicMock()
    db_manager.active_connection.serialize.return_value = b"database_bytes"
    db_manager.is_locked_mode = False # Plain save

    mock_file = MagicMock()
    mock_file.__enter__.return_value = mock_file

    with patch("builtins.open", return_value=mock_file), \
         patch("os.replace") as mock_replace:
             result = db_manager.save_to_disk()

    assert result is True
    db_manager.active_connection.serialize.assert_called_once()

def test_cleanup_calls_release(db_manager):
    """Test that cleanup releases the lock."""
    # We mock save_to_disk to avoid complexity
    with patch.object(db_manager, "save_to_disk") as mock_save:
        with patch.object(db_manager, "release_lock") as mock_release:
            db_manager.cleanup()

            mock_save.assert_called_once()
            mock_release.assert_called_once()

def test_stale_lock_recovery_active_process(db_manager, monkeypatch):
    """Test that if PID exists and is 'intelleo', lock is kept."""
    mock_pid = 12345
    metadata = {"pid": mock_pid}

    mock_file = MagicMock()
    # When read is called, return JSON bytes
    mock_file.read.return_value = json.dumps(metadata).encode()
    mock_file.__enter__.return_value = mock_file

    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", return_value=mock_file), \
         patch("psutil.pid_exists", return_value=True), \
         patch("psutil.Process") as mock_proc_cls:

        mock_proc = mock_proc_cls.return_value
        mock_proc.name.return_value = "intelleo.exe"

        with patch.object(db_manager, "_force_remove_lock") as mock_remove:
            db_manager._check_and_recover_stale_lock()

            mock_remove.assert_not_called()

def test_stale_lock_recovery_dead_process(db_manager, monkeypatch):
    """Test that if PID does not exist, lock is removed."""
    mock_pid = 99999
    metadata = {"pid": mock_pid}

    mock_file = MagicMock()
    mock_file.read.return_value = json.dumps(metadata).encode()
    mock_file.__enter__.return_value = mock_file

    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", return_value=mock_file), \
         patch("psutil.pid_exists", return_value=False):

        with patch.object(db_manager, "_force_remove_lock") as mock_remove:
            db_manager._check_and_recover_stale_lock()

            mock_remove.assert_called_once()
