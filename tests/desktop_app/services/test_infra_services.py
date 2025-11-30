import sys
import os
from unittest.mock import MagicMock, patch, mock_open
import pytest
from desktop_app.services import path_service, hardware_id_service, license_updater_service

class TestPathService:
    def test_get_app_install_dir_frozen(self):
        with patch.object(sys, 'frozen', True, create=True):
            with patch.object(sys, 'executable', '/path/to/exe'):
                assert path_service.get_app_install_dir() == '/path/to'

    def test_get_app_install_dir_source(self):
        with patch.object(sys, 'frozen', False, create=True):
            res = path_service.get_app_install_dir()
            # In source mode, it goes up 2 levels from services/
            assert os.path.isabs(res)

    def test_get_user_data_dir_windows(self):
        with patch("os.name", "nt"), patch.dict(os.environ, {"LOCALAPPDATA": "/win/appdata"}):
            with patch("os.makedirs") as mock_mk:
                path = path_service.get_user_data_dir()
                # Use os.path.join logic to verify
                expected = os.path.join("/win/appdata", "Intelleo")
                # Normalize separators for assertion
                assert path.replace("\\", "/") == expected.replace("\\", "/")
                mock_mk.assert_called()

    def test_get_user_data_dir_linux(self):
        with patch("os.name", "posix"), patch("sys.platform", "linux"):
            with patch("os.path.expanduser", return_value="/home/user"), patch("os.makedirs"):
                assert path_service.get_user_data_dir() == "/home/user/.local/share/Intelleo"

class TestHardwareIdService:
    def test_get_machine_id_windows_wmi(self):
        with patch("os.name", "nt"):
            mock_wmi = MagicMock()
            mock_disk = MagicMock()
            mock_disk.DeviceID = "\\\\.\\PHYSICALDRIVE0"
            mock_disk.SerialNumber = " serial.123. "
            mock_wmi.Win32_DiskDrive.return_value = [mock_disk]

            with patch.dict(sys.modules, {"wmi": MagicMock(WMI=MagicMock(return_value=mock_wmi))}):
                # .strip() -> "serial.123." -> .rstrip('.') -> "serial.123"
                assert hardware_id_service.get_machine_id() == "serial.123"

    def test_get_machine_id_fallback_mac(self):
        with patch("os.name", "posix"), patch("uuid.getnode", return_value=0x1234567890AB):
            assert hardware_id_service.get_machine_id() == "12:34:56:78:90:AB"

class TestLicenseUpdaterService:
    @pytest.fixture
    def service(self):
        client = MagicMock()
        return license_updater_service.LicenseUpdaterService(client)

    def test_update_license_no_config(self, service):
        service.api_client.get.side_effect = Exception("Fail")
        success, msg = service.update_license("hwid")
        assert not success
        assert "Impossibile caricare" in msg

    def test_update_license_already_updated(self, service):
        service.config = {"repo_owner": "o", "repo_name": "n", "github_token": "t"}

        # Mock Manifest Response
        with patch("requests.get") as mock_get:
            # First call: Get manifest meta
            meta_resp = MagicMock()
            meta_resp.json.return_value = {"download_url": "url"}

            # Second call: Get manifest content
            content_resp = MagicMock()
            content_resp.json.return_value = {"hash": "123"}

            mock_get.side_effect = [meta_resp, content_resp]

            # Mock local manifest
            with patch("os.path.exists", return_value=True), \
                 patch("builtins.open", mock_open(read_data='{"hash": "123"}')), \
                 patch("json.load", return_value={"hash": "123"}):

                 success, msg = service.update_license("hwid")
                 assert success
                 assert "già aggiornata" in msg
