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
    @patch('desktop_app.views.login_view.get_machine_id', return_value='HWID-123')
    def test_login_view_reads_license(self, mock_get_id):
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
            text, data = view.read_license_info()
            self.assertIn("Cliente: Test Corp", text)
            self.assertIn("Scadenza: 01/01/2030", text)
            self.assertIn("ID Licenza: HWID-123", text)
            self.assertEqual(data, mock_data)

    def test_login_view_missing_license(self):
        with patch.object(LicenseManager, 'get_license_data', return_value=None):
            view = LoginView(api_client=MagicMock())
            text, data = view.read_license_info()
            self.assertEqual(text, "Dettagli licenza non disponibili. Procedere con l'aggiornamento.")
            self.assertIsNone(data)

if __name__ == '__main__':
    unittest.main()
