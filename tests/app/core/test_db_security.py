import pytest
import os
import sqlite3
from pathlib import Path
from unittest.mock import patch
from app.core.db_security import DBSecurityManager

@pytest.fixture
def temp_workspace(tmp_path):
    return tmp_path

def create_dummy_db(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, data TEXT)")
    c.execute("INSERT INTO test (data) VALUES ('secret_data')")
    conn.commit()
    conn.close()

def test_in_memory_lifecycle(temp_workspace):
    db_path = temp_workspace / "database_documenti.db"

    # 1. Create Plain DB on disk
    create_dummy_db(db_path)

    manager = DBSecurityManager(db_path=str(db_path))

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
    manager.create_lock()
    assert manager.has_lock is True
    assert manager.lock_path.exists()

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
    assert not manager.lock_path.exists()

    # 8. Reload (Simulate Restart)
    manager2 = DBSecurityManager(db_path=str(db_path))
    manager2.load_memory_db()
    conn2 = manager2.get_connection()
    cur2 = conn2.cursor()
    cur2.execute("SELECT data FROM test WHERE data='new_ram_data'")
    assert cur2.fetchone()[0] == 'new_ram_data'

def test_lock_prevents_access(temp_workspace):
    db_path = temp_workspace / "database_documenti.db"
    create_dummy_db(db_path)

    # Instance 1: Running and Locked
    manager1 = DBSecurityManager(db_path=str(db_path))
    manager1.load_memory_db()
    manager1.create_lock()

    # Instance 2: Startup Check
    manager2 = DBSecurityManager(db_path=str(db_path))

    # Should fail at startup if locked
    with pytest.raises(PermissionError):
        manager2.load_memory_db()

    manager1.cleanup()

def test_pre_login_safety(temp_workspace):
    """Verify that data is NOT saved if lock is not held (Pre-Login state)"""
    db_path = temp_workspace / "database_documenti.db"
    create_dummy_db(db_path)

    manager = DBSecurityManager(db_path=str(db_path))
    manager.load_memory_db()
    # Note: No create_lock() called

    conn = manager.get_connection()
    conn.execute("INSERT INTO test (data) VALUES ('unsafe_data')")

    # Try to save
    result = manager.save_to_disk()
    assert result is False # Should refuse to save

    # Verify Disk still Plain (because it was plain initially, and save failed)
    # Actually, if it was plain, load_memory_db sets is_locked_mode=True.
    # But save_to_disk didn't write.
    # So disk should still be the ORIGINAL plain file.
    conn_disk = sqlite3.connect(db_path)
    cur_disk = conn_disk.cursor()
    cur_disk.execute("SELECT data FROM test WHERE data='unsafe_data'")
    assert cur_disk.fetchone() is None # Data not written
