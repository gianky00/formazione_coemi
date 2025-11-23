import pytest
import os
import sqlite3
from pathlib import Path
from app.core.db_security import DBSecurityManager

@pytest.fixture
def temp_workspace(tmp_path):
    # Setup a clean workspace
    db_path = tmp_path / "test_db.db"
    return db_path

def create_dummy_db(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, data TEXT)")
    c.execute("INSERT INTO test (data) VALUES ('secret_data')")
    conn.commit()
    conn.close()

def test_security_manager_lifecycle(temp_workspace):
    db_path = temp_workspace

    # 1. Create Plain DB
    create_dummy_db(db_path)

    # 2. Init Manager
    manager = DBSecurityManager(db_path=str(db_path))

    # 3. Test Initialize (Should detect plain and copy to temp)
    temp_conn_str = manager.initialize_db()

    assert manager.is_locked_mode is False
    assert manager.temp_path.exists()
    assert manager.lock_path.exists()

    # Verify we can read temp
    temp_conn = sqlite3.connect(manager.temp_path)
    cursor = temp_conn.cursor()
    cursor.execute("SELECT data FROM test")
    assert cursor.fetchone()[0] == 'secret_data'
    temp_conn.close()

    # 4. Toggle to Locked (Encryption)
    manager.toggle_security_mode(True)
    assert manager.is_locked_mode is True

    # Verify Main file is now Encrypted (Header check)
    with open(db_path, "rb") as f:
        header = f.read(len(manager._HEADER))
        assert header == manager._HEADER

    # Verify Main file is NOT valid sqlite
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM test")
        assert False, "Should have raised DatabaseError"
    except sqlite3.DatabaseError:
        pass
    except Exception:
        pass

    # 5. Modify Temp and Sync
    temp_conn = sqlite3.connect(manager.temp_path)
    temp_conn.execute("INSERT INTO test (data) VALUES ('new_data')")
    temp_conn.commit()
    temp_conn.close()

    manager.sync_db()

    # 6. Cleanup (Simulate Shutdown)
    manager.cleanup()
    assert not manager.temp_path.exists()
    assert not manager.lock_path.exists()

    # 7. Restart in Locked Mode
    manager2 = DBSecurityManager(db_path=str(db_path))
    assert manager2.is_encrypted() is True

    manager2.initialize_db()
    assert manager2.is_locked_mode is True
    assert manager2.temp_path.exists()

    # Verify Data Persisted
    temp_conn = sqlite3.connect(manager2.temp_path)
    cursor = temp_conn.cursor()
    cursor.execute("SELECT data FROM test WHERE data='new_data'")
    assert cursor.fetchone()[0] == 'new_data'
    temp_conn.close()

    manager2.cleanup()

def test_locking_mechanism(temp_workspace):
    db_path = temp_workspace
    create_dummy_db(db_path)

    manager1 = DBSecurityManager(db_path=str(db_path))
    manager1.initialize_db()

    manager2 = DBSecurityManager(db_path=str(db_path))

    with pytest.raises(PermissionError):
        manager2.initialize_db()

    manager1.cleanup()
