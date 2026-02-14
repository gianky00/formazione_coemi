import os

from app.core.lock_manager import LockManager


def test_lock_manager_release_deletes_file(tmp_path):
    lock_file = tmp_path / ".lock"
    mgr = LockManager(str(lock_file))
    mgr.acquire({"test": "data"})
    assert lock_file.exists()
    mgr.release()
    assert not lock_file.exists()


def test_lock_manager_release_handles_missing_file(tmp_path):
    lock_file = tmp_path / ".lock"
    mgr = LockManager(str(lock_file))
    mgr.acquire({"test": "data"})

    # On Windows we must close handle before removing
    if mgr._lock_handle:
        mgr._lock_handle.close()
        mgr._lock_handle = None

    if lock_file.exists():
        os.remove(str(lock_file))
    mgr.release()  # Should not raise


def test_lock_manager_acquire_already_locked(tmp_path):
    lock_file = tmp_path / ".lock"
    mgr1 = LockManager(str(lock_file))
    mgr1.acquire({"id": "1"})

    mgr2 = LockManager(str(lock_file))
    success, _ = mgr2.acquire({"id": "2"})
    assert success is False
    mgr1.release()
