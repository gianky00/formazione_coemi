import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta

# Importa Sidebar all'interno dei test per isolamento
# from desktop_app.main_window_ui import Sidebar

def test_sidebar_buttons_creation():
    from desktop_app.main_window_ui import Sidebar
    with patch('desktop_app.main_window_ui.load_colored_icon') as mock_load:
        # Mock QIcon to prevent pixmap errors
        mock_load.return_value = MagicMock()

        sidebar = Sidebar()
        assert len(sidebar.buttons) > 0
        assert "database" in sidebar.buttons
        assert "import" in sidebar.buttons

@patch('desktop_app.main_window_ui.load_colored_icon')
@patch('desktop_app.main_window_ui.LicenseManager.get_license_data')
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

    # Check that labels were added
    # License layout is populated in init
    assert sidebar.license_layout.count() > 0

@patch('desktop_app.main_window_ui.load_colored_icon')
@patch('desktop_app.main_window_ui.LicenseManager.get_license_data')
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
