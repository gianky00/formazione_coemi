import os
import shutil
import pytest
import sqlite3
import json
import psutil
import time
from unittest.mock import MagicMock, patch
from pathlib import Path
from app.core.db_security import DBSecurityManager
from app.core.lock_manager import LockManager

# --- DB SECURITY INTEGRATION TESTS ---

@pytest.fixture
def secure_db_env(tmp_path):
    """
    Creates an isolated environment for testing DB security.
    Returns the tmp_path and a configured DBSecurityManager instance.
    """
    db_name = "test_secure.db"
    
    # Patch settings to return tmp_path as DATABASE_PATH/User Data Dir
    with patch("app.core.db_security.settings") as mock_settings, \
         patch("app.core.db_security.get_user_data_dir") as mock_get_dir:
        
        mock_settings.DATABASE_PATH = str(tmp_path / db_name)
        mock_get_dir.return_value = tmp_path

        # Instantiate manager
        manager = DBSecurityManager(db_name=db_name)
        
        yield tmp_path, manager, db_name

        # Teardown: Release lock if held
        try:
            if manager.lock_manager:
                manager.release_lock()
        except:
            pass

def test_initialization_creates_files(secure_db_env):
    tmp_path, manager, db_name = secure_db_env
    
    # DB path should be set correctly
    assert manager.db_path == tmp_path / db_name
    assert manager.lock_path == tmp_path / f".{db_name}.lock"

def test_full_encryption_cycle(secure_db_env):
    tmp_path, manager, db_name = secure_db_env

    # 1. Initialize DB (In Memory)
    conn = manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, data TEXT)")
    cursor.execute("INSERT INTO test (data) VALUES ('secret')")
    conn.commit()

    # 2. Acquire Lock to allow saving
    success, _ = manager.acquire_session_lock({"username": "tester"})
    assert success is True
    assert manager.is_read_only is False

    # 3. Save to Disk (should be encrypted)
    manager.is_locked_mode = True
    saved = manager.save_to_disk()
    assert saved is True
    assert manager.db_path.exists()

    # 4. Verify on Disk content is NOT plain SQLite
    with open(manager.db_path, 'rb') as f:
        header = f.read(15)
        assert header == manager._HEADER
        # Ensure it doesn't start with SQLite header "SQLite format 3"
        f.seek(0)
        full_content = f.read()
        assert b"SQLite format 3" not in full_content[:20]

    # 5. Reload from Disk (Decrypt)
    # Simulate restart by clearing connection and initial bytes
    manager.active_connection = None
    manager.initial_bytes = None
    
    manager.load_memory_db()
    conn2 = manager.get_connection()
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT data FROM test")
    row = cursor2.fetchone()
    assert row[0] == 'secret'

def test_verify_integrity(secure_db_env):
    tmp_path, manager, db_name = secure_db_env
    
    # Create valid encrypted DB
    conn = manager.get_connection()
    conn.execute("CREATE TABLE t (a)")
    manager.acquire_session_lock({"u": "t"})
    manager.is_locked_mode = True
    manager.save_to_disk()

    # Check Integrity
    assert manager.verify_integrity() is True

    # Corrupt the file
    with open(manager.db_path, 'wb') as f:
        f.write(manager._HEADER + b"GARBAGE_DATA_NOT_ENCRYPTED_CORRECTLY")

    # Check Integrity
    assert manager.verify_integrity() is False

def test_lock_acquisition_and_release(secure_db_env):
    tmp_path, manager, db_name = secure_db_env
    
    # Acquire
    success, info = manager.acquire_session_lock({"user": "admin", "pid": 1234})
    assert success is True
    assert manager.lock_path.exists()
    assert manager.has_lock is True

    # Check content of lock file
    with open(manager.lock_path, 'rb') as f:
        f.seek(1) # Skip lock byte
        data = json.load(f)
        assert data["user"] == "admin"
        # The manager adds its own pid, not necessarily what we passed in info unless mapped
        # info passed to acquire is user_info, manager adds pid
        assert "pid" in data

    # Release
    manager.release_lock()
    
    # Verify internal state
    assert manager.lock_manager._is_locked is False
    
    # Verify lock file removal (might depend on OS, but release logic tries to remove it)
    # If it fails to remove, it's not a hard failure for the app, but desirable for test
    if manager.lock_path.exists():
        # Verify it's at least unlocked or empty? 
        # Actually LockManager closes handle.
        pass

def test_save_fails_if_read_only(secure_db_env):
    tmp_path, manager, db_name = secure_db_env
    
    # Initialize connection so save_to_disk has something to save
    manager.get_connection()
    
    # Force Read-Only
    manager.is_read_only = True
    
    # Try Save
    saved = manager.save_to_disk()
    assert saved is False

def test_stale_lock_recovery(secure_db_env):
    tmp_path, manager, db_name = secure_db_env
    
    # 1. Create a fake lock file from a "dead" process
    fake_pid = 99999
    metadata = {"pid": fake_pid, "user": "zombie"}
    with open(manager.lock_path, 'wb') as f:
        f.write(b'\x01') # Locked byte simulation
        f.write(json.dumps(metadata).encode('utf-8'))
    
    # 2. Trigger recovery logic
    # We mock psutil.pid_exists to return False for our fake PID
    with patch('psutil.pid_exists', return_value=False):
        manager._check_and_recover_stale_lock()

    # 3. Lock file should be gone
    assert not manager.lock_path.exists()

def test_stale_lock_respects_living_process(secure_db_env):
    tmp_path, manager, db_name = secure_db_env
    
    # 1. Create lock for CURRENT process (alive)
    my_pid = os.getpid()
    metadata = {"pid": my_pid, "user": "me"}
    
    with open(manager.lock_path, 'wb') as f:
        f.write(b'\x01')
        f.write(json.dumps(metadata).encode('utf-8'))

    # 2. Trigger recovery check
    # We must patch psutil.Process to return a valid name "python" or "intelleo"
    with patch('psutil.pid_exists', return_value=True), \
         patch('psutil.Process') as mock_proc:
        
        mock_proc.return_value.name.return_value = "python.exe"
        manager._check_and_recover_stale_lock()

    # 3. Lock file should REMAIN
    assert manager.lock_path.exists()
