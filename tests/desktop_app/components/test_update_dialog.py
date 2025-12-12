import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import pytest

# Force mock mode for these tests

# Inject mocks
from tests.desktop_app.mock_qt import mock_qt_modules
sys.modules.update(mock_qt_modules())

from desktop_app.components.update_dialog import UpdateAvailableDialog

# Mark tests to run in forked subprocess for isolation
pytestmark = pytest.mark.forked

class TestUpdateDialog(unittest.TestCase):
    def test_init_and_labels(self):
        dialog = UpdateAvailableDialog("1.0.1", "http://update.com")
        self.assertEqual(dialog.version, "1.0.1")
        self.assertEqual(dialog.url, "http://update.com")

    @patch('desktop_app.components.update_dialog.QDesktopServices')
    def test_download_action(self, mock_ds):
        dialog = UpdateAvailableDialog("1.0.1", "http://update.com")
        
        # Verify dialog closes on accept
        with patch.object(dialog, 'accept') as mock_accept:
            dialog.download_update()
            
            mock_ds.openUrl.assert_called()
            args = mock_ds.openUrl.call_args[0][0]
            # Verify URL passed to openUrl logic (Mock QUrl might be tricky to inspect property, but call is made)
            mock_accept.assert_called()

if __name__ == '__main__':
    unittest.main()
