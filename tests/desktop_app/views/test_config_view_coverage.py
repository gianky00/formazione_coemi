import sys
import unittest
from unittest.mock import MagicMock, patch, mock_open

# Inject mocks
from tests.desktop_app.mock_qt import mock_qt_modules
sys.modules.update(mock_qt_modules())

from PyQt6.QtWidgets import QDialogButtonBox
from desktop_app.views.config_view import ConfigView, UserDialog, ChangePasswordDialog
from app.utils.security import obfuscate_string

class TestConfigViewCoverage(unittest.TestCase):
    def setUp(self):
        self.mock_api_client = MagicMock()
        # Setup initial config
        self.mock_api_client.get_mutable_config.return_value = {
            "DATABASE_PATH": "C:/db.db",
            "SMTP_PORT": 587,
            "GEMINI_API_KEY_ANALYSIS": obfuscate_string("old_key"),
            "GEMINI_API_KEY_CHAT": obfuscate_string("old_chat_key")
        }
        self.mock_api_client.user_info = {"is_admin": True, "id": 1}
        
        self.view = ConfigView(self.mock_api_client)

    def test_load_config_populates_ui(self):
        # Trigger load
        self.view.showEvent(None)
        
        # Verify fields populated
        self.assertEqual(self.view.database_settings.db_path_input.text(), "C:/db.db")
        self.assertEqual(self.view.email_settings.smtp_port_input.text(), "587")
        
        # Verify de-obfuscation
        # The view sets the text to revealed key
        self.assertEqual(self.view.api_settings.gemini_analysis_key_input.text(), "old_key")

    def test_save_config_logic(self):
        self.view.load_config()
        
        # Modify a field
        self.view.email_settings.smtp_host_input.setText("new.host")
        self.view.api_settings.gemini_analysis_key_input.setText("new_key")
        
        self.view.save_config()
        
        self.mock_api_client.update_mutable_config.assert_called()
        args = self.mock_api_client.update_mutable_config.call_args[0][0]
        
        self.assertEqual(args["SMTP_HOST"], "new.host")
        # Check obfuscation
        self.assertNotEqual(args["GEMINI_API_KEY_ANALYSIS"], "new_key")
        self.assertTrue(args["GEMINI_API_KEY_ANALYSIS"].startswith("obf:"))

    def test_unsaved_changes_protection(self):
        self.view.load_config()
        self.assertFalse(self.view.unsaved_changes)
        
        # Change text
        self.view.email_settings.smtp_host_input.setText("changed")
        # Simulate textChanged signal handling manually or trust signal connection
        self.view.mark_dirty() 
        
        self.assertTrue(self.view.unsaved_changes)
        
        # Try switching tab with changes
        with patch('desktop_app.views.config_view.CustomMessageDialog.show_question', return_value=False):
            self.view.switch_tab(1)
            pass

    def test_user_dialog_data(self):
        dialog = UserDialog()
        dialog.username_input.setText("user")
        dialog.is_admin_check.setChecked(True)
        
        data = dialog.get_data()
        self.assertEqual(data['username'], "user")
        self.assertTrue(data['is_admin'])

    def test_change_password_dialog(self):
        dialog = ChangePasswordDialog()
        dialog.old_password.setText("old")
        dialog.new_password.setText("new")
        dialog.confirm_password.setText("new")
        
        data = dialog.get_data()
        self.assertEqual(data['new_password'], "new")

    def test_audit_export(self):
        # Mock requests inside export_logs
        with patch('desktop_app.views.config_view.QFileDialog.getSaveFileName', return_value=("log.csv", "CSV")), \
             patch('requests.get') as mock_get, \
             patch('builtins.open', new_callable=mock_open):
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.iter_content = lambda chunk_size: [b"data"]
            mock_get.return_value = mock_response

            self.view.audit_widget.export_logs()
            
            mock_get.assert_called()

    def test_import_csv_action(self):
        with patch('desktop_app.views.config_view.QFileDialog.getOpenFileName', return_value=("imp.csv", "CSV")):
            with patch('os.path.exists', return_value=True):
                # Configure mock return value
                self.mock_api_client.import_dipendenti_csv.return_value = {"message": "OK"}
                
                self.view.import_csv()
                
                # In mock environment, thread.start() doesn't run the actual thread
                # Manually call the worker's run method to test the logic
                if hasattr(self.view, '_csv_worker') and self.view._csv_worker:
                    # Manually invoke run() since DummyQThread doesn't execute it
                    self.view._csv_worker.run()
                
                self.mock_api_client.import_dipendenti_csv.assert_called_with("imp.csv")

if __name__ == '__main__':
    unittest.main()
