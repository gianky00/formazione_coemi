
import sys
import os
import pytest
import unittest
import importlib
from unittest.mock import MagicMock, patch

# Force mock mode (must be before mock_qt import)

# Mock modules
from tests.desktop_app.mock_qt import mock_qt_modules
sys.modules.update(mock_qt_modules())

# Mark tests to run in forked subprocess
pytestmark = pytest.mark.forked

def reload_login_view():
    if 'desktop_app.views.login_view' in sys.modules:
        importlib.reload(sys.modules['desktop_app.views.login_view'])

class TestLoginViewLicense(unittest.TestCase):

    def setUp(self):
        self.mock_api = MagicMock()
        reload_login_view()
        # Must re-import class after reload
        from desktop_app.views.login_view import LoginView
        self.LoginViewClass = LoginView

    def test_login_view_reads_license(self):
        mock_data = {
            "Cliente": "Test Corp",
            "Scadenza Licenza": "01/01/2030",
            "Hardware ID": "HWID-123"
        }

        with patch('desktop_app.views.login_view.LicenseManager.get_license_data', return_value=mock_data):
            with patch('desktop_app.views.login_view.get_machine_id', return_value='HWID-123'):
                view = self.LoginViewClass(api_client=self.mock_api)

                text, data = view.read_license_info()

                assert "Test Corp" in text
                assert data["Hardware ID"] == "HWID-123"

    def test_login_view_missing_license(self):
        with patch('desktop_app.views.login_view.LicenseManager.get_license_data', return_value=None):
             with patch('desktop_app.views.login_view.get_machine_id', return_value='HWID-123'):
                view = self.LoginViewClass(api_client=self.mock_api)
                text, data = view.read_license_info()

                assert "non disponibili" in text
                assert data == {}

if __name__ == '__main__':
    unittest.main()
