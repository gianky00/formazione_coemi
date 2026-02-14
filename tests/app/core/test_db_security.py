import json
import os
import sqlite3
from unittest.mock import patch

import pytest

from app.core.db_security import DBSecurityManager


def create_dummy_db(path):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()


@pytest.fixture
def temp_workspace(tmp_path):
    return tmp_path


@pytest.fixture
def mock_user_data_dir(mocker, temp_workspace):
    return mocker.patch("app.core.db_security.get_user_data_dir", return_value=temp_workspace)


def test_load_memory_db_plain(temp_workspace, mock_user_data_dir):
    db_name = "test_plain.db"
    db_path = temp_workspace / db_name
    create_dummy_db(db_path)

    from app.core.config import settings

    with patch.dict(settings.mutable._data, {"DATABASE_PATH": str(temp_workspace)}):
        manager = DBSecurityManager(db_name=db_name)
        manager.load_memory_db()

        assert manager.is_locked_mode is True
        assert manager.initial_bytes is not None
        assert manager.initial_bytes.startswith(b"SQ")  # SQLite header


def test_lock_enables_read_only(temp_workspace, mock_user_data_dir):
    db_name = "test_lock.db"
    db_path = temp_workspace / db_name
    create_dummy_db(db_path)

    # Force settings to use this workspace
    from app.core.config import settings

    with patch.dict(settings.mutable._data, {"DATABASE_PATH": str(temp_workspace)}):
        # Instance 1: Running and Locked
        manager1 = DBSecurityManager(db_name=db_name)
        manager1.load_memory_db()
        success1, _ = manager1.acquire_session_lock({"user": "admin_1"})
        assert success1 is True

        # Instance 2: Startup
        manager2 = DBSecurityManager(db_name=db_name)
        manager2.load_memory_db()

        # Try to acquire lock
        success2, owner_info = manager2.acquire_session_lock({"user": "admin_2"})

        # Should FAIL to acquire lock
        assert success2 is False
        assert manager2.is_read_only is True

        # On Windows, owner_info might be None due to file sharing locks
        if os.name != "nt":
            assert owner_info is not None
            assert owner_info["user"] == "admin_1"

        manager1.release_lock()


def test_stale_lock_recovery(temp_workspace, mock_user_data_dir):
    db_name = "test_stale.db"
    manager = DBSecurityManager(db_name=db_name)

    # Create a "stale" lock file (Just a file, no OS lock held)
    stale_info = {"user": "zombie_process", "pid": 9999, "uuid": "zombie-123"}
    os.makedirs(os.path.dirname(manager.lock_path), exist_ok=True)
    with open(manager.lock_path, "wb") as f:
        f.write(b"\x01")
        f.write(json.dumps(stale_info).encode("utf-8"))

    # Now try to acquire (should succeed because PID 9999 doesn't exist or is unrelated)
    # We must ensure psutil.pid_exists(9999) returns False
    with patch("psutil.pid_exists", return_value=False):
        success, _ = manager.acquire_session_lock({"user": "live_process"})

    assert success is True
    assert manager.is_read_only is False
    manager.release_lock()


def test_save_to_disk_encrypted(temp_workspace, mock_user_data_dir):
    db_name = "test_encrypt.db"
    manager = DBSecurityManager(db_name=db_name)
    manager.load_memory_db()
    manager.acquire_session_lock({"user": "test"})

    # Create some data
    conn = manager.get_connection()
    conn.execute("CREATE TABLE secret (data TEXT)")
    conn.execute("INSERT INTO secret VALUES ('my-secret')")
    conn.commit()

    # Enable encryption
    manager.toggle_security_mode(enable_encryption=True)
    assert manager.is_locked_mode is True

    # Save
    manager.save_to_disk()

    # Verify file is encrypted (starts with header)
    with open(manager.db_path, "rb") as f:
        header = f.read(len(manager._HEADER))
        assert header == manager._HEADER

    manager.release_lock()
