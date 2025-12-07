import sys
import unittest
import importlib
import types
from unittest.mock import MagicMock, patch

# Inject mocks - MUST BE DONE BEFORE IMPORTING APP MODULES
from tests.desktop_app.mock_qt import mock_qt_modules
sys.modules.update(mock_qt_modules())

# Force reload of modules that might have been imported by other tests with real PyQt
# Use 'from' imports to ensure we have the module objects directly, avoiding AttributeError on package access
from desktop_app.components import animated_widgets, custom_dialog
from desktop_app.views import login_view

# Wrap reload in try/except to handle CI environments where modules might not be in sys.modules yet
# or might be imported as something else (TypeError)
for module in [animated_widgets, custom_dialog, login_view]:
    try:
        if isinstance(module, types.ModuleType):
            importlib.reload(module)
    except (ImportError, TypeError):
        pass

from PyQt6.QtWidgets import QMessageBox
from desktop_app.views.login_view import LoginView

class TestLoginViewCoverage(unittest.TestCase):
    def setUp(self):
        self.mock_api_client = MagicMock()
        self.mock_api_client.user_info = {}
        
        # Patch heavy components
        self.neural_patcher = patch('desktop_app.views.login_view.NeuralNetwork3D')
        self.MockNeural = self.neural_patcher.start()
        
        # Patch License Manager
        self.license_patcher = patch('desktop_app.views.login_view.LicenseManager')
        self.MockLicenseManager = self.license_patcher.start()
        self.MockLicenseManager.get_license_data.return_value = {"Hardware ID": "HWID_123"}
        self.MockLicenseManager.is_license_expiring_soon.return_value = False

        # Patch Hardware ID
        self.hwid_patcher = patch('desktop_app.views.login_view.get_machine_id', return_value="HWID_123")
        self.hwid_patcher.start()

        # Patch paths
        self.path_patcher = patch('desktop_app.views.login_view.get_asset_path', return_value=None)
        self.path_patcher.start()
        
        # Patch QThreadPool
        self.pool_patcher = patch('desktop_app.views.login_view.QThreadPool')
        self.pool_patcher.start()
        
        # Stop auto update timer to avoid side effects
        self.timer_patcher = patch('desktop_app.views.login_view.QTimer')
        self.timer_patcher.start()

    def tearDown(self):
        self.neural_patcher.stop()
        self.license_patcher.stop()
        self.hwid_patcher.stop()
        self.path_patcher.stop()
        self.pool_patcher.stop()
        self.timer_patcher.stop()

    def test_init_check_license(self):
        # We need to mock _auto_update_if_needed because it might trigger things
        with patch.object(LoginView, '_auto_update_if_needed'):
            view = LoginView(self.mock_api_client, license_ok=True)
            self.assertTrue(view.username_input.isEnabled())
            
            view_bad = LoginView(self.mock_api_client, license_ok=False)
            self.assertFalse(view_bad.username_input.isEnabled())

    def test_login_empty_credentials(self):
        view = LoginView(self.mock_api_client)
        view.username_input.setText("")
        view.password_input.setText("")
        
        # Ensure shake_window doesn't cause issues
        with patch.object(view, 'shake_window'):
            with patch('desktop_app.views.login_view.CustomMessageDialog') as mock_dialog:
                view.handle_login()
                mock_dialog.show_warning.assert_called()

    def test_login_success_flow(self):
        view = LoginView(self.mock_api_client)
        view.username_input.setText("user")
        view.password_input.setText("pass")

        # Mock LoginWorker
        with patch('desktop_app.views.login_view.LoginWorker') as MockWorker:
            worker_instance = MockWorker.return_value
            worker_instance.finished_success = MagicMock()
            
            view.handle_login()
            
            # Simulate success signal
            response = {"access_token": "tok", "user_id": 1}
            view.on_login_success(response)
            
            self.mock_api_client.set_token.assert_called_with(response)

    def test_license_update_trigger(self):
        view = LoginView(self.mock_api_client)
        
        with patch('desktop_app.views.login_view.LicenseUpdateWorker') as MockWorker:
            view.handle_update_license()
            MockWorker.assert_called()

    def test_force_password_change(self):
        view = LoginView(self.mock_api_client)
        
        response = {"access_token": "tok", "require_password_change": True, "read_only": False}
        
        # Helper to set user_info side effect
        def side_effect(token):
             self.mock_api_client.user_info = {"require_password_change": True, "read_only": False}
        self.mock_api_client.set_token.side_effect = side_effect

        with patch('desktop_app.views.login_view.ForcePasswordChangeDialog') as MockDialog:
            mock_dlg = MockDialog.return_value
            mock_dlg.exec.return_value = True
            mock_dlg.get_data.return_value = ("new", "new")
            
            # Mock CustomMessageDialog to catch "Success" info
            with patch('desktop_app.views.login_view.CustomMessageDialog'):
                view.on_login_success(response)
            
            self.mock_api_client.change_password.assert_called_with("primoaccesso", "new")

    def test_update_checker_integration(self):
        view = LoginView(self.mock_api_client)
        
        with patch('desktop_app.views.login_view.UpdateWorker') as MockWorker:
            worker = MockWorker.return_value
            worker.update_available = MagicMock()
            
            view.check_updates()
            MockWorker.assert_called()

            # Simulate update found
            # Patch show_update_dialog to avoid exec
            with patch.object(view, 'show_update_dialog'):
                view.on_update_available("2.0", "http://url")
                self.assertIn("Aggiornamento disponibile", view.version_label.text())

if __name__ == '__main__':
    unittest.main()
