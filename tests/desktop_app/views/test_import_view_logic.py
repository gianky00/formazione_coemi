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

        # The method now uses async Worker pattern to fetch paths first
        # Worker is imported from desktop_app.workers.worker inside the method
        with patch("desktop_app.workers.worker.Worker") as MockWorker, \
             patch("PyQt6.QtCore.QThreadPool") as MockThreadPool:

            mock_worker_instance = MockWorker.return_value
            mock_worker_instance.signals = MagicMock()
            mock_worker_instance.signals.result = MagicMock()
            mock_worker_instance.signals.error = MagicMock()

            import_view.process_dropped_files(file_paths)

            # Verify Worker was created for async path fetching
            MockWorker.assert_called()
            MockThreadPool.globalInstance().start.assert_called()

    def test_stop_processing(self, import_view):
        import_view.thread = MagicMock()
        import_view.thread.isRunning.return_value = True
        import_view.worker = MagicMock()
        import_view.stop_button = MagicMock()

        import_view.stop_processing()

        import_view.worker.stop.assert_called()
        import_view.stop_button.setText.assert_called_with("Fermando...")
