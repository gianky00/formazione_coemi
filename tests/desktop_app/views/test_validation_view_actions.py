import sys
from unittest.mock import MagicMock, patch, ANY
import pytest
import pandas as pd
from tests.desktop_app.mock_qt import mock_modules, QtCore

# Apply mocks to sys.modules
for name, mod in mock_modules.items():
    sys.modules[name] = mod

# Import the module OBJECT so we can use patch.object on it
from desktop_app.views import validation_view as vv_module
from desktop_app.views.validation_view import ValidationView

@pytest.fixture
def api_client():
    client = MagicMock()
    client.access_token = "fake_token"
    client.base_url = "http://test/api/v1"
    client._get_headers.return_value = {"Authorization": "Bearer fake_token"}
    client.get_paths.return_value = {"database_path": "/fake/db/path"}
    return client

@pytest.fixture
def validation_view(api_client):
    with patch.object(vv_module, "FetchCertificatesWorker") as MockFetch:
        worker = MockFetch.return_value
        worker.signals = MagicMock()
        worker.signals.result = MagicMock()
        worker.signals.result.connect = MagicMock()
        worker.signals.error = MagicMock()
        worker.signals.error.connect = MagicMock()
        worker.signals.finished = MagicMock()
        worker.signals.finished.connect = MagicMock()

        view = ValidationView(api_client=api_client)
        data = [
            {"id": 1, "nome": "ROSSI MARIO", "categoria": "ANTINCENDIO", "stato_certificato": "in_scadenza"},
            {"id": 2, "nome": "BIANCHI LUIGI", "categoria": "PRIMO SOCCORSO", "stato_certificato": "valido"}
        ]
        view._on_data_loaded(data)
        return view

def test_load_data_success(validation_view):
    """Test data loading and table population."""
    assert validation_view.df is not None
    assert len(validation_view.df) == 2
    assert validation_view.table_view.setModel_called

def test_load_data_error(validation_view):
    """Test error handling during data load."""
    with patch.object(vv_module, "CustomMessageDialog") as MockDialog:
        validation_view._on_error("Network Error")
        MockDialog.show_error.assert_called_with(validation_view, "Errore di Connessione", ANY)
        assert validation_view.df.empty

def test_validate_selected(validation_view):
    """Test validating selected rows."""
    validation_view.is_read_only = False
    validation_view.get_selected_ids = MagicMock(return_value=["1", "2"])

    with patch.object(vv_module, "CustomMessageDialog") as MockDialog, \
         patch.object(vv_module, "ValidateCertificatesWorker") as MockWorker:

        MockDialog.show_question.return_value = True
        
        worker_instance = MagicMock()
        worker_instance.signals = MagicMock()
        worker_instance.signals.result = MagicMock()
        worker_instance.signals.result.connect = MagicMock()
        worker_instance.signals.finished = MagicMock()
        worker_instance.signals.finished.connect = MagicMock()
        worker_instance.signals.progress = MagicMock()
        worker_instance.signals.progress.connect = MagicMock()
        worker_instance.signals.error = MagicMock()
        worker_instance.signals.error.connect = MagicMock()
        MockWorker.return_value = worker_instance

        validation_view.validate_selected()

        MockWorker.assert_called_with(ANY, ["1", "2"])
        validation_view.threadpool.start.assert_called_with(worker_instance)

def test_delete_selected(validation_view):
    """Test deleting selected rows."""
    validation_view.is_read_only = False
    validation_view.get_selected_ids = MagicMock(return_value=["1"])

    with patch.object(vv_module, "CustomMessageDialog") as MockDialog, \
         patch.object(vv_module, "DeleteCertificatesWorker") as MockWorker:

        MockDialog.show_question.return_value = True
        
        worker_instance = MagicMock()
        worker_instance.signals = MagicMock()
        worker_instance.signals.result = MagicMock()
        worker_instance.signals.result.connect = MagicMock()
        worker_instance.signals.finished = MagicMock()
        worker_instance.signals.finished.connect = MagicMock()
        worker_instance.signals.progress = MagicMock()
        worker_instance.signals.progress.connect = MagicMock()
        worker_instance.signals.error = MagicMock()
        worker_instance.signals.error.connect = MagicMock()
        MockWorker.return_value = worker_instance

        validation_view.delete_selected()

        MockWorker.assert_called_with(ANY, ["1"])
        validation_view.threadpool.start.assert_called_with(worker_instance)

