import sys
import os
from unittest.mock import MagicMock, patch
import pytest
from datetime import date

# Apply mocks BEFORE importing any PyQt modules
from tests.desktop_app.mock_qt import mock_qt_modules

modules = mock_qt_modules()
for name, mod in modules.items():
    sys.modules[name] = mod

# Now safe to import
from desktop_app.main_window_ui import Sidebar
from desktop_app.views.login_view import LoginView
from desktop_app.views.config_view import AuditLogWidget

@pytest.fixture
def mock_api_client():
    client = MagicMock()
    client.get_audit_logs.return_value = [
        {"id": 1, "timestamp": "2023-10-27T10:00:00", "username": "admin", "action": "LOGIN", "details": "Success"}
    ]
    return client

@patch('desktop_app.main_window_ui.load_colored_icon')
def test_sidebar_license_logic(mock_load_icon):
    # Mock return value to avoid QPixmap usage
    mock_load_icon.return_value = MagicMock()

    # Mock detailed_licenza.txt
    content = """Hardware ID: 12345
Scadenza Licenza: 31/12/2030
Generato il: 01/01/2023
"""
    with open("dettagli_licenza.txt", "w") as f:
        f.write(content)

    try:
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
    finally:
        if os.path.exists("dettagli_licenza.txt"):
            os.remove("dettagli_licenza.txt")

@patch('desktop_app.main_window_ui.load_colored_icon')
def test_sidebar_license_legacy_format(mock_load_icon):
    mock_load_icon.return_value = MagicMock()

    # Mock detailed_licenza.txt with YYYY-MM-DD
    content = """Hardware ID: 12345
Scadenza Licenza: 2030-12-31
Generato il: 2023-01-01
"""
    with open("dettagli_licenza.txt", "w") as f:
        f.write(content)

    try:
        sidebar = Sidebar()
        # We want to check if "La licenza termina tra" label exists
        labels = []
        for i in range(sidebar.license_layout.count()):
            item = sidebar.license_layout.itemAt(i)
            if item.widget():
                labels.append(item.widget().text())

        # This assertion is expected to FAIL currently because parsing fails
        assert any("termina tra" in t for t in labels)

    finally:
        if os.path.exists("dettagli_licenza.txt"):
            os.remove("dettagli_licenza.txt")

@patch('desktop_app.utils.get_asset_path', return_value=None) # Avoid loading logo pixmap
def test_login_view_instantiation(mock_get_asset, mock_api_client):
    # Just check if it crashes
    with open("dettagli_licenza.txt", "w") as f:
        f.write("Hardware ID: Test")
    try:
        view = LoginView(mock_api_client)
        assert view is not None
    finally:
        if os.path.exists("dettagli_licenza.txt"):
            os.remove("dettagli_licenza.txt")

def test_audit_log_widget(mock_api_client):
    widget = AuditLogWidget(mock_api_client)
    widget.refresh_logs()
    mock_api_client.get_audit_logs.assert_called()
