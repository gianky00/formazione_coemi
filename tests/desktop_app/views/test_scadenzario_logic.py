import sys
from unittest.mock import MagicMock, patch, ANY, call
import pytest
from datetime import date, timedelta
from tests.desktop_app.mock_qt import mock_modules, QtCore

# Apply mocks to sys.modules
for name, mod in mock_modules.items():
    sys.modules[name] = mod

from desktop_app.views.scadenzario_view import ScadenzarioView

@pytest.fixture
def mock_api_client_cls():
    with patch("desktop_app.views.scadenzario_view.APIClient") as MockClass:
        client_instance = MockClass.return_value
        client_instance.base_url = "http://test/api/v1"
        client_instance._get_headers.return_value = {"Authorization": "Bearer token"}
        yield MockClass

@pytest.fixture
def scadenzario_view(mock_api_client_cls):
    with patch("desktop_app.views.scadenzario_view.FetchCertificatesWorker") as MockFetch:
        worker = MockFetch.return_value
        worker.signals.result = MagicMock()
        worker.signals.error = MagicMock()
        worker.signals.finished = MagicMock()

        view = ScadenzarioView() # No args
        # We can inject our mock client instance if we want to control it further,
        # but MockClass.return_value is already global to the fixture scope?
        # view.api_client is the mock instance.
        return view

def test_init(scadenzario_view):
    """Test initialization."""
    assert scadenzario_view is not None
    assert scadenzario_view.gantt_scene is not None
    # Verify default zoom (3.0 months)
    assert scadenzario_view.zoom_months == 3.0

def test_load_data_trigger(scadenzario_view):
    """Test that load_data triggers the worker."""
    scadenzario_view.load_data()
    scadenzario_view.threadpool.start.assert_called()

def test_on_data_loaded_populates_tree(scadenzario_view):
    """Test that loaded data populates the tree widget."""
    # Data format: list of dicts
    today = date.today().strftime("%d/%m/%Y")
    data = [
        {"nome": "ROSSI MARIO", "categoria": "ANTINCENDIO", "stato_certificato": "valido", "data_scadenza": "31/12/2099", "matricola": "123"},
        {"nome": "BIANCHI LUIGI", "categoria": "PRIMO SOCCORSO", "stato_certificato": "in_scadenza", "data_scadenza": today, "matricola": "456"}
    ]

    # We need to mock QTreeWidgetItem to check if items are added.
    # mock_qt mocks QTreeWidgetItem.
    # The view calls QTreeWidgetItem(parent, strings).

    with patch("desktop_app.views.scadenzario_view.QTreeWidgetItem") as MockItem, \
         patch("desktop_app.views.scadenzario_view.GanttBarItem"):
        scadenzario_view._on_data_loaded(data)

        # Check if items were created
        # We expect Categories, Statuses, and Leaves.
        # 2 Categories (ANTINCENDIO, PRIMO SOCCORSO).
        # 2 Statuses (IN SCADENZA/SCADUTI).
        # 2 Leaves.
        assert MockItem.call_count >= 2

def test_update_gantt_chart(scadenzario_view):
    """Test the Gantt chart generation logic."""
    today = date.today()
    exp1 = (today + timedelta(days=10)).strftime("%d/%m/%Y")
    exp2 = (today - timedelta(days=5)).strftime("%d/%m/%Y")

    data = [
        {"nome": "ROSSI MARIO", "categoria": "ANTINCENDIO", "stato_certificato": "in_scadenza", "data_scadenza": exp1, "matricola": "123"},
        {"nome": "BIANCHI LUIGI", "categoria": "PRIMO SOCCORSO", "stato_certificato": "scaduto", "data_scadenza": exp2, "matricola": "456"}
    ]

    # Mock GanttBarItem to verify instantiation
    with patch("desktop_app.views.scadenzario_view.GanttBarItem") as MockBar:
        scadenzario_view._on_data_loaded(data)

        # Check if bars were added to scene.
        # redraw_gantt_scene is called by _on_data_loaded.
        # It adds items to gantt_scene.

        # We expect 2 bars if they are within visible range.
        # Default zoom is 3 months. (-1 to +2 months from today).
        # Both dates are close to today, so they should be visible.
        assert MockBar.call_count >= 1 # At least one should be visible
        # scadenzario_view.gantt_scene is a DummyQGraphicsScene (real object), so addItem is not a mock
        assert len(scadenzario_view.gantt_scene.items()) > 0

def test_export_pdf(scadenzario_view):
    """Test export PDF triggers backend endpoint."""
    # export_to_pdf uses Worker
    with patch("desktop_app.views.scadenzario_view.Worker") as MockWorker, \
         patch("desktop_app.views.scadenzario_view.QFileDialog.getSaveFileName", return_value=("report.pdf", "PDF")) as mock_dialog:

        worker_instance = MockWorker.return_value
        worker_instance.signals.result = MagicMock()

        scadenzario_view.export_to_pdf()

        # Verify Worker was created with a function
        assert MockWorker.called
        func = MockWorker.call_args[0][0]

        # Execute the function to verify it calls requests
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            func()
            mock_get.assert_called()
            assert "/notifications/export-report" in mock_get.call_args[0][0]

def test_send_manual_alert(scadenzario_view):
    """Test manual alert button triggers API via Worker."""
    with patch("desktop_app.views.scadenzario_view.Worker") as MockWorker:
        scadenzario_view.generate_email()

        assert MockWorker.called
        func = MockWorker.call_args[0][0]

        with patch("requests.post") as mock_post:
            func()
            mock_post.assert_called()
            assert "/notifications/send-manual-alert" in mock_post.call_args[0][0]

def test_send_manual_alert_success_handling(scadenzario_view):
    """Test handling of email sent success signal."""
    with patch("desktop_app.views.scadenzario_view.ToastManager.success") as mock_success:
        mock_response = MagicMock()
        mock_response.status_code = 200

        scadenzario_view._on_email_sent(mock_response)
        mock_success.assert_called_with("Successo", ANY, scadenzario_view.window())

def test_zoom_levels(scadenzario_view):
    """Test zoom level changes."""
    # Test update_zoom_from_combo
    # We mock animate_zoom to avoid Qt animation complexity or we mock QVariantAnimation
    with patch.object(scadenzario_view, "animate_zoom") as mock_anim:
        scadenzario_view.update_zoom_from_combo(1) # 6 Mesi
        mock_anim.assert_called_with(6.0)

        scadenzario_view.update_zoom_from_combo(2) # 1 Anno
        mock_anim.assert_called_with(12.0)

def test_read_only_mode(scadenzario_view):
    """Test read only mode disables manual alert."""
    scadenzario_view.set_read_only(True)

    # Check flag
    assert scadenzario_view.is_read_only is True

    # Check button disabled (via mock)
    # generate_email_button is AnimatedButton (inherits QPushButton/QWidget)
    # Mock doesn't store state, but we can verify setEnabled was called
    # But wait, AnimatedButton is imported. Is it mocked?
    # desktop_app.components.animated_widgets.AnimatedButton
    # We mocked qt modules, but custom widgets might be real if not patched.
    # mock_qt mocks 'PyQt6.QtWidgets', so AnimatedButton inheriting from QPushButton will inherit from DummyQWidget.
    # So we can't easily check 'enabled' property unless we spy setEnabled.

    # We can test that generate_email returns early
    with patch("desktop_app.views.scadenzario_view.Worker") as MockWorker:
        scadenzario_view.generate_email()
        MockWorker.assert_not_called()
