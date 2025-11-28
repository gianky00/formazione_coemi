
import sys
import unittest
from unittest.mock import MagicMock, patch

# --- 1. MOCK QT MODULES BEFORE IMPORTING APP CODE ---
from tests.desktop_app.mock_qt import mock_qt_modules

# Patch sys.modules with mocked PyQt6 modules
modules_to_patch = mock_qt_modules()
sys.modules.update(modules_to_patch)

# --- 2. IMPORT APP CODE ---
# We must import after patching
from desktop_app.main import ApplicationController
from desktop_app.api_client import APIClient
from desktop_app.views.import_view import ImportView
from desktop_app.views.database_view import DatabaseView

class TestReadOnlyEnforcement(unittest.TestCase):

    def setUp(self):
        # Mock API Client
        self.mock_api = MagicMock(spec=APIClient)
        self.mock_api.base_url = "http://mock-api"

        # Patch APIClient instantiation in ApplicationController
        with patch('desktop_app.main.APIClient', return_value=self.mock_api):
            with patch('desktop_app.main.MasterWindow'): # Mock window to avoid complex init
                self.controller = ApplicationController()
                # Mock MasterWindow instance attached to controller
                self.controller.master_window = MagicMock()

    def test_propagation_of_read_only_mode(self):
        """
        Verifies that on_login_success(read_only=True) calls set_read_only_mode(True)
        on the dashboard.
        """
        # Mock user info with read_only=True
        user_info = {
            "username": "testuser",
            "read_only": True
        }

        # Mock Dashboard creation
        mock_dashboard = MagicMock()
        self.controller.dashboard = mock_dashboard

        # ACT: Call on_login_success
        self.controller.on_login_success(user_info)

        # ASSERT: set_read_only_mode should be called with True
        mock_dashboard.set_read_only_mode.assert_called_with(True)

    def test_import_view_disables_controls(self):
        """
        Verifies that ImportView.set_read_only(True) disables specific controls
        and sets tooltips.
        """
        # Create ImportView (headless via mocks)
        with patch('desktop_app.views.import_view.APIClient', return_value=self.mock_api):
            import_view = ImportView()

            # Setup mocks for children
            import_view.drop_zone = MagicMock()
            import_view.drop_zone.select_folder_button = MagicMock()
            import_view.results_display = MagicMock()

            # ACT: Set Read Only
            import_view.set_read_only(True)

            # ASSERT: Controls Disabled
            import_view.drop_zone.select_folder_button.setEnabled.assert_called_with(False)
            import_view.drop_zone.setAcceptDrops.assert_called_with(False)

            # ASSERT: Tooltips Set (Standardized)
            import_view.drop_zone.select_folder_button.setToolTip.assert_called_with("Database in sola lettura")
            import_view.drop_zone.setToolTip.assert_called_with("Database in sola lettura")

    def test_backend_permission_check(self):
        """
        Verifies that the backend dependency check_write_permission raises 503
        when db_security.is_read_only is True.
        """
        # This requires importing the backend dependency code
        from app.api.deps import check_write_permission
        from fastapi import HTTPException

        # Patch db_security
        with patch('app.api.deps.db_security') as mock_db_sec:
            mock_db_sec.is_read_only = True

            # ACT & ASSERT
            with self.assertRaises(HTTPException) as cm:
                check_write_permission()

            self.assertEqual(cm.exception.status_code, 503)
            self.assertEqual(cm.exception.detail, "Database in sola lettura. Operazione non consentita.")

    def test_application_controller_blocks_analysis(self):
        """
        Verifies that ApplicationController blocks analyze_path if dashboard is read-only.
        """
        # Set up controller with a mocked dashboard that is read-only
        mock_dashboard = MagicMock()
        mock_dashboard.is_read_only = True
        self.controller.dashboard = mock_dashboard

        # Patch QMessageBox to check warning
        with patch('desktop_app.main.QMessageBox') as mock_msg:
             # ACT
             self.controller.analyze_path("some/path.pdf")

             # ASSERT
             mock_msg.warning.assert_called()
             # Ensure analyze_path was NOT called on dashboard
             mock_dashboard.analyze_path.assert_not_called()

if __name__ == '__main__':
    unittest.main()
