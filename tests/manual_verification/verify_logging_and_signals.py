import logging
import sys
import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QObject, pyqtSignal

# Add repo root to path
import os
sys.path.insert(0, os.getcwd())

from app.utils.logging import setup_logging
from desktop_app.views.login_view import LoginWorker

class TestLoggingAndSignals(unittest.TestCase):
    def test_setup_logging_clears_handlers(self):
        """Verify setup_logging removes existing handlers."""
        logger = logging.getLogger('')

        # Add a dummy handler
        dummy_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(dummy_handler)
        self.assertIn(dummy_handler, logger.handlers)

        # Run setup_logging
        setup_logging()

        # Verify dummy handler is gone
        self.assertNotIn(dummy_handler, logger.handlers)
        # Verify we have exactly 2 handlers (File + Console) as configured
        self.assertEqual(len(logger.handlers), 2)

    def test_login_worker_signals(self):
        """Verify LoginWorker signals accept Python objects."""
        # This test mimics the emission that caused the crash
        worker = LoginWorker(MagicMock(), "user", "pass")

        # Mock slots
        success_slot = MagicMock()
        error_slot = MagicMock()

        worker.finished_success.connect(success_slot)
        worker.finished_error.connect(error_slot)

        # Emit dict (PyQt_PyObject)
        data = {"token": "123", "user": "admin"}
        try:
            worker.finished_success.emit(data)
            success_slot.assert_called_with(data)
        except Exception as e:
            self.fail(f"Signal finished_success failed to emit dict: {e}")

        # Emit string
        error_msg = "Login failed"
        try:
            worker.finished_error.emit(error_msg)
            error_slot.assert_called_with(error_msg)
        except Exception as e:
            self.fail(f"Signal finished_error failed to emit string: {e}")

if __name__ == '__main__':
    unittest.main()
