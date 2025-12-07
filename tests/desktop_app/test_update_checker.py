import unittest
from unittest.mock import patch, MagicMock
from desktop_app.services.update_checker import UpdateChecker, UpdateWorker
from PyQt6.QtCore import QThread
import time

class TestUpdateChecker(unittest.TestCase):
    @patch('desktop_app.services.update_checker.requests.get')
    @patch('desktop_app.services.update_checker.version.parse')
    @patch('desktop_app.services.update_checker.__version__', '1.0.0')
    def test_check_for_updates_available(self, mock_parse, mock_get):
        # Mock Response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "latest_version": "1.1.0",
            "installer_url": "http://example.com/installer.exe"
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Mock Version Comparison
        # 1.1.0 > 1.0.0
        mock_parse.side_effect = lambda v: tuple(map(int, v.split('.')))

        checker = UpdateChecker()
        has_update, ver, url = checker.check_for_updates()

        self.assertTrue(has_update)
        self.assertEqual(ver, "1.1.0")
        self.assertEqual(url, "http://example.com/installer.exe")

    @patch('desktop_app.services.update_checker.requests.get')
    @patch('desktop_app.services.update_checker.version.parse')
    @patch('desktop_app.services.update_checker.__version__', '1.0.0')
    def test_check_for_updates_none(self, mock_parse, mock_get):
        # Mock Response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "latest_version": "1.0.0",
            "installer_url": "http://example.com/installer.exe"
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Mock Version Comparison
        # 1.0.0 == 1.0.0
        mock_parse.side_effect = lambda v: tuple(map(int, v.split('.')))

        checker = UpdateChecker()
        has_update, ver, url = checker.check_for_updates()

        self.assertFalse(has_update)
        self.assertIsNone(ver)
        self.assertIsNone(url)

if __name__ == '__main__':
    unittest.main()
