import pytest
from unittest.mock import patch, MagicMock
import threading
from app.services.notification_service import check_and_send_alerts, _email_lock

def test_race_condition_prevention():
    # Acquire lock manually to simulate running task
    # We use a timeout to avoid hanging if logic is broken
    acquired = _email_lock.acquire(timeout=1)
    assert acquired

    try:
        with patch("app.services.notification_service.get_report_data") as mock_data:
            # Call function
            check_and_send_alerts()

            # Should skip execution because lock is held
            mock_data.assert_not_called()
    finally:
        _email_lock.release()

def test_normal_execution():
    # Ensure lock is free
    if _email_lock.locked():
        _email_lock.release()

    with patch("app.services.notification_service.get_report_data") as mock_data:
        mock_data.return_value = ([], [], [])
        # Mock SessionLocal to avoid DB connection
        with patch("app.services.notification_service.SessionLocal") as MockSession:
             check_and_send_alerts()
             mock_data.assert_called_once()
