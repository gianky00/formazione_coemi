
import sys
import pytest
import unittest
from unittest.mock import MagicMock, patch

# Mock modules
from tests.desktop_app.mock_qt import mock_qt_modules
sys.modules.update(mock_qt_modules())

from desktop_app.views.login_view import LoginView
from desktop_app.services.license_manager import LicenseManager

class TestLoginViewLicense(unittest.TestCase):

    def setUp(self):
        self.mock_api = MagicMock()

    def test_login_view_reads_license(self):
        # Setup Mock for LicenseManager
        mock_data = {
            "Cliente": "Test Corp",
            "Scadenza Licenza": "01/01/2030",
            "Hardware ID": "HWID-123"
        }

        # Patching the method on the class in the VIEW module
        # Because LoginView imports LicenseManager from services directly
        with patch('desktop_app.views.login_view.LicenseManager.get_license_data', return_value=mock_data):
            # Also mock get_machine_id which is used in init
            with patch('desktop_app.views.login_view.get_machine_id', return_value='HWID-123'):
                view = LoginView(api_client=self.mock_api)

                # Verify text content
                text, data = view.read_license_info()

                assert "Test Corp" in text
                assert data["Hardware ID"] == "HWID-123"

    def test_login_view_missing_license(self):
        with patch('desktop_app.views.login_view.LicenseManager.get_license_data', return_value=None):
             with patch('desktop_app.views.login_view.get_machine_id', return_value='HWID-123'):
                view = LoginView(api_client=self.mock_api)
                text, data = view.read_license_info()

                assert "non disponibili" in text
                assert data == {}

if __name__ == '__main__':
    unittest.main()
