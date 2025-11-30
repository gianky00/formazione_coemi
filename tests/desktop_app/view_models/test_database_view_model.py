import sys
from unittest.mock import MagicMock, patch
import pytest
import pandas as pd

# Mock Qt
from tests.desktop_app.mock_qt import mock_modules

class TestDatabaseViewModel:
    @pytest.fixture
    def view_model(self):
        # Apply mocks globally for this test setup
        with patch.dict(sys.modules, mock_modules):
            # Import inside patch context
            from desktop_app.view_models.database_view_model import DatabaseViewModel

            # Need to mock imports inside the module that are NOT covered by mock_qt?
            # APIClient is imported.

            with patch("desktop_app.view_models.database_view_model.APIClient"), \
                 patch("desktop_app.view_models.database_view_model.QThreadPool"):

                vm = DatabaseViewModel()
                vm.api_client = MagicMock()
                vm.threadpool = MagicMock()
                yield vm

    def test_load_data_success(self, view_model):
        data = [
            {"id": 1, "nome": "Rossi", "categoria": "A", "stato_certificato": "attivo", "data_rilascio": "2024", "corso": "C"},
            {"id": 2, "nome": "Bianchi", "categoria": "B", "stato_certificato": "scaduto", "data_rilascio": "2023", "corso": "D"}
        ]

        # Now we can use string patching because module is in sys.modules (patched)
        # Wait, yield vm keeps the patch.dict context alive?
        # Yes, yield inside with block keeps context open until teardown.

        with patch("desktop_app.view_models.database_view_model.FetchCertificatesWorker") as MockWorker:
            mock_worker = MockWorker.return_value
            mock_worker.signals = MagicMock()

            view_model.load_data()

            view_model.threadpool.start.assert_called_with(mock_worker)

            # Simulate completion
            callback = mock_worker.signals.result.connect.call_args_list[0][0][0]
            callback(data)

            assert not view_model.filtered_data.empty
            assert "Dipendente" in view_model.filtered_data.columns
            assert len(view_model.filtered_data) == 2

    def test_filter_data(self, view_model):
        view_model._df_original = pd.DataFrame([
            {"Dipendente": "Rossi", "categoria": "A", "stato_certificato": "attivo"},
            {"Dipendente": "Bianchi", "categoria": "B", "stato_certificato": "in_scadenza"}
        ])

        view_model.filter_data("Rossi", "Tutti", "Tutti")
        assert len(view_model.filtered_data) == 1
        assert view_model.filtered_data.iloc[0]["Dipendente"] == "Rossi"

        view_model.filter_data("Tutti", "Tutti", "in scadenza")
        assert len(view_model.filtered_data) == 1
        assert view_model.filtered_data.iloc[0]["stato_certificato"] == "in_scadenza"

    def test_delete_certificates(self, view_model):
        with patch("desktop_app.view_models.database_view_model.DeleteCertificatesWorker") as MockWorker:
            mock_worker = MockWorker.return_value
            mock_worker.signals = MagicMock()

            view_model.delete_certificates([1, 2])
            view_model.threadpool.start.assert_called()

            # Simulate result
            callback = mock_worker.signals.result.connect.call_args_list[0][0][0]

            # Use a mock for operation_completed signal
            mock_signal = MagicMock()
            view_model.operation_completed = mock_signal

            # Use side effect to trigger reload
            with patch.object(view_model, 'load_data') as mock_load:
                callback({"success": 2, "errors": []})
                mock_signal.emit.assert_called()
                mock_load.assert_called()