def test_edit_data_success(validation_view):
    """Test editing a certificate."""
    validation_view.is_read_only = False
    validation_view.get_selected_ids = MagicMock(return_value=["1"])

    with patch.object(vv_module, "requests") as mock_requests, \
         patch.object(vv_module, "EditCertificatoDialog") as MockDialog, \
         patch.object(vv_module, "CustomMessageDialog"):

        # Configure mock GET response
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = {
            "id": 1, "nome": "ROSSI MARIO", "corso": "CORSO TEST", "categoria": "ANTINCENDIO",
            "data_rilascio": "01/01/2020", "data_scadenza": "01/01/2025"
        }
        mock_get_response.raise_for_status = MagicMock()
        mock_requests.get.return_value = mock_get_response
        
        # Configure mock PUT response
        mock_put_response = MagicMock()
        mock_put_response.raise_for_status = MagicMock()
        mock_requests.put.return_value = mock_put_response

        # Configure dialog mock
        dialog_instance = MockDialog.return_value
        dialog_instance.exec.return_value = True
        dialog_instance.get_data.return_value = {"nome": "ROSSI MARIO UPDATED"}

        validation_view.edit_data()

        mock_requests.put.assert_called()
        put_call_args = mock_requests.put.call_args
        assert "/certificati/1" in put_call_args[0][0]

def test_context_menu_open_pdf(validation_view):
    """Test context menu action 'Apri PDF'."""
    assert validation_view.model.rowCount() == 2

    mock_index = MagicMock()
    mock_index.isValid.return_value = True
    mock_index.row.return_value = 0
    validation_view.table_view.indexAt = MagicMock(return_value=mock_index)

    # Create action mocks that we control
    mock_action_pdf = MagicMock(name="action_pdf")
    mock_action_folder = MagicMock(name="action_folder")

    with patch.object(vv_module, "QMenu") as MockMenu, \
         patch.object(vv_module, "find_document", return_value="/path/to/doc.pdf") as mock_find, \
         patch.object(vv_module, "QDesktopServices") as mock_desktop, \
         patch.object(vv_module, "QAction", side_effect=[mock_action_pdf, mock_action_folder]):

        menu_instance = MockMenu.return_value
        menu_instance.exec.return_value = mock_action_pdf
        menu_instance.addAction = MagicMock()

        validation_view._show_context_menu(QtCore.QPoint(0, 0))

        mock_find.assert_called()
        mock_desktop.openUrl.assert_called()

def test_context_menu_open_folder(validation_view):
    """Test context menu action 'Apri percorso file'."""
    mock_index = MagicMock()
    mock_index.isValid.return_value = True
    mock_index.row.return_value = 0
    validation_view.table_view.indexAt = MagicMock(return_value=mock_index)

    mock_action_pdf = MagicMock(name="action_pdf")
    mock_action_folder = MagicMock(name="action_folder")

    with patch.object(vv_module, "QMenu") as MockMenu, \
         patch.object(vv_module, "find_document", return_value="/path/to/doc.pdf") as mock_find, \
         patch.object(vv_module, "subprocess") as mock_subprocess, \
         patch.object(vv_module, "os") as mock_os, \
         patch.object(vv_module, "QAction", side_effect=[mock_action_pdf, mock_action_folder]):

        menu_instance = MockMenu.return_value
        menu_instance.exec.return_value = mock_action_folder
        menu_instance.addAction = MagicMock()
        
        mock_os.name = 'nt'
        mock_os.path.dirname.return_value = "/path/to"

        validation_view._show_context_menu(QtCore.QPoint(0, 0))

        mock_find.assert_called()
        mock_subprocess.run.assert_called()
        args = mock_subprocess.run.call_args[0][0]
        assert args[0] == 'explorer'

def test_action_completed_success(validation_view):
    """Test handling of successful action completion."""
    with patch.object(vv_module, "CustomMessageDialog") as MockDialog, \
         patch.object(vv_module, "FetchCertificatesWorker"):
        
        validation_view._on_action_completed({"success": 2, "errors": []}, "validate")
        
        MockDialog.show_info.assert_called()

def test_action_completed_with_errors(validation_view):
    """Test handling of action completion with errors."""
    with patch.object(vv_module, "CustomMessageDialog") as MockDialog, \
         patch.object(vv_module, "FetchCertificatesWorker"):
        
        validation_view._on_action_completed({"success": 1, "errors": ["Error 1"]}, "validate")
        
        MockDialog.show_warning.assert_called()