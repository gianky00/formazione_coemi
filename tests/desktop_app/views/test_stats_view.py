import sys
from unittest.mock import MagicMock, patch

# 1. Setup Mocks for PyQt6
from tests.desktop_app import mock_qt
sys.modules["PyQt6"] = mock_qt.mock_modules["PyQt6"]
sys.modules["PyQt6.QtWidgets"] = mock_qt.mock_modules["PyQt6.QtWidgets"]
sys.modules["PyQt6.QtCore"] = mock_qt.mock_modules["PyQt6.QtCore"]
sys.modules["PyQt6.QtGui"] = mock_qt.mock_modules["PyQt6.QtGui"]

# 2. Import the module under test
from desktop_app.views.stats_view import StatsView, StatsWorker

def test_stats_view_initialization():
    mock_api = MagicMock()
    view = StatsView(mock_api)
    
    assert view is not None
    # Check if layout was set
    assert view.layout is not None

def test_refresh_data_starts_worker():
    """Test that refresh_data creates and starts a worker."""
    mock_api = MagicMock()
    view = StatsView(mock_api)
    
    # Mock the worker
    with patch.object(view, '_worker', None):
        view.refresh_data()
        # A worker should have been created
        assert view._worker is not None

def test_on_data_received_updates_kpis():
    """Test that _on_data_received correctly updates the KPIs."""
    mock_api = MagicMock()
    view = StatsView(mock_api)
    
    # Simulate receiving data
    summary = {
        "total_dipendenti": 100,
        "total_certificati": 500,
        "scaduti": 10,
        "in_scadenza": 5,
        "compliance_percent": 95
    }
    compliance_data = [
        {"category": "Sicurezza", "total": 50, "active": 40, "expiring": 5, "expired": 5, "compliance": 80},
        {"category": "Salute", "total": 30, "active": 20, "expiring": 5, "expired": 5, "compliance": 66}
    ]
    
    view._on_data_received(summary, compliance_data)
    
    # Verify KPI updates
    assert view.kpi_total.lbl_value.text() == "100"
    assert view.kpi_certs.lbl_value.text() == "500"
    assert view.kpi_expired.lbl_value.text() == "10"
    assert view.kpi_expiring.lbl_value.text() == "5"
    assert view.kpi_compliance.lbl_value.text() == "95%"

    # Verify Compliance Bars creation
    assert len(view.compliance_layout.widgets) == 2 

def test_on_data_received_empty():
    """Test that empty data doesn't crash."""
    mock_api = MagicMock()
    view = StatsView(mock_api)
    
    # Simulate receiving empty data
    view._on_data_received({}, [])
    
    # Should not crash and KPIs should show default values
    assert view.kpi_total.lbl_value.text() == "0"

def test_refresh_data_failure():
    mock_api = MagicMock()
    view = StatsView(mock_api)
    
    # Should not crash on error
    view._on_error("API Error")
    # No exception raised is success

def test_show_event():
    mock_api = MagicMock()
    view = StatsView(mock_api)
    view.refresh_data = MagicMock()
    
    # Simulate showEvent
    view.showEvent(MagicMock())
    
    view.refresh_data.assert_called_once()

def test_cleanup():
    """Test that cleanup properly stops workers."""
    mock_api = MagicMock()
    view = StatsView(mock_api)
    
    # Mock a running worker
    mock_worker = MagicMock()
    mock_worker.isRunning.return_value = True
    view._worker = mock_worker
    
    view.cleanup()
    
    mock_worker.quit.assert_called()
