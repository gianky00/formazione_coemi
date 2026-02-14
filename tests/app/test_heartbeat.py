import json
import time

from app.core.db_security import db_security
from app.core.lock_manager import LockManager


def test_heartbeat_mechanism(mocker, tmp_path):
    # Mock LockManager for isolation
    lock_file = tmp_path / ".test_heartbeat.lock"
    db_security.lock_path = lock_file
    db_security.lock_manager = LockManager(str(lock_file))

    # 1. Acquire Lock
    success, _ = db_security.acquire_session_lock({"user": "test"})
    assert success
    assert not db_security.is_read_only

    # Verify heartbeat timer started
    assert db_security._heartbeat_timer is not None

    db_security.force_read_only_mode()
    assert db_security.is_read_only
    assert db_security._heartbeat_timer is None  # Should be cancelled


def test_lock_manager_heartbeat(tmp_path):
    lock_file = tmp_path / ".heartbeat.lock"
    lm = LockManager(str(lock_file))

    # Acquire
    success, _ = lm.acquire({"test": "data", "uuid": "123"})
    assert success

    # Initial timestamp
    with open(lock_file, "rb") as f:
        f.seek(1)
        data = json.loads(f.read().decode("utf-8"))
        ts1 = data.get("timestamp")

    time.sleep(0.1)

    # Update Heartbeat
    res = lm.update_heartbeat()
    assert res

    # Verify timestamp changed
    with open(lock_file, "rb") as f:
        f.seek(1)
        data = json.loads(f.read().decode("utf-8"))
        ts2 = data.get("timestamp")

    assert ts2 > ts1 if ts1 else True

    # Release
    lm.release()


def test_lock_manager_release_cleanup(tmp_path):
    lock_file = tmp_path / ".release.lock"
    lm = LockManager(str(lock_file))
    lm.acquire({"test": "data"})
    assert lock_file.exists()

    lm.release()
    assert not lock_file.exists()


def test_heartbeat_failure_no_handle(tmp_path):
    lock_file = tmp_path / ".no_handle.lock"
    lm = LockManager(str(lock_file))
    # Not acquired
    assert lm.update_heartbeat() is False


def test_read_existing_metadata(tmp_path):
    lock_file = tmp_path / ".metadata.lock"
    lm = LockManager(str(lock_file))
    meta = {"uuid": "test-uuid", "user": "test-user"}
    lm.acquire(meta)

    # Another manager (or same) reads metadata without lock
    lm2 = LockManager(str(lock_file))
    read_meta = lm2._read_existing_metadata()
    assert read_meta is not None
    assert read_meta["uuid"] == "test-uuid"
    assert read_meta["user"] == "test-user"

    lm.release()
