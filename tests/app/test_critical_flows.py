from unittest.mock import MagicMock

from app.core.db_security import db_security
from app.db.models import Certificato


def test_concurrency_lock_failure(setup_security_manager):
    """
    Simulates a scenario where the database lock is held by another process.
    Verifies that the application correctly enters Read-Only mode.
    """
    # 1. Force Lock Failure (Simulate another user holding lock)
    db_security.lock_manager.acquire.return_value = (False, {"user": "another_user", "pid": 999})

    # 2. Attempt to acquire session lock
    success, owner = db_security.acquire_session_lock({"user": "me"})

    # 3. Verify Read-Only Mode enforced
    assert success is False
    assert db_security.is_read_only is True
    assert owner["user"] == "another_user"


def test_save_blocked_in_read_only(setup_security_manager):
    """
    Verifies that save_to_disk() is strictly blocked when in Read-Only mode,
    preventing data corruption or race conditions.
    """
    # 1. Set Read-Only Mode
    db_security.is_read_only = True
    db_security.active_connection = MagicMock()  # Mock connection

    # 2. Attempt Save
    result = db_security.save_to_disk()

    # 3. Verify Blocked
    assert result is False
    # Ensure no serialization attempt occurred
    db_security.active_connection.serialize.assert_not_called()


def test_save_allowed_in_write_mode(setup_security_manager):
    """
    Verifies that save_to_disk() works correctly when Write Access is granted.
    """
    # 1. Set Write Mode
    db_security.is_read_only = False
    db_security.active_connection = MagicMock()
    db_security.active_connection.serialize.return_value = b"serialized_data"

    # 2. Attempt Save
    result = db_security.save_to_disk()

    # 3. Verify Success
    assert result is True
    db_security.active_connection.serialize.assert_called_once()
    # The mocked file system (tmp_path) should now contain the file
    assert db_security.db_path.exists()


def test_upload_does_not_persist(test_client, db_session, mock_ai_service):
    """
    Verifies Data Integrity: The 'Import/Upload' step must be purely analytical.
    No data should be written to the database until the user explicitly saves it via the UI.
    """
    # Mock AI response
    mock_ai_service.return_value = {
        "nome": "ROSSI MARIO",
        "categoria": "ANTINCENDIO",
        "corso": "Corso Antincendio",
        "data_rilascio": "01/01/2024",
        "data_scadenza": "01/01/2029",
    }

    # Pre-count certificates
    initial_count = db_session.query(Certificato).count()

    # Perform Upload
    files = {"file": ("test.pdf", b"%PDF-1.4 fake content", "application/pdf")}
    response = test_client.post("/upload-pdf/", files=files)

    assert response.status_code == 200

    # Post-count certificates
    final_count = db_session.query(Certificato).count()

    # Assert DB remains unchanged
    assert final_count == initial_count
