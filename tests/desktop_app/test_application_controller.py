import sys
from unittest.mock import MagicMock, patch
import pytest

# Apply Mocks
from tests.desktop_app.mock_qt import mock_modules

class TestApplicationController:
    @pytest.fixture
    def controller(self):
        old_modules = sys.modules.copy()
        sys.modules.update(mock_modules)

        from desktop_app.main import ApplicationController

        with patch("desktop_app.main.APIClient"), \
             patch("desktop_app.main.IPCBridge"), \
             patch("desktop_app.main.MasterWindow"), \
             patch("desktop_app.main.LoginView"):

            ctrl = ApplicationController()
            # Manually mock the master_window if patch didn't link it correctly to self
            ctrl.master_window = MagicMock()
            ctrl.api_client = MagicMock()
            yield ctrl

        sys.modules.clear()
        sys.modules.update(old_modules)

    def test_start_shows_login(self, controller):
        controller.start()
        controller.master_window.showMaximized.assert_called_once()

    def test_on_login_success(self, controller):
        user_info = {
            "username": "test",
            "account_name": "Test User",
            "read_only": True,
            "previous_login": "2024-01-01T10:00:00"
        }

        # Use string patching now that module is in sys.modules
        with patch("desktop_app.main.MainDashboardWidget") as MockDash:
            mock_dash = MockDash.return_value
            mock_dash.sidebar = MagicMock()

            controller.on_login_success(user_info)

            MockDash.assert_called_once()
            mock_dash.set_read_only_mode.assert_called_with(True)
            mock_dash.sidebar.set_user_info.assert_called_with("Test User", "01/01/2024\n10:00")
            controller.master_window.show_dashboard.assert_called_with(mock_dash)

    def test_analyze_path(self, controller):
        controller.dashboard = MagicMock()
        controller.dashboard.is_read_only = False

        controller.analyze_path("/path/to/analyze")
        controller.dashboard.analyze_path.assert_called_with("/path/to/analyze")

    def test_analyze_path_read_only(self, controller):
        controller.dashboard = MagicMock()
        controller.dashboard.is_read_only = True

        with patch("desktop_app.main.QMessageBox") as MockBox:
            controller.analyze_path("/path")
            controller.dashboard.analyze_path.assert_not_called()
            MockBox.warning.assert_called()

    def test_analyze_path_pending(self, controller):
        controller.dashboard = None
        controller.analyze_path("/path")
        assert controller.pending_action == {"action": "analyze", "path": "/path"}

    def test_import_csv(self, controller):
        controller.dashboard = MagicMock()
        controller.dashboard.is_read_only = False

        controller.api_client.import_dipendenti_csv.return_value = {"message": "Success", "warnings": []}

        with patch("desktop_app.main.QMessageBox") as MockBox:
            controller.import_dipendenti_csv("/file.csv")
            controller.api_client.import_dipendenti_csv.assert_called_with("/file.csv")
            MockBox.information.assert_called()
