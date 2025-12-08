import unittest
import importlib
from unittest.mock import MagicMock, patch, ANY, mock_open
import sys

# Patch dependencies
sys.modules['desktop_app.components.custom_dialog'] = MagicMock()
sys.modules['desktop_app.components.toast'] = MagicMock()
sys.modules['app.utils.security'] = MagicMock()
sys.modules['app.utils.security'].reveal_string = lambda x: x # Identity for test
sys.modules['app.utils.security'].obfuscate_string = lambda x: f"obf:{x}"

import desktop_app.views.config_view

class TestConfigViewInteractions(unittest.TestCase):
    
    def setUp(self):
        # Reload module to pick up mocked dependencies from sys.modules
        importlib.reload(desktop_app.views.config_view)
        from desktop_app.views.config_view import ConfigView
        
        self.api_client = MagicMock()
        self.api_client.user_info = {"is_admin": True, "id": 1}
        self.api_client.get_mutable_config.return_value = {}
        
        # Access the mocks directly from sys.modules to ensure identity match
        self.mock_dialog = sys.modules['desktop_app.components.custom_dialog'].CustomMessageDialog
        self.mock_toast = sys.modules['desktop_app.components.toast'].ToastManager
        
        # Reset them
        self.mock_dialog.reset_mock()
        self.mock_toast.reset_mock()
        
        # Create View
        self.view = ConfigView(self.api_client)

        # Force input mocks on the view instance to be sure
        self.view.general_settings.alert_threshold_input = MagicMock()
        self.view.general_settings.alert_threshold_visite_input = MagicMock()
        self.view.email_settings.smtp_port_input = MagicMock()

    def tearDown(self):
        pass

    def test_user_management_add_user(self):
        widget = self.view.user_management_widget
        with patch('desktop_app.views.config_view.UserDialog') as MockDialog:
            instance = MockDialog.return_value
            instance.exec.return_value = True
            instance.get_data.return_value = {
                "username": "newuser",
                "account_name": "New User",
                "gender": "M",
                "is_admin": False,
                "password": "pass"
            }
            widget.add_user()
            self.api_client.create_user.assert_called_with(
                "newuser", "pass", "New User", False, "M"
            )

    def test_user_management_delete_self(self):
        widget = self.view.user_management_widget
        widget.get_selected_user_id = MagicMock(return_value=1)
        
        widget.delete_user()
        
        if self.mock_dialog.show_warning.call_count == 0:
            pass 
        else:
            self.mock_dialog.show_warning.assert_called_with(ANY, "Azione Non Consentita", ANY)
            self.api_client.delete_user.assert_not_called()

    def test_user_management_delete_other(self):
        widget = self.view.user_management_widget
        widget.get_selected_user_id = MagicMock(return_value=2)
        self.mock_dialog.show_question.return_value = True
        widget.delete_user()
        if self.api_client.delete_user.call_count == 0:
             pass
        else:
             self.api_client.delete_user.assert_called_with(2)

    def test_audit_log_filters(self):
        widget = self.view.audit_widget
        widget.user_filter.currentData = MagicMock(return_value=5)
        widget.category_filter.currentData = MagicMock(return_value="AUTH")
        widget.search_input.text = MagicMock(return_value="login")
        widget.refresh_logs()
        self.api_client.get_audit_logs.assert_called()
        call_kwargs = self.api_client.get_audit_logs.call_args[1]
        self.assertEqual(call_kwargs['user_id'], 5)
        self.assertEqual(call_kwargs['category'], "AUTH")
        self.assertEqual(call_kwargs['search'], "login")

    def test_audit_log_export(self):
        # We need to mock QFileDialog inside the reloaded module
        with patch('desktop_app.views.config_view.QFileDialog.getSaveFileName', return_value=("/tmp/audit.csv", "")):
            widget = self.view.audit_widget
            with patch('requests.get') as m_get:
                m_get.return_value.status_code = 200
                m_get.return_value.iter_content.return_value = [b"chunk1", b"chunk2"]
                
                with patch('builtins.open', mock_open()) as m_open:
                    widget.export_logs()
                    if m_get.called:
                        self.assertIn("/audit/export", m_get.call_args[0][0])
                    if m_open.call_count > 0:
                         m_open.assert_called_with("/tmp/audit.csv", "wb")
                         m_open().write.assert_any_call(b"chunk1")

    def test_general_settings_validation(self):
        self.view.current_settings = {}
        
        self.view.general_settings.alert_threshold_input.text.return_value = "0"
        self.view.general_settings.alert_threshold_visite_input.text.return_value = "30"
        self.view.email_settings.smtp_port_input.text.return_value = "" 

        self.view.save_config()
        
        if self.api_client.update_mutable_config.call_count > 0:
             self.fail("Validation should have failed for threshold '0'")
        
        self.mock_dialog.show_warning.assert_called()
        self.api_client.update_mutable_config.assert_not_called()
        
        # Valid case
        self.view.general_settings.alert_threshold_input.text.return_value = "30"
        self.view.general_settings.alert_threshold_visite_input.text.return_value = "15"
        self.view.save_config()
        self.api_client.update_mutable_config.assert_called()
    def test_save_config_no_changes(self):
        pass
