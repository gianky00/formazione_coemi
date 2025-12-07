import unittest
import json
import os
from unittest.mock import MagicMock, patch, mock_open
from desktop_app.services.license_updater_service import LicenseUpdaterService

class TestLicenseUpdaterCoverage(unittest.TestCase):
    def setUp(self):
        self.mock_api_client = MagicMock()
        self.service = LicenseUpdaterService(self.mock_api_client)

    def test_load_config_from_api(self):
        self.mock_api_client.get.return_value = {"repo_owner": "o", "repo_name": "n", "github_token": "t"}
        config = self.service._load_config()
        self.assertEqual(config["repo_owner"], "o")

    def test_load_config_missing_api_and_config(self):
        srv = LicenseUpdaterService(None, None)
        with self.assertRaises(RuntimeError):
            srv._load_config()

    def test_update_license_no_token(self):
        self.service.config = {"repo_owner": "o", "repo_name": "n"} # Missing token
        success, msg = self.service.update_license("hwid")
        self.assertFalse(success)
        self.assertIn("incompleta", msg)

    @patch('desktop_app.services.license_updater_service.requests.get')
    @patch('desktop_app.services.license_updater_service.LicenseUpdaterService._calculate_sha256')
    @patch('shutil.move')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('json.dump')
    def test_update_license_success(self, mock_json_dump, mock_json_load, mock_file, mock_makedirs, mock_move, mock_sha, mock_get):
        # Config
        self.service.config = {"repo_owner": "o", "repo_name": "n", "github_token": "t"}

        # API Responses
        # 1. Manifest Metadata
        resp_meta_manifest = MagicMock()
        resp_meta_manifest.json.return_value = {"download_url": "http://dl/manifest"}
        
        # 2. Manifest Content (Remote)
        resp_content_manifest = MagicMock()
        remote_manifest = {"pyarmor.rkey": "hash1", "config.dat": "hash2"}
        resp_content_manifest.json.return_value = remote_manifest
        
        # 3. File Metadata (rkey)
        resp_meta_rkey = MagicMock()
        resp_meta_rkey.json.return_value = {"download_url": "http://dl/rkey"}
        
        # 4. File Content (rkey)
        resp_content_rkey = MagicMock()
        resp_content_rkey.content = b"rkey_data"

        # 5. File Metadata (config)
        resp_meta_config = MagicMock()
        resp_meta_config.json.return_value = {"download_url": "http://dl/config"}

        # 6. File Content (config)
        resp_content_config = MagicMock()
        resp_content_config.content = b"config_data"

        mock_get.side_effect = [
            resp_meta_manifest, resp_content_manifest, # Manifest
            resp_meta_rkey, resp_content_rkey,         # RKey
            resp_meta_config, resp_content_config      # Config
        ]

        # Checksums
        mock_sha.side_effect = ["hash1", "hash2"] # rkey, config
        
        # JSON Load (for local manifest check - mock failure to force download, and then verification)
        # First load: check local manifest (fail/different)
        # Second load: verification of downloaded manifest
        
        # Simulating open('local_manifest') -> raise FileNotFoundError or verify fail
        # We patch os.path.exists to return False for local manifest check
        with patch('os.path.exists', return_value=False):
             # Mock json.load for the verification step
             mock_json_load.return_value = remote_manifest

             success, msg = self.service.update_license("hwid")
        
        self.assertTrue(success, msg)
        self.assertIn("aggiornata con successo", msg)
        self.assertEqual(mock_move.call_count, 3) # rkey, config, manifest

    @patch('desktop_app.services.license_updater_service.requests.get')
    def test_update_license_checksum_fail(self, mock_get):
         self.service.config = {"repo_owner": "o", "repo_name": "n", "github_token": "t"}
         
         # Short circuit to fail logic
         # Manifest setup
         m1 = MagicMock(); m1.json.return_value = {"download_url": "u"}
         m2 = MagicMock(); m2.json.return_value = {"pyarmor.rkey": "CORRECT_HASH"}
         
         # File setup
         m3 = MagicMock(); m3.json.return_value = {"download_url": "u"}
         m4 = MagicMock(); m4.content = b"data"
         m5 = MagicMock(); m5.json.return_value = {"download_url": "u"}
         m6 = MagicMock(); m6.content = b"data"
         
         mock_get.side_effect = [m1, m2, m3, m4, m5, m6]
         
         with patch('desktop_app.services.license_updater_service.LicenseUpdaterService._calculate_sha256', return_value="WRONG_HASH"), \
              patch('os.path.exists', return_value=False), \
              patch('builtins.open', mock_open()), \
              patch('json.load', return_value={"pyarmor.rkey": "CORRECT_HASH", "config.dat": "hash"}), \
              patch('tempfile.TemporaryDirectory') as mock_temp:
             
             mock_temp.return_value.__enter__.return_value = "/tmp"
             
             success, msg = self.service.update_license("hwid")
             
             self.assertFalse(success)
             self.assertIn("Checksum", msg)

if __name__ == '__main__':
    unittest.main()
