import sys
import pytest
from unittest.mock import patch, MagicMock

def test_database_view_init():
    from desktop_app.views.database_view import DatabaseView

    # Mock internal dependencies
    with patch("desktop_app.views.database_view.DatabaseViewModel") as MockVM, \
         patch("desktop_app.views.database_view.APIClient"):

        view = DatabaseView()
        # Verify it's our DummyQWidget
        assert view is not None
        MockVM.assert_called()

def test_validation_view_init():
    from desktop_app.views.validation_view import ValidationView

    # ValidationView uses requests directly AND APIClient
    # It now uses QThreadPool for loading data
    with patch("desktop_app.views.validation_view.APIClient"), \
         patch("desktop_app.views.validation_view.requests.get") as mock_get, \
         patch("desktop_app.views.validation_view.QThreadPool") as MockThreadPool:

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = []

        view = ValidationView()
        assert view is not None

        # Manually trigger refresh
        view.refresh_data()
        # Should start a worker
        assert MockThreadPool.return_value.start.called

def test_scadenzario_view_init():
    from desktop_app.views.scadenzario_view import ScadenzarioView

    with patch("desktop_app.views.scadenzario_view.APIClient"), \
         patch("desktop_app.views.scadenzario_view.requests.get") as mock_get, \
         patch("desktop_app.views.scadenzario_view.QGraphicsView") as MockQGraphicsView, \
         patch("desktop_app.views.scadenzario_view.QThreadPool") as MockThreadPool:

        mock_instance = MockQGraphicsView.return_value
        mock_instance.viewport.return_value.width.return_value = 800

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = []

        view = ScadenzarioView()
        assert view is not None
        # ScadenzarioView calls load_data in init -> starts worker
        assert MockThreadPool.return_value.start.called

def test_import_view_init():
    from desktop_app.views.import_view import ImportView
    view = ImportView()
    assert view is not None

def test_config_view_init():
    from desktop_app.views.config_view import ConfigView
    from desktop_app.api_client import APIClient

    # Mock the APIClient
    mock_api_client = MagicMock(spec=APIClient)
    mock_api_client.user_info = {'is_admin': True}
    mock_api_client.get_mutable_config.return_value = {}

    # ConfigView uses os.getenv, continue mocking it
    with patch("os.getenv", return_value="test_value"):
        # Pass the mocked client to the constructor
        view = ConfigView(api_client=mock_api_client)
        assert view is not None
        # Basic assertion to ensure the view initialized
        assert view.api_client == mock_api_client

def test_edit_dialog_init():
    from desktop_app.views.edit_dialog import EditCertificatoDialog
    data = {
        "nome": "Mario", "corso": "C1", "categoria": "CAT1",
        "data_rilascio": "01/01/2025", "data_scadenza": "01/01/2026"
    }
    categories = ["CAT1", "CAT2"]
    dialog = EditCertificatoDialog(data, categories)
    assert dialog is not None
    # Test get_data
    res = dialog.get_data()
    assert res['nome'] == "Mario"
