import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
from datetime import datetime, date
from desktop_app.views.import_view import PdfWorker

class TestPdfWorker(unittest.TestCase):

    def setUp(self):
        self.api_client = MagicMock()
        self.api_client.base_url = "http://test-api"
        self.worker = PdfWorker([], "/tmp/test_folder", self.api_client)
        # Mock signals to prevent segfaults or errors if no event loop
        self.worker.log_message = MagicMock()
        self.worker.status_update = MagicMock()
        self.worker.progress = MagicMock()
        self.worker.finished = MagicMock()

    @patch('desktop_app.views.import_view.requests.post')
    @patch('desktop_app.views.import_view.shutil.move')
    @patch('desktop_app.views.import_view.os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data=b"pdf_content")
    def test_process_pdf_success_active(self, mock_file, mock_makedirs, mock_move, mock_post):
        # Setup
        file_path = "/tmp/test_folder/doc.pdf"

        # Mock API responses
        # 1. upload-pdf response
        mock_upload_resp = MagicMock()
        mock_upload_resp.status_code = 200
        mock_upload_resp.json.return_value = {
            "entities": {
                "nome": "Mario Rossi",
                "corso": "Corso Sicurezza",
                "categoria": "ANTINCENDIO",
                "data_rilascio": "01-01-2025",
                "data_scadenza": "01-01-2030",
                "data_nascita": "01-01-1980"
            }
        }

        # 2. save certificate response
        mock_save_resp = MagicMock()
        mock_save_resp.status_code = 200
        mock_save_resp.json.return_value = {
            "id": 1,
            "nome": "Mario Rossi",
            "matricola": "12345",
            "categoria": "ANTINCENDIO",
            "data_scadenza": "01/01/2030",
            "assegnazione_fallita_ragione": None
        }

        mock_post.side_effect = [mock_upload_resp, mock_save_resp]

        # Execute
        self.worker.process_pdf(file_path)

        # Assertions
        # Check folder creation
        expected_base = os.path.dirname(file_path)
        expected_doc_folder = os.path.join(expected_base, "DOCUMENTI DIPENDENTI", "Mario Rossi (12345)", "ANTINCENDIO", "ATTIVO")
        mock_makedirs.assert_any_call(expected_doc_folder, exist_ok=True)

        # Check file move
        expected_new_filename = "Mario Rossi (12345) - ANTINCENDIO - 01_01_2030.pdf"
        expected_dest_path = os.path.join(expected_doc_folder, expected_new_filename)
        mock_move.assert_called_with(file_path, expected_dest_path)

    @patch('desktop_app.views.import_view.requests.post')
    @patch('desktop_app.views.import_view.shutil.move')
    @patch('desktop_app.views.import_view.os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data=b"pdf_content")
    def test_process_pdf_success_expired_historical(self, mock_file, mock_makedirs, mock_move, mock_post):
        # Setup
        file_path = "/tmp/test_folder/old_doc.pdf"

        # Mock API responses
        mock_upload_resp = MagicMock()
        mock_upload_resp.status_code = 200
        mock_upload_resp.json.return_value = {"entities": {}}

        mock_save_resp = MagicMock()
        mock_save_resp.status_code = 200
        mock_save_resp.json.return_value = {
            "id": 1,
            "nome": "Luigi Verdi",
            "matricola": "67890",
            "categoria": "PRIMO SOCCORSO",
            "data_scadenza": "01/01/2020", # Expired
            "assegnazione_fallita_ragione": None
        }

        mock_post.side_effect = [mock_upload_resp, mock_save_resp]

        # Execute
        self.worker.process_pdf(file_path)

        # Assertions
        expected_base = os.path.dirname(file_path)
        # Status should be STORICO
        expected_doc_folder = os.path.join(expected_base, "DOCUMENTI DIPENDENTI", "Luigi Verdi (67890)", "PRIMO SOCCORSO", "STORICO")
        mock_makedirs.assert_any_call(expected_doc_folder, exist_ok=True)

        expected_new_filename = "Luigi Verdi (67890) - PRIMO SOCCORSO - 01_01_2020.pdf"
        expected_dest_path = os.path.join(expected_doc_folder, expected_new_filename)
        mock_move.assert_called_with(file_path, expected_dest_path)

    @patch('desktop_app.views.import_view.requests.post')
    @patch('desktop_app.views.import_view.shutil.move')
    @patch('desktop_app.views.import_view.os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data=b"pdf_content")
    def test_process_pdf_no_expiration_nomine(self, mock_file, mock_makedirs, mock_move, mock_post):
        # Setup
        file_path = "/tmp/test_folder/nomina.pdf"

        # Mock API responses
        mock_upload_resp = MagicMock()
        mock_upload_resp.status_code = 200
        mock_upload_resp.json.return_value = {"entities": {}}

        mock_save_resp = MagicMock()
        mock_save_resp.status_code = 200
        mock_save_resp.json.return_value = {
            "id": 1,
            "nome": "Anna Bianchi",
            "matricola": "11223",
            "categoria": "NOMINE",
            "data_scadenza": None, # No expiration
            "assegnazione_fallita_ragione": None
        }

        mock_post.side_effect = [mock_upload_resp, mock_save_resp]

        # Execute
        self.worker.process_pdf(file_path)

        # Assertions
        expected_base = os.path.dirname(file_path)
        # Status should be ATTIVO
        expected_doc_folder = os.path.join(expected_base, "DOCUMENTI DIPENDENTI", "Anna Bianchi (11223)", "NOMINE", "ATTIVO")
        mock_makedirs.assert_any_call(expected_doc_folder, exist_ok=True)

        # Filename should contain "no scadenza"
        expected_new_filename = "Anna Bianchi (11223) - NOMINE - no scadenza.pdf"
        expected_dest_path = os.path.join(expected_doc_folder, expected_new_filename)
        mock_move.assert_called_with(file_path, expected_dest_path)

    @patch('desktop_app.views.import_view.requests.post')
    @patch('desktop_app.views.import_view.shutil.move')
    @patch('desktop_app.views.import_view.os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data=b"pdf_content")
    def test_process_pdf_manual_assignment(self, mock_file, mock_makedirs, mock_move, mock_post):
        # Setup
        file_path = "/tmp/test_folder/orphan.pdf"

        # Mock API responses
        mock_upload_resp = MagicMock()
        mock_upload_resp.status_code = 200
        mock_upload_resp.json.return_value = {"entities": {}}

        mock_save_resp = MagicMock()
        mock_save_resp.status_code = 200
        mock_save_resp.json.return_value = {
            "id": 1,
            "assegnazione_fallita_ragione": "Non trovato in anagrafica"
        }

        mock_post.side_effect = [mock_upload_resp, mock_save_resp]

        # Execute
        self.worker.process_pdf(file_path)

        # Assertions
        expected_base = os.path.dirname(file_path)
        # Should be moved to NON ANALIZZATI
        expected_folder = os.path.join(expected_base, "NON ANALIZZATI")
        expected_dest = os.path.join(expected_folder, "orphan.pdf")

        mock_makedirs.assert_any_call(expected_folder, exist_ok=True)
        mock_move.assert_called_with(file_path, expected_dest)
