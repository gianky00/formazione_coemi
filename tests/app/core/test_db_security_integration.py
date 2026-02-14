import sqlite3

import pytest

from app.core.db_security import DBSecurityManager


@pytest.fixture
def secure_db_env(tmp_path):
    db_name = "test_secure.db"
    manager = DBSecurityManager(db_name=db_name)
    # Redirect paths to tmp_path
    manager.data_dir = tmp_path
    manager.db_path = tmp_path / db_name
    manager.lock_path = tmp_path / f".{db_name}.lock"
    # Re-init lock manager with new path
    from app.core.lock_manager import LockManager

    manager.lock_manager = LockManager(str(manager.lock_path))
    return tmp_path, manager, db_name


def test_secure_initialization(secure_db_env):
    _tmp_path, manager, _db_name = secure_db_env
    assert manager.is_read_only is True
    assert manager.is_locked_mode is False


def test_load_and_get_connection(secure_db_env):
    _tmp_path, manager, _db_name = secure_db_env
    manager.load_memory_db()
    conn = manager.get_connection()
    assert isinstance(conn, sqlite3.Connection)
    conn.execute("CREATE TABLE t1 (id int)")
    conn.commit()


def test_lock_acquisition_and_release(secure_db_env):
    _tmp_path, manager, _db_name = secure_db_env

    # Acquire
    success, _info = manager.acquire_session_lock({"user": "admin"})
    assert success is True
    assert manager.lock_path.exists()
    assert manager.has_lock is True

    # Release
    manager.release_lock()
    assert manager.has_lock is False
    assert not manager.lock_path.exists()


def test_integrity_check_plain(secure_db_env):
    _tmp_path, manager, _db_name = secure_db_env
    conn = sqlite3.connect(manager.db_path)
    conn.execute("CREATE TABLE t1 (id int)")
    conn.commit()
    conn.close()

    assert manager.verify_integrity() is True


def test_encryption_toggle(secure_db_env):
    _tmp_path, manager, _db_name = secure_db_env
    manager.load_memory_db()
    manager.acquire_session_lock({"user": "admin"})

    # Initialize connection so save_to_disk has something to save
    manager.get_connection()

    manager.toggle_security_mode(enable_encryption=True)
    assert manager.is_locked_mode is True

    manager.save_to_disk()
    with open(manager.db_path, "rb") as f:
        assert f.read(len(manager._HEADER)) == manager._HEADER

    manager.release_lock()


def test_backup_creation(secure_db_env):
    tmp_path, manager, _db_name = secure_db_env
    # Create DB file
    with open(manager.db_path, "w") as f:
        f.write("data")

    manager.create_backup()
    backup_dir = tmp_path / "Backups"
    assert backup_dir.exists()
    assert len(list(backup_dir.glob("*.bak"))) == 1
