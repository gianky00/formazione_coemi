import sys
import os
from unittest.mock import MagicMock, patch
import pytest
from datetime import date

@pytest.fixture
def mock_api_client():
    client = MagicMock()
    client.get_audit_logs.return_value = [
        {"id": 1, "timestamp": "2023-10-27T10:00:00", "username": "admin", "action": "LOGIN", "details": "Success"}
    ]
    return client

@patch('desktop_app.main_window_ui.load_colored_icon')
@patch('desktop_app.services.license_manager.LicenseManager.get_license_data')
def test_sidebar_license_logic(mock_get_license, mock_load_icon):
    from desktop_app.main_window_ui import Sidebar
    # Mock return value to avoid QPixmap usage
    mock_load_icon.return_value = MagicMock()

    mock_get_license.return_value = {
        "Hardware ID": "12345",
        "Scadenza Licenza": "31/12/2030",
        "Generato il": "01/01/2023"
    }

    sidebar = Sidebar()
    info = sidebar.read_license_info()
    assert info["Hardware ID"] == "12345"
    assert info["Scadenza Licenza"] == "31/12/2030"

    # Check labels
    labels = []
    for i in range(sidebar.license_layout.count()):
        item = sidebar.license_layout.itemAt(i)
        if item.widget():
            labels.append(item.widget().text())
    assert any("termina tra" in t for t in labels)

@patch('desktop_app.main_window_ui.load_colored_icon')
@patch('desktop_app.services.license_manager.LicenseManager.get_license_data')
def test_sidebar_license_legacy_format(mock_get_license, mock_load_icon):
    from desktop_app.main_window_ui import Sidebar
    mock_load_icon.return_value = MagicMock()

    # Mock with YYYY-MM-DD
    mock_get_license.return_value = {
        "Hardware ID": "12345",
        "Scadenza Licenza": "2030-12-31",
        "Generato il": "2023-01-01"
    }

    sidebar = Sidebar()
    # We want to check if "La licenza termina tra" label exists
    labels = []
    for i in range(sidebar.license_layout.count()):
        item = sidebar.license_layout.itemAt(i)
        if item.widget():
            labels.append(item.widget().text())

    assert any("termina tra" in t for t in labels)

@patch('desktop_app.utils.get_asset_path', return_value=None) # Avoid loading logo pixmap
@patch('desktop_app.services.license_manager.LicenseManager.get_license_data')
def test_login_view_instantiation(mock_get_license, mock_get_asset, mock_api_client):
    from desktop_app.views.login_view import LoginView

    mock_get_license.return_value = {"Hardware ID": "Test"}

    view = LoginView(mock_api_client)
    assert view is not None

def test_audit_log_widget(mock_api_client):
    from desktop_app.views.config_view import AuditLogWidget
    widget = AuditLogWidget(mock_api_client)
    widget.refresh_logs()
    mock_api_client.get_audit_logs.assert_called()
