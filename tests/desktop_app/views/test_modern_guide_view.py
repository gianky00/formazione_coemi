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
        view = modern_guide_view.ModernGuideView()

        # Verify internal state of our dummy webview
        assert isinstance(view.webview, DummyQWebEngineView)

        # Should fall back to HTML or URL depending on file existence
        if view.webview.html:
             assert "Guida non trovata" in view.webview.html
        else:
             assert view.webview.url is not None

    @patch('os.path.exists')
    def test_init_frozen_mode(self, mock_exists):
        """Test initialization in frozen mode (has _MEIPASS)"""
        mock_exists.return_value = True

        mock_qtcore = sys.modules['PyQt6.QtCore']
        mock_qtcore.QUrl.fromLocalFile.side_effect = lambda path: f"file://{path}"

        with patch.object(sys, '_MEIPASS', '/tmp/fake_meipass', create=True):
             from desktop_app.views import modern_guide_view
             view = modern_guide_view.ModernGuideView()

             assert view.webview.url is not None
             assert '/tmp/fake_meipass/guide/index.html' in view.webview.url

    @patch('os.path.exists')
    def test_fallback_html(self, mock_exists):
        """Test that HTML fallback is used when file is missing"""
        mock_exists.return_value = False

        if hasattr(sys, '_MEIPASS'):
            del sys._MEIPASS

        from desktop_app.views import modern_guide_view
        view = modern_guide_view.ModernGuideView()

        assert view.webview.html is not None
        assert "Guida non trovata" in view.webview.html
