import sys
import unittest
from unittest.mock import patch, MagicMock
from tests.desktop_app.mock_qt import mock_qt_modules

# Patch before import
mock_modules = mock_qt_modules()
with patch.dict(sys.modules, mock_modules):
    from desktop_app.views.login_view import LoginView
    from desktop_app.services.license_manager import LicenseManager

class TestLoginViewLicense(unittest.TestCase):
    def test_login_view_reads_license(self):
        # Setup Mock for LicenseManager
        mock_data = {
            "Cliente": "Test Corp",
            "Scadenza Licenza": "01/01/2030",
            "Hardware ID": "HWID-123"
        }

        # Patching the method on the class directly to ensure it catches the reference
        with patch.object(LicenseManager, 'get_license_data', return_value=mock_data):
            view = LoginView(api_client=MagicMock())

            # Verify text content
            text = view.read_license_info()
            print(f"DEBUG: Read text: {text}")
            self.assertIn("Licenza: Test Corp", text)
            self.assertIn("Scadenza: 01/01/2030", text)

    def test_login_view_missing_license(self):
        with patch.object(LicenseManager, 'get_license_data', return_value=None):
            view = LoginView(api_client=MagicMock())
            text = view.read_license_info()
            print(f"DEBUG: Read text: {text}")
            self.assertEqual(text, "Licenza non trovata o non valida")

if __name__ == '__main__':
    unittest.main()
