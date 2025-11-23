import sys
import pytest
from unittest.mock import patch, MagicMock

def test_dashboard_view_init():
    from desktop_app.views.dashboard_view import DashboardView

    # Mock internal dependencies
    with patch("desktop_app.views.dashboard_view.DashboardViewModel") as MockVM, \
         patch("desktop_app.views.dashboard_view.APIClient"):

        view = DashboardView()
        # Verify it's our DummyQWidget
        assert view is not None
        MockVM.assert_called()

def test_validation_view_init():
    from desktop_app.views.validation_view import ValidationView

    # ValidationView uses requests directly AND APIClient
    with patch("desktop_app.views.validation_view.APIClient"), \
         patch("desktop_app.views.validation_view.requests.get") as mock_get:

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = []

        view = ValidationView()
        assert view is not None

        # Manually trigger refresh
        view.refresh_data()
        mock_get.assert_called()

def test_scadenzario_view_init():
    from desktop_app.views.scadenzario_view import ScadenzarioView

    with patch("desktop_app.views.scadenzario_view.APIClient"), \
         patch("desktop_app.views.scadenzario_view.requests.get") as mock_get:

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = []

        view = ScadenzarioView()
        assert view is not None
        # ScadenzarioView calls load_data in init
        mock_get.assert_called()

def test_import_view_init():
    from desktop_app.views.import_view import ImportView
    view = ImportView()
    assert view is not None

def test_config_view_init():
    from desktop_app.views.config_view import ConfigView
    # ConfigView uses os.getenv
    with patch("os.getenv", return_value="test_value"):
        view = ConfigView()
        assert view is not None
        # Check if it tried to set text
        # Since DummyQWidget.setText updates _text, and ConfigView sets it from env
        assert view.gemini_api_key_input.text() == "test_value"

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
