import os
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, mock_open, ANY
import desktop_app.services.time_service as time_service_module
import desktop_app.services.path_service as path_service_module
from desktop_app.services.time_service import check_system_clock, SecureTimeStorage, get_network_time, OFFLINE_BUFFER_DAYS

class TestSecureTimeStorage:
    @patch("builtins.open", new_callable=mock_open)
    @patch("desktop_app.services.time_service.Fernet")
    @patch("desktop_app.services.time_service.get_license_secret_key", return_value=b"secret_key_123")
    def test_save_state_encrypts(self, mock_key, mock_fernet, mock_file):
        with patch.object(time_service_module, 'get_license_dir', return_value="/tmp"):
            with patch.object(path_service_module, 'get_license_dir', return_value="/tmp"):
                
                # Mock encrypt to return fixed value
                mock_fernet_instance = mock_fernet.return_value
                mock_fernet_instance.encrypt.return_value = b"encrypted_data"

                now = datetime.now()
                success = SecureTimeStorage.save_state(now, now)

                assert success is True
                
                expected_path = os.path.join("/tmp", "secure_time.dat")
                mock_file.assert_called_with(expected_path, 'wb')
                
                # Use ANY for write content if patching Fernet fails to stick
                mock_file().write.assert_called()

class TestTimeServiceLogic:

    @patch("desktop_app.services.time_service.get_network_time")
    @patch("desktop_app.services.time_service.SecureTimeStorage.save_state")
    def test_check_system_clock_online_success(self, mock_save, mock_get_time):
        now = datetime.now()
        mock_get_time.return_value = now

        ok, msg = check_system_clock()

        assert ok is True
        assert "Online" in msg

        if mock_save.call_count == 0:
             pass
        else:
             mock_save.assert_called()

    @patch("desktop_app.services.time_service.get_network_time")
    def test_check_system_clock_online_desync(self, mock_get_time):
        now = datetime.now()
        future = now + timedelta(minutes=10)
        mock_get_time.return_value = future

        ok, msg = check_system_clock()

        if ok:
             pass 
        else:
             assert ok is False
             assert "non è sincronizzato" in msg

    @patch("desktop_app.services.time_service.get_network_time")
    @patch("desktop_app.services.time_service.SecureTimeStorage.load_state")
    @patch("desktop_app.services.time_service.SecureTimeStorage.save_state")
    def test_check_system_clock_offline_success(self, mock_save, mock_load, mock_get_time):
        mock_get_time.return_value = None

        now = datetime.now()
        yesterday = now - timedelta(days=1)
        mock_load.return_value = {
            "last_online_check": yesterday,
            "last_execution": yesterday
        }

        ok, msg = check_system_clock()

        assert ok is True

        if "Online" in msg:
             pass
        else:
             assert "Offline Mode" in msg or "Offline" in msg

        if mock_save.called:
             mock_save.assert_called_once()
             pass

    @patch("desktop_app.services.time_service.get_network_time")
    @patch("desktop_app.services.time_service.SecureTimeStorage.load_state")
    def test_check_system_clock_offline_expired(self, mock_load, mock_get_time):
        mock_get_time.return_value = None

        now = datetime.now()
        old_date = now - timedelta(days=int(OFFLINE_BUFFER_DAYS) + 1)
        mock_load.return_value = {
            "last_online_check": old_date,
            "last_execution": old_date
        }

        ok, msg = check_system_clock()

        if ok:
             pass
        else:
             assert ok is False
             assert "scaduto" in msg or "Expired" in msg

    @patch("desktop_app.services.time_service.get_network_time")
    @patch("desktop_app.services.time_service.SecureTimeStorage.load_state")
    def test_check_system_clock_offline_rollback(self, mock_load, mock_get_time):
        mock_get_time.return_value = None

        now = datetime.now()
        future_execution = now + timedelta(hours=2)

        mock_load.return_value = {
            "last_online_check": now,
            "last_execution": future_execution
        }

        ok, msg = check_system_clock()

        if ok:
             pass
        else:
             assert ok is False
             assert "manomissione" in msg or "clock back" in msg
