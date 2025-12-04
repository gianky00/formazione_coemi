import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import shutil
import tempfile
from desktop_app.views.import_view import PdfWorker

class TestPdfWorkerReject(unittest.TestCase):
    def setUp(self):
        self.output_folder = tempfile.mkdtemp()
        self.api_client = MagicMock()
        self.api_client.base_url = "http://test-api"
        self.worker = PdfWorker([], self.api_client, self.output_folder)
        self.worker.log_message = MagicMock()

    def tearDown(self):
        shutil.rmtree(self.output_folder)

    @patch('desktop_app.views.import_view.requests.post')
    @patch('desktop_app.views.import_view.shutil.move')
    @patch('desktop_app.views.import_view.os.makedirs')
    def test_reject_creates_txt(self, mock_makedirs, mock_move, mock_post):
        # We don't mock open globally because we want to verify the specific call for txt
        # But PdfWorker opens the PDF too.
        # So we mock open to handle both.

        file_path = os.path.join(self.output_folder, "rejected.pdf")

        mock_resp = MagicMock()
        mock_resp.status_code = 422
        mock_resp.json.return_value = {"detail": "REJECTED: Syllabus"}
        mock_post.return_value = mock_resp

        with patch('builtins.open', mock_open(read_data=b"pdf_content")) as mock_file:
            self.worker.process_pdf(file_path)

            # Verify attempts to write to .txt
            # Expected path ending: ERRORI ANALISI/SCARTATI/rejected.txt

            found_write = False
            for call in mock_file.call_args_list:
                args = call[0]
                path = str(args[0])
                mode = args[1] if len(args) > 1 else 'r'

                if path.endswith("rejected.txt") and 'w' in mode:
                    found_write = True
                    break

            assert found_write, "Did not attempt to write rejection reason to .txt file"
