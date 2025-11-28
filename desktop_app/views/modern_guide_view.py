import sys
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QUrl, pyqtSlot, QObject, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

class GuideBridge(QObject):
    """
    A bridge object to expose functionality to the frontend.
    """
    # Signal kept for compatibility, though tab interface might not use it
    closeRequested = pyqtSignal()

    @pyqtSlot()
    def closeWindow(self):
        """Slot accessible from JavaScript."""
        self.closeRequested.emit()

class ModernGuideView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # WebEngine View
        self.webview = QWebEngineView()

        # QWebChannel Setup for Bridge
        self.channel = QWebChannel()
        self.bridge = GuideBridge()
        self.channel.registerObject("bridge", self.bridge)
        self.webview.page().setWebChannel(self.channel)

        main_layout.addWidget(self.webview)

        # Pre-load immediately
        self.load_guide()

    def load_guide(self):
        # Determine the path to the index.html
        if hasattr(sys, '_MEIPASS'):
            # Frozen environment
            base_dir = os.path.join(sys._MEIPASS, 'guide')
        else:
            # Development environment
            base_dir = os.path.abspath(os.path.join(os.getcwd(), 'guide_frontend', 'dist'))

        index_path = os.path.join(base_dir, 'index.html')

        if not os.path.exists(index_path):
            # Fallback explanation
            html_content = f"""
            <html>
            <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
                <h1>Guida non trovata</h1>
                <p>Il file della guida non &egrave; stato trovato in: {index_path}</p>
                <p>Assicurati di aver eseguito il comando di build:</p>
                <pre>python tools/build_guide.py</pre>
            </body>
            </html>
            """
            self.webview.setHtml(html_content)
        else:
            self.webview.setUrl(QUrl.fromLocalFile(index_path))
