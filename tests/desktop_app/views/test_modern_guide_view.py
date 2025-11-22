import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Define dummy classes to replace Qt classes
# This avoids MagicMock recursion/iteration issues and allows cleaner inheritance

class DummyQDialog:
    def __init__(self, parent=None):
        pass
    def resize(self, w, h):
        pass
    def setWindowFlags(self, flags):
        pass
    def windowFlags(self):
        return 0
    def setWindowTitle(self, title):
        pass
    def exec(self):
        pass
    def setGraphicsEffect(self, effect):
        pass
    def accept(self):
        pass

class DummyQWebEngineView:
    def __init__(self, parent=None):
        self.url = None
        self.html = None
    def setUrl(self, url):
        self.url = url
    def setHtml(self, html):
        self.html = html
    def page(self):
        page = MagicMock()
        return page

class DummyQVBoxLayout:
    def __init__(self, parent=None):
        pass
    def setContentsMargins(self, l, t, r, b):
        pass
    def addWidget(self, widget):
        pass
    def setSpacing(self, s):
        pass

class DummyQHBoxLayout(DummyQVBoxLayout):
    pass

# Create mocks for the modules
mock_qtwidgets = MagicMock()
mock_qtwidgets.QDialog = DummyQDialog
mock_qtwidgets.QVBoxLayout = DummyQVBoxLayout
mock_qtwidgets.QHBoxLayout = DummyQHBoxLayout
mock_qtwidgets.QGraphicsOpacityEffect = MagicMock()
mock_qtwidgets.QMessageBox = MagicMock()
mock_qtwidgets.QFrame = MagicMock()
mock_qtwidgets.QLabel = MagicMock()
mock_qtwidgets.QPushButton = MagicMock()

mock_qtwebengine = MagicMock()
mock_qtwebengine.QWebEngineView = DummyQWebEngineView

mock_qtwebchannel = MagicMock()
mock_qtwebchannel.QWebChannel = MagicMock()

mock_qtcore = MagicMock()
mock_qtcore.Qt = MagicMock()
mock_qtcore.QUrl = MagicMock()
mock_qtcore.QPropertyAnimation = MagicMock()
mock_qtcore.QEasingCurve = MagicMock()
mock_qtcore.pyqtSlot = lambda x=None, **kw: lambda f: f # Mock decorator

# Patch sys.modules
module_patches = {
    'PyQt6.QtWidgets': mock_qtwidgets,
    'PyQt6.QtWebEngineWidgets': mock_qtwebengine,
    'PyQt6.QtWebChannel': mock_qtwebchannel,
    'PyQt6.QtCore': mock_qtcore,
}

with patch.dict(sys.modules, module_patches):
    # Clean out existing imports
    for k in list(sys.modules.keys()):
        if k.startswith('desktop_app'):
            del sys.modules[k]

    from desktop_app.views import modern_guide_view

class TestModernGuideView:

    def test_init_dev_mode(self):
        """Test initialization in development mode (no _MEIPASS)"""
        if hasattr(sys, '_MEIPASS'):
            del sys._MEIPASS

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

        # Setup QUrl mock to return a string we can check
        mock_qtcore.QUrl.fromLocalFile.side_effect = lambda path: f"file://{path}"

        with patch.object(sys, '_MEIPASS', '/tmp/fake_meipass', create=True):
             dialog = modern_guide_view.ModernGuideDialog()

             assert dialog.webview.url is not None
             assert '/tmp/fake_meipass/guide/index.html' in dialog.webview.url

    @patch('os.path.exists')
    def test_fallback_html(self, mock_exists):
        """Test that HTML fallback is used when file is missing"""
        mock_exists.return_value = False

        if hasattr(sys, '_MEIPASS'):
            del sys._MEIPASS

        dialog = modern_guide_view.ModernGuideDialog()

        assert dialog.webview.html is not None
        assert "Guida non trovata" in dialog.webview.html
