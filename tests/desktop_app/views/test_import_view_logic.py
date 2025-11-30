import sys
from unittest.mock import MagicMock, patch
import pytest
from tests.desktop_app.mock_qt import mock_modules

class TestImportViewLogic:
    @pytest.fixture
    def import_view(self):
        with patch.dict(sys.modules, mock_modules):
            from desktop_app.views.import_view import ImportView

            # Patch APIClient instantiation inside ImportView
            with patch("desktop_app.views.import_view.APIClient") as MockClient:
                view = ImportView()
                view.api_client = MockClient.return_value

                view.status_label = MagicMock()
                view.progress_bar = MagicMock()
                view.results_display = MagicMock()

                yield view

    def test_process_dropped_files_no_files(self, import_view):
        import_view.results_display.clear = MagicMock()
        import_view.process_dropped_files([])
        import_view.results_display.clear.assert_called()
        # No processing started

    def test_process_dropped_files_success(self, import_view):
        file_paths = ["/file1.pdf"]
        import_view.api_client.get_paths.return_value = {"database_path": "/tmp/db"}

        with patch("desktop_app.views.import_view.PdfWorker") as MockWorker, \
             patch("desktop_app.views.import_view.QThread"), \
             patch("os.path.isdir", return_value=True):

            mock_worker_instance = MockWorker.return_value
            mock_worker_instance.signals = MagicMock()

            # Manually mock signals on the instance because WorkerSignals is not used here (PdfWorker has signals directly)
            mock_worker_instance.finished = MagicMock()
            mock_worker_instance.progress = MagicMock()
            mock_worker_instance.log_message = MagicMock()
            mock_worker_instance.status_update = MagicMock()
            mock_worker_instance.etr_update = MagicMock()

            import_view.process_dropped_files(file_paths)

            MockWorker.assert_called()
            # Verify thread start
            import_view.thread.start.assert_called()

    def test_stop_processing(self, import_view):
        import_view.thread = MagicMock()
        import_view.thread.isRunning.return_value = True
        import_view.worker = MagicMock()
        import_view.stop_button = MagicMock()

        import_view.stop_processing()

        import_view.worker.stop.assert_called()
        import_view.stop_button.setText.assert_called_with("Fermando...")
