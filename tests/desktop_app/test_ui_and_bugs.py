import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta
import sys

# Assicuriamo che desktop_app sia importabile
sys.path.append(".")

def test_toast_manager_singleton():
    from desktop_app.components.toast import ToastManager
    t1 = ToastManager.instance()
    t2 = ToastManager.instance()
    assert t1 is t2

@patch('desktop_app.main_window_ui.load_colored_icon')
@patch('desktop_app.main_window_ui.LicenseManager.get_license_data')
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
