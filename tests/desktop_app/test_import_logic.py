import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import shutil
import tempfile
from datetime import datetime, date
from desktop_app.views.import_view import PdfWorker

class TestPdfWorker(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for output to ensure valid OS paths
        self.output_folder = tempfile.mkdtemp()
        
        # We do NOT patch collections.deque anymore as it caused side effects
        
        self.api_client = MagicMock()
        self.api_client.base_url = "http://test-api"
        self.worker = PdfWorker([], self.api_client, self.output_folder)
        # Mock signals
        self.worker.log_message = MagicMock()
        self.worker.status_update = MagicMock()
        self.worker.progress = MagicMock()
        self.worker.finished = MagicMock()
        self.worker.etr_update = MagicMock()

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.output_folder)

    def assert_path_called(self, mock_func, expected_path, **kwargs):
        """Helper to assert a path was passed to a mock, normalizing separators."""
        assert mock_func.called, f"Mock {mock_func._mock_name} was not called"

        # Check if any call matches the expected path
        found = False
        norm_expected = os.path.normpath(expected_path)

        for call_args in mock_func.call_args_list:
            args = call_args[0]
            if len(args) > 0:
                norm_actual = os.path.normpath(args[0])
                if norm_actual == norm_expected:
                    found = True
                    break

        if not found:
            # Format actual calls for debug
            actual_calls = [os.path.normpath(c[0][0]) if c[0] else str(c) for c in mock_func.call_args_list]
            raise AssertionError(f"Path {norm_expected} not found in calls. Actual calls: {actual_calls}")

    @patch('desktop_app.views.import_view.requests.post')
    @patch('desktop_app.views.import_view.shutil.move')
    @patch('desktop_app.views.import_view.os.makedirs')
    @patch('desktop_app.views.import_view.os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data=b"pdf_content")
    def test_process_pdf_success_active(self, mock_file, mock_exists, mock_makedirs, mock_move, mock_post):
        file_path = os.path.join(self.output_folder, "doc.pdf")

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
        self.assert_path_called(mock_makedirs, expected_doc_folder)

        expected_new_filename = "Mario Rossi (12345) - ANTINCENDIO - 01_01_2030.pdf"
        expected_dest_path = os.path.join(expected_doc_folder, expected_new_filename)
        # Verify move called with correct dest
        # mock_move(src, dst)
        assert mock_move.called
        # Check last call or find match
        args = mock_move.call_args[0]
        assert os.path.normpath(args[1]) == os.path.normpath(expected_dest_path)

    @patch('desktop_app.views.import_view.requests.post')
    @patch('desktop_app.views.import_view.shutil.move')
    @patch('desktop_app.views.import_view.os.makedirs')
    @patch('desktop_app.views.import_view.os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data=b"pdf_content")
    def test_process_pdf_success_expired_historical(self, mock_file, mock_exists, mock_makedirs, mock_move, mock_post):
        file_path = os.path.join(self.output_folder, "old_doc.pdf")

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
        self.assert_path_called(mock_makedirs, expected_doc_folder)

        expected_new_filename = "Luigi Verdi (67890) - PRIMO SOCCORSO - 01_01_2020.pdf"
        expected_dest_path = os.path.join(expected_doc_folder, expected_new_filename)

        assert mock_move.called
        args = mock_move.call_args[0]
        assert os.path.normpath(args[1]) == os.path.normpath(expected_dest_path)

    @patch('desktop_app.views.import_view.requests.post')
    @patch('desktop_app.views.import_view.shutil.move')
    @patch('desktop_app.views.import_view.os.makedirs')
    @patch('desktop_app.views.import_view.os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data=b"pdf_content")
    def test_process_pdf_no_expiration_nomine(self, mock_file, mock_exists, mock_makedirs, mock_move, mock_post):
        file_path = os.path.join(self.output_folder, "nomina.pdf")

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
        self.assert_path_called(mock_makedirs, expected_doc_folder)

        expected_new_filename = "Anna Bianchi (11223) - NOMINA - no scadenza.pdf"
        expected_dest_path = os.path.join(expected_doc_folder, expected_new_filename)

        assert mock_move.called
        args = mock_move.call_args[0]
        assert os.path.normpath(args[1]) == os.path.normpath(expected_dest_path)

    @patch('desktop_app.views.import_view.requests.post')
    @patch('desktop_app.views.import_view.shutil.move')
    @patch('desktop_app.views.import_view.os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data=b"pdf_content")
    def test_process_pdf_manual_assignment(self, mock_file, mock_makedirs, mock_move, mock_post):
        file_path = os.path.join(self.output_folder, "orphan.pdf")

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
        expected_folder = os.path.join(self.worker.output_folder, "ERRORI ANALISI", "ASSENZA MATRICOLE", "SCONOSCIUTO (N-A)", "ANTINCENDIO", "ATTIVO")
        self.assert_path_called(mock_makedirs, expected_folder)
        
        expected_dest = os.path.join(expected_folder, "SCONOSCIUTO (N-A) - ANTINCENDIO - no scadenza.pdf")

        assert mock_move.called
        args = mock_move.call_args[0]
        assert os.path.normpath(args[1]) == os.path.normpath(expected_dest)

    @patch('desktop_app.views.import_view.requests.post')
    @patch('desktop_app.views.import_view.shutil.move')
    @patch('desktop_app.views.import_view.os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data=b"pdf_content")
    def test_process_pdf_ai_failure(self, mock_file, mock_makedirs, mock_move, mock_post):
        file_path = os.path.join(self.output_folder, "error.pdf")

        mock_upload_resp = MagicMock()
        mock_upload_resp.status_code = 429
        mock_upload_resp.text = "Too Many Requests"

        mock_post.side_effect = [mock_upload_resp]

        self.worker.process_pdf(file_path)

        # Default fallback -> ERRORI ANALISI/ALTRI ERRORI/<Filename>/error.pdf
        # Note: filename without extension is used as folder
        expected_folder = os.path.join(self.worker.output_folder, "ERRORI ANALISI", "ALTRI ERRORI", "error")
        expected_dest = os.path.join(expected_folder, "error.pdf")

        self.assert_path_called(mock_makedirs, expected_folder)

        assert mock_move.called
        args = mock_move.call_args[0]
        assert os.path.normpath(args[1]) == os.path.normpath(expected_dest)
