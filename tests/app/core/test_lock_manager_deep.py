import os
from unittest.mock import patch

import pytest

from app.core.lock_manager import LockManager


@pytest.fixture
def mock_path(tmp_path):
    return str(tmp_path / ".lock")


def test_acquire_success(mock_path):
    mgr = LockManager(mock_path)
    success, owner = mgr.acquire({"uuid": "test-1"})
    assert success is True
    assert owner is None
    assert os.path.exists(mock_path)
    mgr.release()


def test_acquire_collision(mock_path):
    mgr1 = LockManager(mock_path)
    mgr1.acquire({"uuid": "owner-1", "user": "alice"})

    mgr2 = LockManager(mock_path)
    # This should fail on Windows/Linux due to OS lock
    success, owner = mgr2.acquire({"uuid": "owner-2"})

    assert success is False
    # On Windows owner might be None due to share locks, on Unix it should be alice
    if os.name != "nt":
        assert owner is not None
        assert owner["uuid"] == "owner-1"

    mgr1.release()


def test_acquire_open_failure(mock_path):
    mgr = LockManager(mock_path)
    with patch("builtins.open", side_effect=PermissionError("Locked")):
        success, _owner = mgr.acquire({"uuid": "1"})
        assert success is False


def test_update_heartbeat_success(mock_path):
    mgr = LockManager(mock_path)
    mgr.acquire({"uuid": "1"})
    assert mgr.update_heartbeat() is True
    mgr.release()


def test_release_twice_safe(mock_path):
    mgr = LockManager(mock_path)
    mgr.acquire({"uuid": "1"})
    mgr.release()
    mgr.release()  # Should not raise
