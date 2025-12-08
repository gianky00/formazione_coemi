import unittest
import os
import io
import sys
import importlib
from unittest.mock import MagicMock, patch, mock_open
import requests

class TestAPIClientCoverage(unittest.TestCase):
    def setUp(self):
        # Ensure we have the real APIClient class, not a mock from sys.modules pollution
        if 'desktop_app.api_client' in sys.modules:
            del sys.modules['desktop_app.api_client']
        
        import desktop_app.api_client
        importlib.reload(desktop_app.api_client)
        self.module = desktop_app.api_client
        self.APIClient = self.module.APIClient

    def test_set_and_clear_token(self):
        client = self.APIClient()
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
        client.set_token(token_data)
        
        self.assertEqual(client.access_token, "fake_token")
        self.assertEqual(client.user_info["username"], "admin")
        self.assertTrue(client.user_info["is_admin"])

        client.clear_token()
        self.assertIsNone(client.access_token)
        self.assertIsNone(client.user_info)

    def test_get_headers(self):
        # Patch the function on the reloaded module
        with patch.object(self.module, 'get_device_id', return_value="device_123"):
            client = self.APIClient()
            
            headers = client._get_headers()
            self.assertEqual(headers.get("X-Device-ID"), "device_123")
            self.assertNotIn("Authorization", headers)

            client.access_token = "token_abc"
            headers = client._get_headers()
            self.assertEqual(headers["Authorization"], "Bearer token_abc")

    @patch('requests.get')
    def test_get_success(self, mock_get):
        client = self.APIClient()
        client.base_url = "http://testserver/api/v1"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        data = client.get("endpoint")
        self.assertEqual(data, {"key": "value"})
        mock_get.assert_called()
        args, kwargs = mock_get.call_args
        self.assertTrue(args[0].endswith("/api/v1/endpoint"))

    @patch('requests.get')
    def test_get_connection_error(self, mock_get):
        client = self.APIClient()
        mock_get.side_effect = requests.exceptions.ConnectionError("Offline")
        
        with self.assertRaises(ConnectionError) as cm:
            client.get("endpoint")
        self.assertIn("Offline", str(cm.exception))

    @patch('requests.post')
    def test_login_success(self, mock_post):
        client = self.APIClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "123"}
        mock_post.return_value = mock_response

        resp = client.login("u", "p")
        self.assertEqual(resp["access_token"], "123")

    @patch('requests.post')
    def test_login_fail(self, mock_post):
        client = self.APIClient()
        mock_post.side_effect = requests.exceptions.ConnectionError
        with self.assertRaises(Exception):
            client.login("u", "p")

    @patch('requests.post')
    def test_logout(self, mock_post):
        client = self.APIClient()
        client.access_token = "tok"
        client.logout()
        self.assertIsNone(client.access_token)
        mock_post.assert_called()

    @patch('os.path.getsize')
    @patch('builtins.open', new_callable=mock_open, read_data=b"data")
    @patch('requests.post')
    def test_import_dipendenti_csv(self, mock_post, mock_file, mock_size):
        client = self.APIClient()
        # Case 1: File too big
        mock_size.return_value = 10 * 1024 * 1024 # 10MB
        with self.assertRaises(ValueError) as cm:
            client.import_dipendenti_csv("large.csv")
        self.assertIn("supera il limite", str(cm.exception))

        # Case 2: Success
        mock_size.return_value = 1024
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "ok"}
        mock_post.return_value = mock_response

        res = client.import_dipendenti_csv("ok.csv")
        self.assertEqual(res["message"], "ok")

    @patch('requests.get')
    def test_get_mutable_config(self, mock_get):
        client = self.APIClient()
        mock_response = MagicMock()
        mock_response.json.return_value = {"SETTING": 1}
        mock_get.return_value = mock_response
        
        self.assertEqual(client.get_mutable_config()["SETTING"], 1)

    @patch('requests.post')
    def test_toggle_db_security(self, mock_post):
        client = self.APIClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        client.toggle_db_security(True)
        mock_post.assert_called()
        args, kwargs = mock_post.call_args
        self.assertTrue(args[0].endswith("/config/db-security/toggle"))
        self.assertEqual(kwargs['json'], {"locked": True})

    @patch('requests.post')
    def test_move_database(self, mock_post):
        client = self.APIClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        client.move_database("path")
        mock_post.assert_called()

if __name__ == '__main__':
    unittest.main()
