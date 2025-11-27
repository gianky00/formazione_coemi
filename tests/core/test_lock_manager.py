import os
import pytest
from app.core.lock_manager import LockManager

def test_lock_manager_release_deletes_file(tmp_path):
    lock_file = tmp_path / ".test.lock"
    lock_manager = LockManager(str(lock_file))

    # 1. Acquire
    success, info = lock_manager.acquire({"test": "data"})
    assert success
    assert lock_file.exists()

    # 2. Release
    lock_manager.release()

    # 3. Verify file is gone
    assert not lock_file.exists()

def test_lock_manager_release_handles_missing_file(tmp_path):
    lock_file = tmp_path / ".test_missing.lock"
    lock_manager = LockManager(str(lock_file))

    # 1. Acquire
    success, info = lock_manager.acquire({"test": "data"})
    assert success

    # 2. Delete file externally
    os.remove(lock_file)

    # 3. Release (should not crash)
    lock_manager.release()
