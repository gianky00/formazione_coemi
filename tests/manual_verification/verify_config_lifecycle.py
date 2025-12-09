import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication

# Ensure path
sys.path.insert(0, os.getcwd())

from desktop_app.views.config_view import ConfigView
from desktop_app.services.worker_manager import WorkerManager

class TestConfigLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create QApplication once
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_cleanup_robustness(self):
        """
        Verify ConfigView.cleanup() handles all workers and doesn't crash.
        """
        api_client = MagicMock()
        api_client.user_info = {"is_admin": True, "id": 1}

        # Mock WorkerManager to prevent actual thread tracking if desired,
        # but better to test integration if possible.
        # We'll use the real WorkerManager but ensure we clean it.

        view = ConfigView(api_client)

        # Simulate starting workers
        # 1. Main Loader
        view.trigger_refresh()

        # 2. Optimize Worker (Database)
        # Mock message box to return Yes
        with patch('desktop_app.components.custom_dialog.CustomMessageDialog.show_question', return_value=True):
            view.database_settings.optimize_db()

        # 3. Search Timer (Audit)
        view.audit_widget.search_timer.start()

        # Verify states before cleanup
        self.assertTrue(view.loader_worker.isRunning() or view.loader_worker.isFinished())
        # Optimize worker might be running or finished depending on mock/execution speed.
        # Since API client is mock, it might finish fast or hang if mock blocks?
        # Mock api client methods return instantly by default (MagicMock).
        # So threads might finish instantly.

        # To simulate running thread, we can make the mock block.
        # But for cleanup test, we just want to ensure NO CRASH.

        print("Calling cleanup...")
        try:
            view.cleanup()
        except Exception as e:
            self.fail(f"Cleanup failed with exception: {e}")

        # Verify sub-widgets cleaned up
        self.assertFalse(view.audit_widget.search_timer.isActive())

        if view.database_settings.worker:
             self.assertFalse(view.database_settings.worker.isRunning())

        if view.loader_worker:
             self.assertFalse(view.loader_worker.isRunning())

if __name__ == "__main__":
    unittest.main()
