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
    # Mock FetchCertificatesWorker at the destination to ensure it's captured
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
    # Patch at source for method (works for imported classes)
    with patch("desktop_app.components.custom_dialog.CustomMessageDialog.show_error") as mock_error:
        validation_view._on_error("Network Error")
        mock_error.assert_called_with(validation_view, "Errore di Connessione", ANY)
        assert validation_view.df.empty

def test_validate_selected(validation_view):
    """Test validating selected rows."""
    validation_view.is_read_only = False
    validation_view.get_selected_ids = MagicMock(return_value=["1", "2"])

    # Patch at DESTINATION for classes and functions
    with patch("desktop_app.views.validation_view.CustomMessageDialog.show_question", return_value=True), \
         patch("desktop_app.views.validation_view.ValidateCertificatesWorker") as MockWorker:

        worker_instance = MockWorker.return_value
        worker_instance.signals.result = MagicMock()
        worker_instance.signals.finished = MagicMock()
        worker_instance.signals.progress = MagicMock()
        worker_instance.signals.error = MagicMock()

        validation_view.validate_selected()

        MockWorker.assert_called_with(ANY, ["1", "2"])
        validation_view.threadpool.start.assert_called_with(worker_instance)

        # Simulate worker success
        validation_view._on_action_completed({"success": 2, "errors": []}, "validate")
        # Check reload triggered
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
    validation_view.is_read_only = False
    validation_view.get_selected_ids = MagicMock(return_value=["1"])

    with patch("requests.get") as mock_get, \
         patch("requests.put") as mock_put, \
         patch("desktop_app.views.validation_view.EditCertificatoDialog") as MockDialog:

        mock_get.return_value.json.return_value = {
            "id": 1, "nome": "ROSSI MARIO", "corso": "CORSO TEST", "categoria": "ANTINCENDIO",
            "data_rilascio": "01/01/2020", "data_scadenza": "01/01/2025"
        }
        mock_get.return_value.raise_for_status = MagicMock()

        dialog_instance = MockDialog.return_value
        dialog_instance.exec.return_value = True
        dialog_instance.get_data.return_value = {"nome": "ROSSI MARIO UPDATED"}

        mock_put.return_value.raise_for_status = MagicMock()

        validation_view.edit_data()

        mock_put.assert_called()
        validation_view.threadpool.start.assert_called()

def test_context_menu_open_pdf(validation_view):
    """Test context menu action 'Apri PDF'."""
    # Ensure model has rows
    assert validation_view.model.rowCount() == 2

    mock_index = MagicMock()
    mock_index.isValid.return_value = True
    mock_index.row.return_value = 0
    validation_view.table_view.indexAt = MagicMock(return_value=mock_index)

    # Patch at destination!
    with patch("desktop_app.views.validation_view.QMenu") as MockMenu, \
         patch("desktop_app.views.validation_view.find_document", return_value="/path/to/doc.pdf") as mock_find, \
         patch("desktop_app.views.validation_view.QDesktopServices.openUrl") as mock_open_url:

        # Create explicit action objects to return
        action_pdf = MagicMock(name="action_pdf")

        # When QMenu(self) is called, return mock
        menu_instance = MockMenu.return_value
        # When menu.exec is called, return action_pdf
        menu_instance.exec.return_value = action_pdf

        # We need to trick the view logic:
        # open_pdf_action = QAction("Apri PDF", self)
        # if action == open_pdf_action: ...

        # The view instantiates QAction. We mock QAction class.
        # But we need to know WHICH instance is which.
        # Easier approach: Use a side_effect on QAction constructor to capture the instances,
        # OR just rely on the fact that if we return `action_pdf` from exec,
        # we need `open_pdf_action` variable in view to equal `action_pdf`.

        # If we patch QAction, `open_pdf_action` will be a MagicMock (instance 1).
        # We need `menu.exec` to return THAT instance.

        # Strategy: Don't patch QAction. Let it be the Mock from mock_qt.
        # But wait, ValidationView imports QAction from QtWidgets.
        # mock_qt puts MagicMock in sys.modules['PyQt6.QtWidgets'].
        # So QAction IS a MagicMock class.

        # Issue: `open_pdf_action = QAction(...)` creates a NEW mock instance.
        # `menu.exec(...)` returns `action_pdf` (our pre-defined mock).
        # They are different objects. `if action == open_pdf_action` fails.

        # Fix: We must patch QAction in the view to return the object we want,
        # OR we capture the created actions.

        with patch("desktop_app.views.validation_view.QAction") as PatchedQAction:
            # Side effect to return specific mocks for the two calls
            mock_action_pdf = MagicMock(name="pdf")
            mock_action_folder = MagicMock(name="folder")
            PatchedQAction.side_effect = [mock_action_pdf, mock_action_folder]

            menu_instance.exec.return_value = mock_action_pdf

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
         patch("desktop_app.views.validation_view.find_document", return_value="/path/to/doc.pdf"), \
         patch("desktop_app.views.validation_view.subprocess.run") as mock_subprocess, \
         patch("os.name", "nt"), \
         patch("desktop_app.views.validation_view.QAction") as PatchedQAction:

        mock_action_pdf = MagicMock(name="pdf")
        mock_action_folder = MagicMock(name="folder")
        PatchedQAction.side_effect = [mock_action_pdf, mock_action_folder]

        menu_instance = MockMenu.return_value
        menu_instance.exec.return_value = mock_action_folder

        validation_view._show_context_menu(QtCore.QPoint(0,0))

        mock_subprocess.assert_called()
        args = mock_subprocess.call_args[0][0]
        assert args[0] == 'explorer'
