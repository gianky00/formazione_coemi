import sys
import pytest
from unittest.mock import MagicMock, patch, mock_open
from datetime import datetime, timedelta

# Mock modules needed for LicenseManager imports
from tests.desktop_app.mock_qt import mock_modules

class TestLicenseManagerFull:
    def test_get_license_data_found_user_dir(self):
        with patch.dict(sys.modules, mock_modules):
            from desktop_app.services.license_manager import LicenseManager

            with patch("desktop_app.services.license_manager.get_license_dir", return_value="/user/lic"), \
                 patch("os.path.exists") as mock_exists, \
                 patch("builtins.open", mock_open(read_data=b"encrypted")) as mock_file, \
                 patch("desktop_app.services.license_manager.Fernet") as MockFernet, \
                 patch("desktop_app.services.license_manager.get_license_secret_key", return_value=b"key"):

                 mock_exists.return_value = True
                 MockFernet.return_value.decrypt.return_value = b'{"Cliente": "Test"}'

                 data = LicenseManager.get_license_data()
                 assert data["Cliente"] == "Test"
                 # Check it looked in user dir first (normpath handles separators if needed, but here simple string check)
                 # os.path.join uses OS separator. On linux /user/lic/config.dat
                 # On windows \user\lic\config.dat
                 # Since we run on linux in sandbox:
                 mock_file.assert_called_with("/user/lic/config.dat", "rb")

    def test_get_license_data_fallback(self):
        with patch.dict(sys.modules, mock_modules):
            from desktop_app.services.license_manager import LicenseManager

            with patch("desktop_app.services.license_manager.get_license_dir", return_value="/user/lic"), \
                 patch("desktop_app.services.license_manager.get_app_install_dir", return_value="/app/install"), \
                 patch("os.path.exists") as mock_exists, \
                 patch("builtins.open", mock_open(read_data=b"encrypted")), \
                 patch("desktop_app.services.license_manager.Fernet") as MockFernet, \
                 patch("desktop_app.services.license_manager.get_license_secret_key", return_value=b"key"):

                 # First path False, Second path True
                 def exists_side_effect(path):
                     if "user" in path: return False
                     if "Licenza" in path: return True
                     return False

                 mock_exists.side_effect = exists_side_effect
                 MockFernet.return_value.decrypt.return_value = b'{"Cliente": "Fallback"}'

                 data = LicenseManager.get_license_data()
                 assert data["Cliente"] == "Fallback"

    def test_is_license_expiring_soon(self):
        with patch.dict(sys.modules, mock_modules):
            from desktop_app.services.license_manager import LicenseManager

            # Setup dates
            today = datetime(2025, 1, 1).date()

            with patch("desktop_app.services.license_manager.get_secure_date", return_value=today):
                # Expiring in 5 days (True)
                data = {"Scadenza Licenza": "06/01/2025"}
                assert LicenseManager.is_license_expiring_soon(data, days=7) is True

                # Expiring in 10 days (False)
                data = {"Scadenza Licenza": "11/01/2025"}
                assert LicenseManager.is_license_expiring_soon(data, days=7) is False

                # Already expired (False, as logic requires today < expiry)
                data = {"Scadenza Licenza": "31/12/2024"}
                assert LicenseManager.is_license_expiring_soon(data, days=7) is False

                # Invalid format
                data = {"Scadenza Licenza": "invalid"}
                assert LicenseManager.is_license_expiring_soon(data, days=7) is False
