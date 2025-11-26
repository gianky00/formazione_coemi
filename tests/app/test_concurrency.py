import os
import time
import pytest
from unittest.mock import patch, MagicMock
from app.core.lock_manager import LockManager
from app.core.db_security import DBSecurityManager

# Use a consistent path for the test lock file
TEST_DB_NAME = "test_concurrency.db"
TEST_DATA_DIR = os.path.join(os.getcwd(), "test_data")
TEST_DB_PATH = os.path.join(TEST_DATA_DIR, TEST_DB_NAME)
TEST_LOCK_PATH = os.path.join(TEST_DATA_DIR, f".{TEST_DB_NAME}.lock")

@pytest.fixture(scope="function")
def cleanup_files():
    """Fixture to ensure test files are removed before and after each test."""
    if os.path.exists(TEST_LOCK_PATH):
        os.remove(TEST_LOCK_PATH)
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    if not os.path.exists(TEST_DATA_DIR):
        os.makedirs(TEST_DATA_DIR)
    yield
    if os.path.exists(TEST_LOCK_PATH):
        os.remove(TEST_LOCK_PATH)
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

def test_lock_manager_acquire_release(cleanup_files):
    """Test basic lock acquisition and release."""
    lock_manager = LockManager(TEST_LOCK_PATH)

    # First acquisition should succeed
    success, owner_info = lock_manager.acquire({"user": "test_user", "pid": 123})
    assert success is True
    assert owner_info is None
    assert lock_manager._is_locked is True

    # Release the lock
    lock_manager.release()
    assert lock_manager._is_locked is False

def test_lock_manager_second_process_fails(cleanup_files):
    """Test that a second process fails to acquire the lock and gets owner info."""
    lm1 = LockManager(TEST_LOCK_PATH)
    lm2 = LockManager(TEST_LOCK_PATH)

    # Process 1 acquires the lock
    pid1 = 12345
    user1 = "user_one"
    success1, _ = lm1.acquire({"user": user1, "pid": pid1})
    assert success1 is True

    # Process 2 attempts to acquire the lock and should fail
    pid2 = 54321
    user2 = "user_two"
    success2, owner_info2 = lm2.acquire({"user": user2, "pid": pid2})

    assert success2 is False
    assert owner_info2 is not None
    assert owner_info2["pid"] == pid1
    assert owner_info2["user"] == user1

    # Cleanup
    lm1.release()

@patch("os.getpid")
def test_db_manager_concurrency_fallback_to_readonly(mock_getpid, cleanup_files):
    """
    Simulates two DBSecurityManager instances trying to acquire a lock.
    The first gets it, the second should fall back to read-only mode.
    """
    # === Process 1: The Winner ===
    mock_getpid.return_value = 1111
    db_manager1 = DBSecurityManager(db_name=TEST_DB_NAME)
    # Force the data_dir to our test directory
    db_manager1.data_dir = TEST_DATA_DIR
    db_manager1.db_path = TEST_DB_PATH
    db_manager1.lock_path = TEST_LOCK_PATH
    db_manager1.lock_manager = LockManager(TEST_LOCK_PATH)

    # Process 1 acquires the lock
    success1, _ = db_manager1.acquire_session_lock({"user": "winner"})
    assert success1 is True
    assert db_manager1.is_read_only is False
    assert db_manager1.read_only_info is None

    # === Process 2: The Contender ===
    mock_getpid.return_value = 2222
    db_manager2 = DBSecurityManager(db_name=TEST_DB_NAME)
    # Force the data_dir to our test directory
    db_manager2.data_dir = TEST_DATA_DIR
    db_manager2.db_path = TEST_DB_PATH
    db_manager2.lock_path = TEST_LOCK_PATH
    db_manager2.lock_manager = LockManager(TEST_LOCK_PATH)

    # Process 2 attempts to acquire and should be forced into read-only
    success2, owner_info2 = db_manager2.acquire_session_lock({"user": "contender"})

    assert success2 is False
    assert db_manager2.is_read_only is True
    assert db_manager2.read_only_info is not None
    assert db_manager2.read_only_info["pid"] == 1111
    assert db_manager2.read_only_info["user"] == "winner"

    # Verify that the read-only instance cannot save
    # We need to give it a connection to test this
    db_manager2.active_connection = MagicMock()
    save_result = db_manager2.save_to_disk()
    assert save_result is False
    db_manager2.active_connection.serialize.assert_not_called()

    # Cleanup: The original lock owner releases the lock
    db_manager1.release_lock()
