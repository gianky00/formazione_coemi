import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
from datetime import datetime, date

class TestPdfWorker(unittest.TestCase):

    def setUp(self):
        # Patch collections.deque to avoid import error during test collection if logic changed
        with patch("collections.deque"):
            from desktop_app.views.import_view import PdfWorker
        self.api_client = MagicMock()
        self.api_client.base_url = "http://test-api"
        self.worker = PdfWorker([], self.api_client, "/tmp/output")
        # Mock signals
        self.worker.log_message = MagicMock()
        self.worker.status_update = MagicMock()
        self.worker.progress = MagicMock()
        self.worker.finished = MagicMock()
        self.worker.etr_update = MagicMock()

    @patch('desktop_app.views.import_view.requests.post')
    @patch('desktop_app.views.import_view.shutil.move')
    @patch('desktop_app.views.import_view.os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data=b"pdf_content")
    def test_process_pdf_success_active(self, mock_file, mock_makedirs, mock_move, mock_post):
        file_path = "/tmp/test_folder/doc.pdf"

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

        self.worker.process_pdf(file_path)

        expected_doc_folder = os.path.join(self.worker.output_folder, "DOCUMENTI DIPENDENTI", "Mario Rossi (12345)", "ANTINCENDIO", "ATTIVO")
        mock_makedirs.assert_any_call(expected_doc_folder, exist_ok=True)

        expected_new_filename = "Mario Rossi (12345) - ANTINCENDIO - 01_01_2030.pdf"
        expected_dest_path = os.path.join(expected_doc_folder, expected_new_filename)
        mock_move.assert_called_with(file_path, expected_dest_path)

    @patch('desktop_app.views.import_view.requests.post')
    @patch('desktop_app.views.import_view.shutil.move')
    @patch('desktop_app.views.import_view.os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data=b"pdf_content")
    def test_process_pdf_success_expired_historical(self, mock_file, mock_makedirs, mock_move, mock_post):
        file_path = "/tmp/test_folder/old_doc.pdf"

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
            "data_scadenza": "01/01/2020",
            "assegnazione_fallita_ragione": None
        }

        mock_post.side_effect = [mock_upload_resp, mock_save_resp]

        self.worker.process_pdf(file_path)

        expected_doc_folder = os.path.join(self.worker.output_folder, "DOCUMENTI DIPENDENTI", "Luigi Verdi (67890)", "PRIMO SOCCORSO", "STORICO")
        mock_makedirs.assert_any_call(expected_doc_folder, exist_ok=True)

        expected_new_filename = "Luigi Verdi (67890) - PRIMO SOCCORSO - 01_01_2020.pdf"
        expected_dest_path = os.path.join(expected_doc_folder, expected_new_filename)
        mock_move.assert_called_with(file_path, expected_dest_path)

    @patch('desktop_app.views.import_view.requests.post')
    @patch('desktop_app.views.import_view.shutil.move')
    @patch('desktop_app.views.import_view.os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data=b"pdf_content")
    def test_process_pdf_no_expiration_nomine(self, mock_file, mock_makedirs, mock_move, mock_post):
        file_path = "/tmp/test_folder/nomina.pdf"

        mock_upload_resp = MagicMock()
        mock_upload_resp.status_code = 200
        mock_upload_resp.json.return_value = {"entities": {}}

        mock_save_resp = MagicMock()
        mock_save_resp.status_code = 200
        mock_save_resp.json.return_value = {
            "id": 1,
            "nome": "Anna Bianchi",
            "matricola": "11223",
            "categoria": "NOMINA",
            "data_scadenza": None,
            "assegnazione_fallita_ragione": None
        }

        mock_post.side_effect = [mock_upload_resp, mock_save_resp]

        self.worker.process_pdf(file_path)

        expected_doc_folder = os.path.join(self.worker.output_folder, "DOCUMENTI DIPENDENTI", "Anna Bianchi (11223)", "NOMINA", "ATTIVO")
        mock_makedirs.assert_any_call(expected_doc_folder, exist_ok=True)

        expected_new_filename = "Anna Bianchi (11223) - NOMINA - no scadenza.pdf"
        expected_dest_path = os.path.join(expected_doc_folder, expected_new_filename)
        mock_move.assert_called_with(file_path, expected_dest_path)

    @patch('desktop_app.views.import_view.requests.post')
    @patch('desktop_app.views.import_view.shutil.move')
    @patch('desktop_app.views.import_view.os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data=b"pdf_content")
    def test_process_pdf_manual_assignment(self, mock_file, mock_makedirs, mock_move, mock_post):
        file_path = "/tmp/test_folder/orphan.pdf"

        mock_upload_resp = MagicMock()
        mock_upload_resp.status_code = 200
        mock_upload_resp.json.return_value = {"entities": {"categoria": "ANTINCENDIO"}}

        mock_save_resp = MagicMock()
        mock_save_resp.status_code = 200
        mock_save_resp.json.return_value = {
            "id": 1,
            "nome": "SCONOSCIUTO",
            "categoria": "ANTINCENDIO",
            "assegnazione_fallita_ragione": "Non trovato in anagrafica (matricola mancante)."
        }

        mock_post.side_effect = [mock_upload_resp, mock_save_resp]

        self.worker.process_pdf(file_path)

        # Logic for "matricola" in failure reason -> ERRORI ANALISI/ASSENZA MATRICOLE
        # Name is SCONOSCIUTO (N-A)
        # Category is ANTINCENDIO
        # Status is ATTIVO (scadenza None defaults to attivo) -> no, it defaults to 'ATTIVO' in code if not present
        expected_folder = os.path.join(self.worker.output_folder, "ERRORI ANALISI", "ASSENZA MATRICOLE", "SCONOSCIUTO (N-A)", "ANTINCENDIO", "ATTIVO")
        mock_makedirs.assert_any_call(expected_folder, exist_ok=True)

        expected_dest = os.path.join(expected_folder, "SCONOSCIUTO (N-A) - ANTINCENDIO - no scadenza.pdf")
        mock_move.assert_called_with(file_path, expected_dest)

    @patch('desktop_app.views.import_view.requests.post')
    @patch('desktop_app.views.import_view.shutil.move')
    @patch('desktop_app.views.import_view.os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data=b"pdf_content")
    def test_process_pdf_ai_failure(self, mock_file, mock_makedirs, mock_move, mock_post):
        file_path = "/tmp/test_folder/error.pdf"

        mock_upload_resp = MagicMock()
        mock_upload_resp.status_code = 429
        mock_upload_resp.text = "Too Many Requests"

        mock_post.side_effect = [mock_upload_resp]

        self.worker.process_pdf(file_path)

        # Default fallback -> ERRORI ANALISI/ALTRI ERRORI/<Filename>/error.pdf
        expected_folder = os.path.join(self.worker.output_folder, "ERRORI ANALISI", "ALTRI ERRORI", "error")
        expected_dest = os.path.join(expected_folder, "error.pdf")

        mock_makedirs.assert_any_call(expected_folder, exist_ok=True)
        mock_move.assert_called_with(file_path, expected_dest)
