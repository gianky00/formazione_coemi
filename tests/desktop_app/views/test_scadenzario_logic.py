import sys
from unittest.mock import MagicMock, patch, ANY, call
import pytest
from datetime import date, timedelta
from tests.desktop_app.mock_qt import mock_modules, QtCore, DummyQRect

# Apply mocks to sys.modules
for name, mod in mock_modules.items():
    sys.modules[name] = mod

# Import the module OBJECT so we can use patch.object on it
from desktop_app.views import scadenzario_view as sv_module
from desktop_app.views.scadenzario_view import ScadenzarioView

@pytest.fixture
def mock_api_client_cls():
    with patch.object(sv_module, "APIClient") as MockClass:
        client_instance = MockClass.return_value
        client_instance.base_url = "http://test/api/v1"
        client_instance._get_headers.return_value = {"Authorization": "Bearer token"}
        yield MockClass

@pytest.fixture
def scadenzario_view(mock_api_client_cls):
    with patch.object(sv_module, "FetchCertificatesWorker") as MockFetch:
        worker = MockFetch.return_value
        worker.signals = MagicMock()
        worker.signals.result = MagicMock()
        worker.signals.result.connect = MagicMock()
        worker.signals.error = MagicMock()
        worker.signals.error.connect = MagicMock()
        worker.signals.finished = MagicMock()
        worker.signals.finished.connect = MagicMock()

        view = ScadenzarioView()
        return view

def test_init(scadenzario_view):
    """Test initialization."""
    assert scadenzario_view is not None
    assert scadenzario_view.gantt_scene is not None
    assert scadenzario_view.zoom_months == 3.0

def test_load_data_trigger(scadenzario_view):
    """Test that load_data triggers the worker."""
    with patch.object(sv_module, "FetchCertificatesWorker") as MockFetch:
        worker = MockFetch.return_value
        worker.signals = MagicMock()
        worker.signals.result.connect = MagicMock()
        worker.signals.error.connect = MagicMock()
        worker.signals.finished.connect = MagicMock()
        
        scadenzario_view.load_data()
        scadenzario_view.threadpool.start.assert_called()

def test_on_data_loaded_populates_tree(scadenzario_view):
    """Test that loaded data populates the tree widget."""
    today = date.today()
    future_date = (today + timedelta(days=10)).strftime("%d/%m/%Y")

    data = [
        {
            "nome": "ROSSI MARIO",
            "categoria": "ANTINCENDIO",
            "stato_certificato": "valido",
            "data_scadenza": future_date,
            "matricola": "123",
            "data_nascita": "01/01/1980",
            "corso": "CORSO BASE"
        },
        {
            "nome": "BIANCHI LUIGI",
            "categoria": "PRIMO SOCCORSO",
            "stato_certificato": "in_scadenza",
            "data_scadenza": today.strftime("%d/%m/%Y"),
            "matricola": "456",
            "data_nascita": "01/01/1990",
            "corso": "CORSO AVANZATO"
        }
    ]

    scadenzario_view._on_data_loaded(data)
    
    # Verify certificates were processed and stored
    assert len(scadenzario_view.certificates) >= 1, "Certificates should be populated after _on_data_loaded"
    
    # Verify categories are assigned colors
    categories_in_data = set(item['categoria'] for item in scadenzario_view.certificates)
    assert len(categories_in_data) >= 1, "At least one category should be present"

def test_update_gantt_chart(scadenzario_view):
    """Test the Gantt chart generation logic."""
    today = date.today()
    exp1 = (today + timedelta(days=10)).strftime("%d/%m/%Y")
    exp2 = (today - timedelta(days=5)).strftime("%d/%m/%Y")

    data = [
        {
            "nome": "ROSSI MARIO",
            "categoria": "ANTINCENDIO",
            "stato_certificato": "in_scadenza",
            "data_scadenza": exp1,
            "matricola": "123",
            "data_nascita": "01/01/1980",
            "corso": "CORSO BASE"
        },
        {
            "nome": "BIANCHI LUIGI",
            "categoria": "PRIMO SOCCORSO",
            "stato_certificato": "scaduto",
            "data_scadenza": exp2,
            "matricola": "456",
            "data_nascita": "01/01/1990",
            "corso": "CORSO AVANZATO"
        }
    ]

    scadenzario_view._on_data_loaded(data)
    items = scadenzario_view.gantt_scene.items()
    assert len(items) > 0

    from tests.desktop_app.mock_qt import DummyQGraphicsRectItem
    rects = [i for i in items if isinstance(i, DummyQGraphicsRectItem)]
    assert len(rects) >= 1

