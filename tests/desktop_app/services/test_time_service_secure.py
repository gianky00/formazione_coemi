import os
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, mock_open
from desktop_app.services.time_service import check_system_clock, SecureTimeStorage, get_network_time, OFFLINE_BUFFER_DAYS

class TestSecureTimeStorage:
    @patch("builtins.open", new_callable=mock_open)
    @patch("desktop_app.services.time_service.get_license_dir")
    @patch("desktop_app.services.time_service.Fernet")
    @patch("desktop_app.services.time_service.get_license_secret_key", return_value=b"secret_key_123")
    def test_save_state_encrypts(self, mock_key, mock_fernet, mock_dir, mock_file):
        mock_dir.return_value = "/tmp"
        mock_fernet_instance = mock_fernet.return_value
        mock_fernet_instance.encrypt.return_value = b"encrypted_data"

        now = datetime.now()
        success = SecureTimeStorage.save_state(now, now)

        assert success is True
        mock_file.assert_called_with(os.path.join("/tmp", "secure_time.dat"), 'wb')
        mock_file().write.assert_called_with(b"encrypted_data")

class TestTimeServiceLogic:

    @patch("desktop_app.services.time_service.get_network_time")
    @patch("desktop_app.services.time_service.SecureTimeStorage.save_state")
    def test_check_system_clock_online_success(self, mock_save, mock_get_time):
        # Setup: Online, synced
        now = datetime.now()
        mock_get_time.return_value = now

        ok, msg = check_system_clock()

        assert ok is True
        assert "Online" in msg
        mock_save.assert_called() # Should save state

    @patch("desktop_app.services.time_service.get_network_time")
    def test_check_system_clock_online_desync(self, mock_get_time):
        # Setup: Online, but 10 mins ahead
        now = datetime.now()
        future = now + timedelta(minutes=10)
        mock_get_time.return_value = future

        ok, msg = check_system_clock()

        assert ok is False
        assert "non è sincronizzato" in msg

    @patch("desktop_app.services.time_service.get_network_time")
    @patch("desktop_app.services.time_service.SecureTimeStorage.load_state")
    @patch("desktop_app.services.time_service.SecureTimeStorage.save_state")
    def test_check_system_clock_offline_success(self, mock_save, mock_load, mock_get_time):
        # Setup: Offline
        mock_get_time.return_value = None

        # Valid state: Check was yesterday, last exec was yesterday
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        mock_load.return_value = {
            "last_online_check": yesterday,
            "last_execution": yesterday
        }

        ok, msg = check_system_clock()

        assert ok is True
        assert "Offline Mode" in msg
        # Should update last_execution to NOW, but keep last_online_check as YESTERDAY

        # Manually check arguments because datetime.now() inside function is slightly different
        mock_save.assert_called_once()
        _, kwargs = mock_save.call_args
        assert kwargs['last_online_check'] == yesterday
        # Allow 1 second difference
        assert abs((kwargs['last_execution'] - now).total_seconds()) < 1

    @patch("desktop_app.services.time_service.get_network_time")
    @patch("desktop_app.services.time_service.SecureTimeStorage.load_state")
    def test_check_system_clock_offline_expired(self, mock_load, mock_get_time):
        # Setup: Offline
        mock_get_time.return_value = None

        # Expired state: Check was 5 days ago (Limit is 3)
        now = datetime.now()
        old_date = now - timedelta(days=OFFLINE_BUFFER_DAYS + 1)
        mock_load.return_value = {
            "last_online_check": old_date,
            "last_execution": old_date
        }

        ok, msg = check_system_clock()

        assert ok is False
        assert "scaduto" in msg

    @patch("desktop_app.services.time_service.get_network_time")
    @patch("desktop_app.services.time_service.SecureTimeStorage.load_state")
    def test_check_system_clock_offline_rollback(self, mock_load, mock_get_time):
        # Setup: Offline
        mock_get_time.return_value = None

        # Rollback detected: System says today, but last execution was TOMORROW (user moved clock back)
        now = datetime.now()
        future_execution = now + timedelta(hours=2)

        mock_load.return_value = {
            "last_online_check": now,
            "last_execution": future_execution
        }

        ok, msg = check_system_clock()

        assert ok is False
        assert "manomissione" in msg
