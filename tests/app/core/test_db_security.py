import pytest
import os
import time
import sqlite3
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.core.db_security import DBSecurityManager

@pytest.fixture
def temp_workspace(tmp_path):
    return tmp_path

@pytest.fixture
def mock_user_data_dir(temp_workspace):
    with patch('app.core.db_security.get_user_data_dir', return_value=temp_workspace) as m:
        yield m

def create_dummy_db(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, data TEXT)")
    c.execute("INSERT INTO test (data) VALUES ('secret_data')")
    conn.commit()
    conn.close()

def test_in_memory_lifecycle(temp_workspace, mock_user_data_dir):
    db_name = "database_documenti.db"
    db_path = temp_workspace / db_name

    # 1. Create Plain DB on disk
    create_dummy_db(db_path)

    manager = DBSecurityManager(db_name=db_name)

    # 2. Load (Should Auto-Encrypt in RAM)
    manager.load_memory_db()
    assert manager.is_locked_mode is True
    assert manager.initial_bytes is not None

    # Verify connection has data
    conn = manager.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT data FROM test")
    assert cur.fetchone()[0] == 'secret_data'

    # 3. Lock (Simulate Login)
    success, _ = manager.acquire_session_lock({"user": "test_user"})
    assert success is True
    assert manager.is_read_only is False

    # 4. Modify in RAM
    conn.execute("INSERT INTO test (data) VALUES ('new_ram_data')")
    conn.commit()

    # 5. Save to Disk (Sync)
    save_result = manager.save_to_disk()
    assert save_result is True

    # 6. Check Disk Content
    # Disk should be encrypted (Header check)
    with open(db_path, "rb") as f:
        header = f.read(len(manager._HEADER))
        assert header == manager._HEADER

    # Verify Disk is NOT valid sqlite
    try:
        conn_disk = sqlite3.connect(db_path)
        c_disk = conn_disk.cursor()
        c_disk.execute("SELECT * FROM test")
        assert False, "Should not be able to open encrypted DB"
    except (sqlite3.DatabaseError, sqlite3.OperationalError):
        pass
    except Exception:
        pass

    # 7. Unlock/Cleanup (Simulate Logout/Shutdown)
    manager.cleanup()
    # Note: Lock file might still exist, but lock is released.

    # 8. Reload (Simulate Restart)
    manager2 = DBSecurityManager(db_name=db_name)
    manager2.load_memory_db()
    conn2 = manager2.get_connection()
    cur2 = conn2.cursor()
    cur2.execute("SELECT data FROM test WHERE data='new_ram_data'")
    assert cur2.fetchone()[0] == 'new_ram_data'

def test_lock_enables_read_only(temp_workspace, mock_user_data_dir):
    """
    Simulate two instances.
    Instance 1 holds the lock.
    Instance 2 should start in Read-Only mode.
    """
    db_name = "database_documenti.db"
    db_path = temp_workspace / db_name
    create_dummy_db(db_path)

    # Instance 1: Running and Locked
    manager1 = DBSecurityManager(db_name=db_name)
    manager1.load_memory_db()
    success1, _ = manager1.acquire_session_lock({"user": "admin_1"})
    assert success1 is True

    # Instance 2: Startup
    manager2 = DBSecurityManager(db_name=db_name)
    manager2.load_memory_db() # Should succeed now
    conn2 = manager2.get_connection() # Initialize connection

    # Try to acquire lock
    success2, owner_info = manager2.acquire_session_lock({"user": "admin_2"})

    # Should FAIL to acquire lock
    assert success2 is False
    assert manager2.is_read_only is True

    # Should retrieve owner info
    assert owner_info is not None
    assert owner_info["user"] == "admin_1"

    # Instance 2 tries to save -> Should Fail
    assert manager2.save_to_disk() is False

    manager1.cleanup()
    manager2.cleanup()

def test_pre_login_safety(temp_workspace, mock_user_data_dir):
    """Verify that data is NOT saved if lock is not acquired (Pre-Login state)"""
    db_name = "database_documenti.db"
    db_path = temp_workspace / db_name
    create_dummy_db(db_path)

    manager = DBSecurityManager(db_name=db_name)
    manager.load_memory_db()

    # Default state must be Read Only
    assert manager.is_read_only is True

    conn = manager.get_connection()
    conn.execute("INSERT INTO test (data) VALUES ('unsafe_data')")

    # Try to save without lock
    result = manager.save_to_disk()
    assert result is False # Should refuse to save

    # Check that disk file was not modified (timestamp or content)
    # Since it failed, the original Plain DB should remain plain and not include unsafe_data.
    conn_disk = sqlite3.connect(db_path)
    cur_disk = conn_disk.cursor()
    cur_disk.execute("SELECT data FROM test WHERE data='unsafe_data'")
    assert cur_disk.fetchone() is None

def test_stale_lock_recovery(temp_workspace, mock_user_data_dir):
    """
    Verify that if a lock file exists but isn't locked by OS (Stale),
    we can acquire it.
    """
    db_name = "database_documenti.db"
    manager = DBSecurityManager(db_name=db_name)

    # Create a "stale" lock file (Just a file, no OS lock held)
    stale_info = {"user": "zombie_process", "pid": 9999}
    os.makedirs(os.path.dirname(manager.lock_path), exist_ok=True)
    with open(manager.lock_path, "wb") as f:
        f.write(b'\0')
        f.write(json.dumps(stale_info).encode('utf-8'))

    # Now try to acquire
    success, _ = manager.acquire_session_lock({"user": "live_process"})

    assert success is True
    assert manager.is_read_only is False

    # Verify metadata was overwritten
    manager.lock_manager.release()

    # Read file content
    with open(manager.lock_path, "rb") as f:
        f.read(1) # Skip sentinel
        data = json.loads(f.read().decode('utf-8'))
        assert data["user"] == "live_process"
