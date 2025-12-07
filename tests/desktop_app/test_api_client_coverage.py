import unittest
import os
import io
from unittest.mock import MagicMock, patch, mock_open
import requests

# Patch get_device_id BEFORE importing APIClient
# This ensures that even if APIClient imports it, we can patch it where it is used.
with patch('desktop_app.utils.get_device_id') as mock_dev:
    from desktop_app.api_client import APIClient

class TestAPIClientCoverage(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.base_url = "http://testserver/api/v1"

    def test_set_and_clear_token(self):
        token_data = {
            "access_token": "fake_token",
            "user_id": 1,
            "username": "admin",
            "is_admin": True,
            "read_only": False,
            "lock_owner": None,
            "previous_login": "2023-01-01",
            "require_password_change": False
        }
        self.client.set_token(token_data)
        
        self.assertEqual(self.client.access_token, "fake_token")
        self.assertEqual(self.client.user_info["username"], "admin")
        self.assertTrue(self.client.user_info["is_admin"])

        self.client.clear_token()
        self.assertIsNone(self.client.access_token)
        self.assertIsNone(self.client.user_info)

    def test_get_headers(self):
        # We need to patch desktop_app.api_client.get_device_id because it is imported into that namespace
        with patch('desktop_app.api_client.get_device_id', return_value="device_123"):
            # No token
            headers = self.client._get_headers()
            self.assertEqual(headers.get("X-Device-ID"), "device_123")
            self.assertNotIn("Authorization", headers)

            # With token
            self.client.access_token = "token_abc"
            headers = self.client._get_headers()
            self.assertEqual(headers["Authorization"], "Bearer token_abc")

    @patch('requests.get')
    def test_get_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        data = self.client.get("endpoint")
        self.assertEqual(data, {"key": "value"})
        # Verify URL construction
        mock_get.assert_called()
        args, kwargs = mock_get.call_args
        self.assertTrue(args[0].endswith("/api/v1/endpoint"))

    @patch('requests.get')
    def test_get_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("Offline")
        
        with self.assertRaises(ConnectionError) as cm:
            self.client.get("endpoint")
        self.assertIn("Offline", str(cm.exception))

    @patch('requests.post')
    def test_login_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "123"}
        mock_post.return_value = mock_response

        resp = self.client.login("u", "p")
        self.assertEqual(resp["access_token"], "123")

    @patch('requests.post')
    def test_login_fail(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError
        with self.assertRaises(Exception):
            self.client.login("u", "p")

    @patch('requests.post')
    def test_logout(self, mock_post):
        self.client.access_token = "tok"
        self.client.logout()
        # Should clear token locally
        self.assertIsNone(self.client.access_token)
        # Should attempt server call
        mock_post.assert_called()

    @patch('os.path.getsize')
    @patch('builtins.open', new_callable=mock_open, read_data=b"data")
    @patch('requests.post')
    def test_import_dipendenti_csv(self, mock_post, mock_file, mock_size):
        # Case 1: File too big
        mock_size.return_value = 10 * 1024 * 1024 # 10MB
        with self.assertRaises(ValueError) as cm:
            self.client.import_dipendenti_csv("large.csv")
        self.assertIn("supera il limite", str(cm.exception))

        # Case 2: Success
        mock_size.return_value = 1024
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "ok"}
        mock_post.return_value = mock_response

        res = self.client.import_dipendenti_csv("ok.csv")
        self.assertEqual(res["message"], "ok")

    @patch('requests.get')
    def test_get_mutable_config(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"SETTING": 1}
        mock_get.return_value = mock_response
        
        self.assertEqual(self.client.get_mutable_config()["SETTING"], 1)

    @patch('requests.post')
    def test_toggle_db_security(self, mock_post):
        # We only care that it makes a POST request
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        self.client.toggle_db_security(True)
        mock_post.assert_called()
        args, kwargs = mock_post.call_args
        self.assertTrue(args[0].endswith("/config/db-security/toggle"))
        self.assertEqual(kwargs['json'], {"locked": True})

    @patch('requests.post')
    def test_move_database(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        self.client.move_database("path")
        mock_post.assert_called()

if __name__ == '__main__':
    unittest.main()
