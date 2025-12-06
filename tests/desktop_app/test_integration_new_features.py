import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta
import sys
import importlib

# Helper to ensure we get a real module, not a Mock from previous tests
def reload_ui_modules():
    if 'desktop_app.main_window_ui' in sys.modules:
        # If it's a MagicMock (from leakage), reload() fails. We must delete it.
        del sys.modules['desktop_app.main_window_ui']

    # Also clean up Sidebar if it was imported specifically
    if 'desktop_app.main_window_ui.Sidebar' in sys.modules:
        del sys.modules['desktop_app.main_window_ui.Sidebar']

def test_sidebar_buttons_creation():
    reload_ui_modules()
    # Now import should trigger a fresh load using the current (mocked) PyQt environment
    from desktop_app.main_window_ui import Sidebar

    with patch('desktop_app.main_window_ui.load_colored_icon') as mock_load:
        mock_load.return_value = MagicMock()

        sidebar = Sidebar()
        assert len(sidebar.buttons) > 0
        assert "database" in sidebar.buttons

@patch('desktop_app.main_window_ui.load_colored_icon')
@patch('desktop_app.main_window_ui.LicenseManager.get_license_data')
def test_sidebar_license_logic(mock_get_license, mock_load_icon):
    reload_ui_modules()
    from desktop_app.main_window_ui import Sidebar
    mock_load_icon.return_value = MagicMock()

    mock_get_license.return_value = {
        "Hardware ID": "12345",
        "Scadenza Licenza": "31/12/2030",
        "Generato il": "01/01/2023"
    }

    sidebar = Sidebar()
    info = sidebar.read_license_info()
    assert info["Hardware ID"] == "12345"
    assert sidebar.license_layout.count() > 0

@patch('desktop_app.main_window_ui.load_colored_icon')
@patch('desktop_app.main_window_ui.LicenseManager.get_license_data')
def test_sidebar_license_legacy_format(mock_get_license, mock_load_icon):
    reload_ui_modules()
    from desktop_app.main_window_ui import Sidebar
    mock_load_icon.return_value = MagicMock()

    mock_get_license.return_value = {
        "Hardware ID": "12345",
        "Scadenza Licenza": "2030-12-31",
        "Generato il": "2023-01-01"
    }

    sidebar = Sidebar()
    labels = []
    for i in range(sidebar.license_layout.count()):
        item = sidebar.license_layout.itemAt(i)
        if item.widget():
            labels.append(item.widget().text())

    assert any("termina tra" in t for t in labels)
