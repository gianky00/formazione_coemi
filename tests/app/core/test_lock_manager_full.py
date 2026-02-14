import json
import os
from unittest.mock import patch

import pytest

from app.core.lock_manager import LockManager


@pytest.fixture
def mock_path(tmp_path):
    return str(tmp_path / ".lock")


@pytest.fixture
def mock_lock_failure():
    """Mock OS-level lock failure."""
    if os.name == "nt":
        return patch("msvcrt.locking", side_effect=OSError("Locked"))
    else:
        return patch("fcntl.flock", side_effect=OSError("Locked"))


def test_acquire_success(mock_path):
    mgr = LockManager(mock_path)
    success, _ = mgr.acquire({"uuid": "123"})
    assert success is True
    mgr.release()


def test_acquire_failure_locked(mock_path, mock_lock_failure):
    mgr = LockManager(mock_path)
    # Pre-create lock file with other owner
    with open(mock_path, "wb") as f:
        f.write(b"\x01")
        f.write(json.dumps({"uuid": "OTHER"}).encode())

    with mock_lock_failure:
        success, owner = mgr.acquire({"uuid": "ME"})
        assert success is False
        if os.name != "nt":  # On Unix we should be able to read
            assert owner["uuid"] == "OTHER"


def test_update_heartbeat_no_handle(mock_path):
    mgr = LockManager(mock_path)
    assert mgr.update_heartbeat() is False


def test_update_heartbeat_success(mock_path):
    mgr = LockManager(mock_path)
    mgr.acquire({"uuid": "123"})
    assert mgr.update_heartbeat() is True
    mgr.release()


def test_read_existing_metadata_success(mock_path):
    mgr = LockManager(mock_path)
    mgr.acquire({"uuid": "123", "user": "test"})

    # Read from another instance
    mgr2 = LockManager(mock_path)
    meta = mgr2._read_existing_metadata()
    if os.name != "nt":  # Read while locked might fail on Windows
        assert meta is not None
        assert meta["uuid"] == "123"

    mgr.release()


def test_read_existing_metadata_corrupt(mock_path):
    mgr = LockManager(mock_path)
    with open(mock_path, "wb") as f:
        f.write(b"\x01")
        f.write(b"{invalid")

    assert mgr._read_existing_metadata() is None


def test_release_cleanup(mock_path):
    mgr = LockManager(mock_path)
    mgr.acquire({"uuid": "1"})
    assert os.path.exists(mock_path)
    mgr.release()
    assert not os.path.exists(mock_path)
