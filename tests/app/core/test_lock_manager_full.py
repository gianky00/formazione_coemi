import pytest
from unittest.mock import MagicMock, patch, mock_open
import json
import os
import time
from app.core.lock_manager import LockManager

@pytest.fixture
def mock_path(tmp_path):
    return str(tmp_path / ".lock")

def test_acquire_success(mock_path):
    mgr = LockManager(mock_path)
    metadata = {"uuid": "123", "pid": 100}

    with patch("fcntl.flock") as mock_flock:
        success, owner = mgr.acquire(metadata)
        assert success is True
        assert owner is None
        mock_flock.assert_called()

    assert os.path.exists(mock_path)
    with open(mock_path, "rb") as f:
        f.seek(1)
        data = json.loads(f.read().decode())
        assert data["uuid"] == "123"

    mgr.release()

def test_acquire_failure_locked(mock_path):
    mgr = LockManager(mock_path)
    metadata = {"uuid": "123"}

    # Pre-create lock file with other owner
    with open(mock_path, "wb") as f:
        f.write(b'\0')
        f.write(json.dumps({"uuid": "OTHER", "pid": 999}).encode())

    with patch("fcntl.flock", side_effect=BlockingIOError("Locked")):
        # Mock time.sleep to speed up retries
        with patch("time.sleep"):
            success, owner = mgr.acquire(metadata, retries=1)

    assert success is False
    assert owner["uuid"] == "OTHER"

def test_update_heartbeat_success(mock_path):
    mgr = LockManager(mock_path)
    metadata = {"uuid": "123", "pid": 100}

    # Acquire first
    with patch("fcntl.flock"):
        mgr.acquire(metadata)

    # Update
    assert mgr.update_heartbeat() is True

    # Check new timestamp
    with open(mock_path, "rb") as f:
        f.seek(1)
        data = json.loads(f.read().decode())
        assert "timestamp" in data

def test_update_heartbeat_split_brain(mock_path):
    mgr = LockManager(mock_path)
    metadata = {"uuid": "123", "pid": 100}

    # Acquire
    with patch("fcntl.flock"):
        mgr.acquire(metadata)

    # Simulate another process overwriting the file
    with open(mock_path, "wb") as f:
        f.write(b'\0')
        f.write(json.dumps({"uuid": "EVIL_TWIN"}).encode())

    # Update should fail
    assert mgr.update_heartbeat() is False

def test_update_heartbeat_not_locked(mock_path):
    mgr = LockManager(mock_path)
    assert mgr.update_heartbeat() is False

def test_release_removes_file(mock_path):
    mgr = LockManager(mock_path)
    with patch("fcntl.flock"):
        mgr.acquire({"uuid": "123"})

    assert os.path.exists(mock_path)
    mgr.release()
    assert not os.path.exists(mock_path)

def test_write_metadata_failure(mock_path):
    mgr = LockManager(mock_path)
    # Simulate valid lock handle
    mgr._lock_handle = MagicMock()

    with patch.object(mgr._lock_handle, "write", side_effect=Exception("Write Fail")):
        with pytest.raises(Exception, match="Write Fail"):
            mgr._write_metadata({})

def test_read_metadata_corrupt_json(mock_path):
    mgr = LockManager(mock_path)
    # Write garbage
    with open(mock_path, "wb") as f:
        f.write(b'\0') # Byte 0
        f.write(b'{bad') # Byte 1

    # We need handle to read
    mgr._lock_handle = open(mock_path, "rb")
    data = mgr._read_metadata()
    mgr._lock_handle.close()

    assert "Corrupt Metadata" in data["status"]

def test_release_handle_close_error(mock_path):
    mgr = LockManager(mock_path)
    mgr._lock_handle = MagicMock()
    mgr._lock_handle.close.side_effect = Exception("Close Fail")

    # Should log error but not crash
    mgr.release()
    assert mgr._lock_handle is None

def test_acquire_retry_logic(mock_path):
    mgr = LockManager(mock_path)
    # Fail locking
    with patch("fcntl.flock", side_effect=BlockingIOError), \
         patch("time.sleep") as mock_sleep:

         mgr.acquire({"uuid": "1"}, retries=2, delay=0.1)
         assert mock_sleep.call_count == 2

def test_acquire_read_metadata_fail(mock_path):
    mgr = LockManager(mock_path)
    # Create empty lock file
    with open(mock_path, "wb") as f: f.write(b'\0')

    with patch("fcntl.flock", side_effect=BlockingIOError):
        with patch.object(mgr, "_read_metadata", side_effect=Exception("Read Fail")):
             success, owner = mgr.acquire({"uuid": "1"}, retries=0)

    assert success is False
    assert "Unknown" in owner["error"]
