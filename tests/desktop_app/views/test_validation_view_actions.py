import sys
from unittest.mock import MagicMock, patch, ANY
import pytest
import pandas as pd
from tests.desktop_app.mock_qt import mock_modules, QtCore

# Apply mocks to sys.modules
for name, mod in mock_modules.items():
    sys.modules[name] = mod

from desktop_app.views.validation_view import ValidationView

@pytest.fixture
def api_client():
    client = MagicMock()
    client.access_token = "fake_token"
    client.base_url = "http://test/api/v1"
    client._get_headers.return_value = {"Authorization": "Bearer fake_token"}
    return client

@pytest.fixture
def validation_view(api_client):
    # Mock FetchCertificatesWorker to prevent immediate thread start or side effects
    with patch("desktop_app.views.validation_view.FetchCertificatesWorker") as MockFetch:
        worker = MockFetch.return_value
        worker.signals.result = MagicMock()
        worker.signals.error = MagicMock()
        worker.signals.finished = MagicMock()

        view = ValidationView(api_client=api_client)
        # Manually trigger data loaded to populate table
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
    # Verify model is set
    assert validation_view.table_view.setModel_called

def test_load_data_error(validation_view):
    """Test error handling during data load."""
    with patch("desktop_app.views.validation_view.CustomMessageDialog.show_error") as mock_error:
        validation_view._on_error("Network Error")
        mock_error.assert_called_with(validation_view, "Errore di Connessione", ANY)
        # Should empty the table
        assert validation_view.df.empty

def test_validate_selected(validation_view):
    """Test validating selected rows."""
    # Ensure view is not read-only
    validation_view.is_read_only = False

    # Mock selection
    validation_view.get_selected_ids = MagicMock(return_value=["1", "2"])

    with patch("desktop_app.views.validation_view.CustomMessageDialog.show_question", return_value=True), \
         patch("desktop_app.views.validation_view.ValidateCertificatesWorker") as MockWorker:

        worker_instance = MockWorker.return_value
        worker_instance.signals.result = MagicMock()
        worker_instance.signals.finished = MagicMock()
        worker_instance.signals.progress = MagicMock()
        worker_instance.signals.error = MagicMock()

        validation_view.validate_selected()

        MockWorker.assert_called_with(ANY, ["1", "2"])
        # ValidationView starts the thread. Since QThreadPool is mocked, it does nothing unless we mock it to run.
        # But we check that the worker was created and added to pool.
        validation_view.threadpool.start.assert_called_with(worker_instance)

        # Simulate worker success
        validation_view._on_action_completed({"success": 2, "errors": []}, "validate")

        # Should reload data
        # Check that start was called at least once more (total > 1)
        assert validation_view.threadpool.start.call_count > 1

def test_delete_selected(validation_view):
    """Test deleting selected rows."""
    validation_view.is_read_only = False
    validation_view.get_selected_ids = MagicMock(return_value=["1"])

    with patch("desktop_app.views.validation_view.CustomMessageDialog.show_question", return_value=True), \
         patch("desktop_app.views.validation_view.DeleteCertificatesWorker") as MockWorker:

        worker_instance = MockWorker.return_value
        worker_instance.signals.result = MagicMock()
        worker_instance.signals.finished = MagicMock()
        worker_instance.signals.progress = MagicMock()
        worker_instance.signals.error = MagicMock()

        validation_view.delete_selected()

        MockWorker.assert_called_with(ANY, ["1"])
        validation_view.threadpool.start.assert_called_with(worker_instance)

def test_edit_data_success(validation_view):
    """Test editing a certificate."""
    validation_view.get_selected_ids = MagicMock(return_value=["1"])

    # Mock requests.get and requests.put
    with patch("requests.get") as mock_get, \
         patch("requests.put") as mock_put, \
         patch("desktop_app.views.validation_view.EditCertificatoDialog") as MockDialog:

        # Setup Get
        mock_get.return_value.json.return_value = {
            "id": 1,
            "nome": "ROSSI MARIO",
            "corso": "CORSO TEST",
            "categoria": "ANTINCENDIO", # Add categoria
            "data_rilascio": "01/01/2020",
            "data_scadenza": "01/01/2025"
        }
        mock_get.return_value.raise_for_status = MagicMock()

        # Setup Dialog
        dialog_instance = MockDialog.return_value
        dialog_instance.exec.return_value = True
        dialog_instance.get_data.return_value = {"nome": "ROSSI MARIO UPDATED"}

        # Setup Put
        mock_put.return_value.raise_for_status = MagicMock()

        validation_view.edit_data()

        mock_put.assert_called()
        # Should reload data
        validation_view.threadpool.start.assert_called()

def test_context_menu_open_pdf(validation_view):
    """Test context menu action 'Apri PDF'."""
    # Mock indexAt to return valid index
    mock_index = MagicMock()
    mock_index.isValid.return_value = True
    mock_index.row.return_value = 0
    validation_view.table_view.indexAt = MagicMock(return_value=mock_index)

    # Use strict patching to ensure we capture the calls
    with patch("desktop_app.views.validation_view.QMenu") as MockMenu, \
         patch("desktop_app.views.validation_view.QAction") as MockAction, \
         patch("desktop_app.views.validation_view.find_document", return_value="/path/to/doc.pdf") as mock_find, \
         patch("desktop_app.views.validation_view.QDesktopServices.openUrl") as mock_open_url:

        # We need distinct actions for PDF and Folder
        action_pdf = MagicMock()
        action_folder = MagicMock()
        MockAction.side_effect = [action_pdf, action_folder]

        menu_instance = MockMenu.return_value
        menu_instance.exec.return_value = action_pdf

        # Trigger
        validation_view._show_context_menu(QtCore.QPoint(0,0))

        mock_find.assert_called()
        mock_open_url.assert_called()

def test_context_menu_open_folder(validation_view):
    """Test context menu action 'Apri percorso file'."""
    mock_index = MagicMock()
    mock_index.isValid.return_value = True
    mock_index.row.return_value = 0
    validation_view.table_view.indexAt = MagicMock(return_value=mock_index)

    with patch("desktop_app.views.validation_view.QMenu") as MockMenu, \
         patch("desktop_app.views.validation_view.QAction") as MockAction, \
         patch("desktop_app.views.validation_view.find_document", return_value="/path/to/doc.pdf"), \
         patch("desktop_app.views.validation_view.subprocess.run") as mock_subprocess, \
         patch("os.name", "nt"): # Simulate Windows

        action_pdf = MagicMock()
        action_folder = MagicMock()
        MockAction.side_effect = [action_pdf, action_folder]

        menu_instance = MockMenu.return_value
        menu_instance.exec.return_value = action_folder

        validation_view._show_context_menu(QtCore.QPoint(0,0))

        # Check call using ANY for args if necessary, but robust check is better
        mock_subprocess.assert_called()
        args = mock_subprocess.call_args[0][0]
        assert args[0] == 'explorer'
        assert args[2] == "/path/to/doc.pdf"

def test_read_only_mode(validation_view):
    """Test that buttons are disabled in read-only mode."""
    validation_view.set_read_only(True)

    # Assert disabled
    assert validation_view.is_read_only is True

    # Test perform action is blocked
    # edit_data checks read_only
    with patch("desktop_app.views.validation_view.EditCertificatoDialog") as MockDialog:
        validation_view.edit_data()
        MockDialog.assert_not_called()

    # delete_selected checks read_only
    with patch("desktop_app.views.validation_view.CustomMessageDialog.show_question") as mock_q:
        validation_view.delete_selected()
        mock_q.assert_not_called()
