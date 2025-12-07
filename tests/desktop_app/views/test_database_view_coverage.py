import sys
import unittest
import pandas as pd
from unittest.mock import MagicMock, patch

# Inject mocks
from tests.desktop_app.mock_qt import mock_qt_modules
sys.modules.update(mock_qt_modules())

from PyQt6.QtCore import Qt
from desktop_app.views.database_view import DatabaseView, CertificatoTableModel

class TestDatabaseViewCoverage(unittest.TestCase):
    def setUp(self):
        self.mock_view_model_patcher = patch('desktop_app.views.database_view.DatabaseViewModel')
        self.mock_api_client_patcher = patch('desktop_app.views.database_view.APIClient')
        
        self.MockViewModel = self.mock_view_model_patcher.start()
        self.MockAPIClient = self.mock_api_client_patcher.start()

        self.mock_vm = self.MockViewModel.return_value
        # Setup default data with REQUIRED columns
        self.mock_vm.filtered_data = pd.DataFrame({
            'id': [1, 2],
            'Dipendente': ['Mario', 'Luigi'],
            'DOCUMENTO': ['Cert A', 'Cert B'], # Added required column
            'stato_certificato': ['ATTIVO', 'SCADUTO']
        })
        self.mock_vm.get_filter_options.return_value = {
            "dipendenti": ["Mario", "Luigi"],
            "categorie": ["Cat1"],
            "stati": ["ATTIVO"]
        }

        self.view = DatabaseView()

    def tearDown(self):
        self.mock_view_model_patcher.stop()
        self.mock_api_client_patcher.stop()

    def test_init_ui(self):
        self.assertTrue(self.view.filter_card.isVisible())
        self.assertTrue(self.view.table_view.isVisible())
        self.MockViewModel.return_value.load_data.assert_called()

    def test_update_table_view(self):
        # Trigger data change
        self.view.on_data_changed()
        
        model = self.view.table_view._model
        self.assertIsInstance(model, CertificatoTableModel)
        self.assertEqual(model.rowCount(), 2)
        self.assertEqual(model.data(model.index(0, 1)), "MARIO") # Upper case

    def test_filters_trigger_load(self):
        # Change combo box
        self.view.dipendente_filter.setCurrentText("Mario")
        self.view._trigger_filter()
        
        self.mock_vm.filter_data.assert_called()

    def test_read_only_state(self):
        self.view.set_read_only(True)
        self.assertFalse(self.view.edit_button.isEnabled())
        self.assertFalse(self.view.delete_button.isEnabled())
        
        self.view.set_read_only(False)
        self.assertTrue(self.view.edit_button.isEnabled())

    def test_export_csv(self):
        with patch('desktop_app.views.database_view.QFileDialog.getSaveFileName', return_value=("test.csv", "CSV")):
            # Ensure model has data
            self.view.on_data_changed()
            
            # Mock to_csv
            with patch.object(self.view.model._data, 'to_csv') as mock_to_csv:
                self.view.export_to_csv()
                mock_to_csv.assert_called_with("test.csv", index=False)

    @patch('desktop_app.views.database_view.CustomMessageDialog')
    def test_delete_action(self, mock_dialog):
        # Initialize model
        self.view.on_data_changed()

        # Mock selection
        mock_selection = MagicMock()
        mock_selection.hasSelection.return_value = True
        mock_index = MagicMock()
        mock_index.row.return_value = 0
        mock_selection.selectedRows.return_value = [mock_index]
        self.view.table_view.selectionModel = MagicMock(return_value=mock_selection)
        
        # Confirm dialog
        mock_dialog.show_question.return_value = True

        self.view.delete_data()
        
        self.mock_vm.delete_certificates.assert_called()

    @patch('desktop_app.views.database_view.QMenu')
    def test_context_menu(self, MockMenu):
        self.view.on_data_changed() # populate model
        
        # Mock indexAt
        mock_index = MagicMock()
        mock_index.isValid.return_value = True
        mock_index.row.return_value = 0
        self.view.table_view.indexAt = MagicMock(return_value=mock_index)

        # Mock menu exec
        mock_menu_instance = MockMenu.return_value
        mock_action = MagicMock()
        mock_menu_instance.exec.return_value = mock_action # Simulate action selected
        
        # We need to simulate that the returned action IS one of the actions added to menu
        # Since we can't easily reference the local variable, we verify the method completes without error
        # and calls exec
        
        # Or better, we test _open_document directly as I did before, but verifying context menu triggering is good coverage
        self.view._show_context_menu(MagicMock())
        mock_menu_instance.exec.assert_called()

    def test_table_model_data_handling(self):
        df = pd.DataFrame({'A': ['foo', None, 'None']})
        model = CertificatoTableModel(df)
        
        # Normal
        self.assertEqual(model.data(model.index(0, 0)), "FOO")
        # None
        self.assertEqual(model.data(model.index(1, 0)), "")
        # String "None"
        self.assertEqual(model.data(model.index(2, 0)), "")

if __name__ == '__main__':
    unittest.main()
