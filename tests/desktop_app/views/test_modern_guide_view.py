import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from tests.desktop_app.mock_qt import DummyQWebEngineView

class TestModernGuideView:

    def test_init_dev_mode(self):
        """Test initialization in development mode (no _MEIPASS)"""
        if hasattr(sys, '_MEIPASS'):
            del sys._MEIPASS

        from desktop_app.views import modern_guide_view
        dialog = modern_guide_view.ModernGuideDialog()

        # Verify internal state of our dummy webview
        assert isinstance(dialog.webview, DummyQWebEngineView)

        # Should fall back to HTML or URL depending on file existence
        if dialog.webview.html:
             assert "Guida non trovata" in dialog.webview.html
        else:
             assert dialog.webview.url is not None

    @patch('os.path.exists')
    def test_init_frozen_mode(self, mock_exists):
        """Test initialization in frozen mode (has _MEIPASS)"""
        mock_exists.return_value = True

        # We need to patch QUrl inside the module because it's already imported by lazy import above?
        # No, modern_guide_view imports QUrl from PyQt6.QtCore.
        # PyQt6.QtCore is the Mock object from sys.modules.
        # So we can set side_effect on it.

        # Access the global mock
        mock_qtcore = sys.modules['PyQt6.QtCore']
        mock_qtcore.QUrl.fromLocalFile.side_effect = lambda path: f"file://{path}"

        with patch.object(sys, '_MEIPASS', '/tmp/fake_meipass', create=True):
             from desktop_app.views import modern_guide_view
             dialog = modern_guide_view.ModernGuideDialog()

             assert dialog.webview.url is not None
             assert '/tmp/fake_meipass/guide/index.html' in dialog.webview.url

    @patch('os.path.exists')
    def test_fallback_html(self, mock_exists):
        """Test that HTML fallback is used when file is missing"""
        mock_exists.return_value = False

        if hasattr(sys, '_MEIPASS'):
            del sys._MEIPASS

        from desktop_app.views import modern_guide_view
        dialog = modern_guide_view.ModernGuideDialog()

        assert dialog.webview.html is not None
        assert "Guida non trovata" in dialog.webview.html
