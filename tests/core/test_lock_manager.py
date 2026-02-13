from app.core.lock_manager import LockManager


def test_lock_manager_release_deletes_file(tmp_path, mocker):
    mocker.patch.object(LockManager, "_lock_byte_0")
    lock_file = tmp_path / ".test.lock"
    lock_manager = LockManager(str(lock_file))

    # 1. Acquire
    success, info = lock_manager.acquire({"test": "data"})
    assert success
    # In mock env we didn't actually lock byte, but file is open
    assert lock_file.exists()

    # 2. Release
    lock_manager.release()

    # 3. Verify file is gone
    assert not lock_file.exists()


def test_lock_manager_release_handles_missing_file(tmp_path, mocker):
    mocker.patch.object(LockManager, "_lock_byte_0")

    # Simulate file missing during release check
    mocker.patch("os.path.exists", return_value=False)
    mock_remove = mocker.patch("os.remove")

    lock_file = tmp_path / ".test_missing.lock"
    lock_manager = LockManager(str(lock_file))

    # 1. Acquire
    success, info = lock_manager.acquire({"test": "data"})
    assert success

    # 2. Release (should not crash and not call remove)
    lock_manager.release()

    mock_remove.assert_not_called()
    assert lock_manager._lock_handle is None


def test_lock_manager_release_handles_remove_error(tmp_path, mocker):
    mocker.patch.object(LockManager, "_lock_byte_0")
    # Simulate OS error on removal (e.g. race condition)
    mock_remove = mocker.patch("os.remove")
    mock_remove.side_effect = OSError("Access Denied")

    lock_file = tmp_path / ".test_error.lock"
    lock_manager = LockManager(str(lock_file))
    lock_manager.acquire({})

    # Release should catch the error and not crash
    lock_manager.release()
    assert lock_manager._lock_handle is None
