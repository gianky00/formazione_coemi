import sys
from unittest.mock import MagicMock, patch

# 1. Setup Mocks for PyQt6
from tests.desktop_app import mock_qt
sys.modules["PyQt6"] = mock_qt.mock_modules["PyQt6"]
sys.modules["PyQt6.QtWidgets"] = mock_qt.mock_modules["PyQt6.QtWidgets"]
sys.modules["PyQt6.QtCore"] = mock_qt.mock_modules["PyQt6.QtCore"]
sys.modules["PyQt6.QtGui"] = mock_qt.mock_modules["PyQt6.QtGui"]

# 2. Import the module under test
from desktop_app.views.stats_view import StatsView

def test_stats_view_initialization():
    mock_api = MagicMock()
    view = StatsView(mock_api)
    
    assert view is not None
    # Check if layout was set
    assert view.layout is not None

def test_refresh_data_success():
    mock_api = MagicMock()
    
    # Mock responses
    mock_api.get.side_effect = [
        # Response for "stats/summary"
        {
            "total_dipendenti": 100,
            "total_certificati": 500,
            "scaduti": 10,
            "in_scadenza": 5,
            "compliance_percent": 95
        },
        # Response for "stats/compliance"
        [
            {"category": "Sicurezza", "total": 50, "compliance": 90},
            {"category": "Salute", "total": 30, "compliance": 40}
        ]
    ]

    view = StatsView(mock_api)
    view.refresh_data()

    # Verify API calls
    assert mock_api.get.call_count == 2
    mock_api.get.assert_any_call("stats/summary")
    mock_api.get.assert_any_call("stats/compliance")

    # Verify KPI updates
    # Note: In mock_qt, QLabel.setText updates ._text attribute if we assume standard behavior, 
    # but the mock implementation might need inspection. 
    # Looking at mock_qt.py: setText sets self._text.
    assert view.kpi_total.lbl_value.text() == "100"
    assert view.kpi_certs.lbl_value.text() == "500"
    assert view.kpi_expired.lbl_value.text() == "15" # 10 + 5
    assert view.kpi_compliance.lbl_value.text() == "95%"

    # Verify Compliance Bars creation
    # The layout should have widgets added.
    # In mock_qt.py, addWidget adds to self.widgets list.
    # The compliance_layout is a QGridLayout.
    assert len(view.compliance_layout.widgets) == 2 

def test_refresh_data_failure():
    mock_api = MagicMock()
    mock_api.get.side_effect = Exception("API Error")

    view = StatsView(mock_api)
    
    # Should not crash
    try:
        view.refresh_data()
    except Exception:
        pytest.fail("refresh_data raised Exception unexpectedly")

def test_show_event():
    mock_api = MagicMock()
    view = StatsView(mock_api)
    view.refresh_data = MagicMock()
    
    # Simulate showEvent
    view.showEvent(MagicMock())
    
    view.refresh_data.assert_called_once()