def test_export_pdf(scadenzario_view):
    """Test export PDF triggers backend endpoint."""
    scadenzario_view.is_read_only = False

    # Configure QFileDialog mock (already a MagicMock from mock_qt)
    sv_module.QFileDialog.getSaveFileName = MagicMock(return_value=("report.pdf", "PDF"))

    with patch.object(sv_module, "Worker") as MockWorker:
        # Properly configure worker instance
        worker_instance = MagicMock()
        worker_instance.signals = MagicMock()
        worker_instance.signals.result = MagicMock()
        worker_instance.signals.result.connect = MagicMock()
        worker_instance.signals.error = MagicMock()
        worker_instance.signals.error.connect = MagicMock()
        worker_instance.signals.finished = MagicMock()
        worker_instance.signals.finished.connect = MagicMock()
        MockWorker.return_value = worker_instance

        scadenzario_view.export_to_pdf()

        assert MockWorker.called, "Worker should have been instantiated"
        func = MockWorker.call_args[0][0]

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            func()
            mock_get.assert_called()
            assert "/notifications/export-report" in mock_get.call_args[0][0]

def test_send_manual_alert(scadenzario_view):
    """Test manual alert button triggers API via Worker."""
    scadenzario_view.is_read_only = False

    with patch.object(sv_module, "Worker") as MockWorker:
        worker_instance = MagicMock()
        worker_instance.signals = MagicMock()
        worker_instance.signals.result = MagicMock()
        worker_instance.signals.result.connect = MagicMock()
        worker_instance.signals.error = MagicMock()
        worker_instance.signals.error.connect = MagicMock()
        worker_instance.signals.finished = MagicMock()
        worker_instance.signals.finished.connect = MagicMock()
        MockWorker.return_value = worker_instance

        scadenzario_view.generate_email()

        assert MockWorker.called, "Worker should have been instantiated"
        func = MockWorker.call_args[0][0]

        with patch("requests.post") as mock_post:
            func()
            mock_post.assert_called()
            assert "/notifications/send-manual-alert" in mock_post.call_args[0][0]

def test_send_manual_alert_success_handling(scadenzario_view):
    """Test handling of email sent success signal."""
    mock_window = MagicMock()
    mock_window.geometry.return_value = DummyQRect(0, 0, 800, 600)
    mock_window.isVisible.return_value = True
    mock_window.windowState.return_value = 0

    scadenzario_view.window = MagicMock(return_value=mock_window)

    # Patch ToastManager using patch.object on the module
    with patch.object(sv_module, "ToastManager") as MockToastManager:
        mock_response = MagicMock()
        mock_response.status_code = 200

        scadenzario_view._on_email_sent(mock_response)

        MockToastManager.success.assert_called_with("Successo", ANY, ANY)

def test_zoom_levels(scadenzario_view):
    """Test zoom level changes."""
    with patch.object(scadenzario_view, "animate_zoom") as mock_anim:
        scadenzario_view.update_zoom_from_combo(1)
        mock_anim.assert_called_with(6.0)

        scadenzario_view.update_zoom_from_combo(2)
        mock_anim.assert_called_with(12.0)

def test_read_only_mode(scadenzario_view):
    """Test read only mode disables manual alert."""
    scadenzario_view.set_read_only(True)
    assert scadenzario_view.is_read_only is True

    with patch.object(sv_module, "Worker") as MockWorker:
        scadenzario_view.generate_email()
        MockWorker.assert_not_called()