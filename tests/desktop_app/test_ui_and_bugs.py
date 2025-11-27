import sys
import os
from unittest.mock import MagicMock, patch
import pytest
from datetime import date, timedelta

@patch('desktop_app.main_window_ui.load_colored_icon')
@patch('desktop_app.services.license_manager.LicenseManager.get_license_data')
def test_sidebar_license_expired(mock_get_license, mock_load_icon):
    from desktop_app.main_window_ui import Sidebar
    mock_load_icon.return_value = MagicMock()

    # Expiry date in past
    past_date = (date.today() - timedelta(days=5)).strftime("%d/%m/%Y")
    mock_get_license.return_value = {
        "Hardware ID": "12345",
        "Scadenza Licenza": past_date,
        "Generato il": "01/01/2023"
    }

    sidebar = Sidebar()
    # Check labels for "Licenza SCADUTA"
    labels = []
    for i in range(sidebar.license_layout.count()):
        item = sidebar.license_layout.itemAt(i)
        if item.widget():
            labels.append(item.widget().text())

    assert any("Licenza SCADUTA" in t for t in labels)
    assert any("5 giorni" in t for t in labels)

@patch('requests.post')
def test_pdf_worker_headers(mock_post):
    from desktop_app.views.import_view import PdfWorker
    mock_client = MagicMock()
    mock_client.base_url = "http://test"
    mock_client._get_headers.return_value = {"Authorization": "Bearer token"}

    worker = PdfWorker(["/tmp/test.pdf"], mock_client, "/tmp/dummy_output")

    # Mock logging
    mock_log = MagicMock()
    worker.log_message.connect(mock_log)

    # Mock file open and os.makedirs
    with patch("builtins.open", create=True) as mock_open, \
         patch("os.makedirs") as mock_makedirs, \
         patch("shutil.move") as mock_move:

        mock_open.return_value.__enter__.return_value = MagicMock()

        # Mock response for upload
        mock_response_upload = MagicMock()
        mock_response_upload.status_code = 200
        mock_response_upload.json.return_value = {"entities": {}}

        # Mock response for save
        mock_response_save = MagicMock()
        mock_response_save.status_code = 200
        mock_response_save.json.return_value = {}

        mock_post.side_effect = [mock_response_upload, mock_response_save]

        worker.process_pdf("/tmp/test.pdf")

        # Debug logs if failure
        if mock_post.call_count != 2:
            print("\nLOGS:", mock_log.call_args_list)

        # Verify calls
        assert mock_post.call_count == 2

        # Check arguments
        # Call 1: upload
        args1, kwargs1 = mock_post.call_args_list[0]
        assert kwargs1.get('headers') == {"Authorization": "Bearer token"}

        # Call 2: save
        args2, kwargs2 = mock_post.call_args_list[1]
        assert kwargs2.get('headers') == {"Authorization": "Bearer token"}
