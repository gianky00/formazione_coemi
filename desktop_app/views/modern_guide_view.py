import sys
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QUrl, pyqtSlot, QObject, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebChannel import QWebChannel
from app.core.path_resolver import get_asset_path

class GuideBridge(QObject):
    """
    A bridge object to expose functionality to the frontend.
    """
    closeRequested = pyqtSignal()

    @pyqtSlot()
    def closeWindow(self):
        """Slot accessible from JavaScript."""
        self.closeRequested.emit()

class CustomWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line_number, source_id):
        # S117: Renamed parameters lineNumber -> line_number, sourceID -> source_id
        # Suppress specific router warnings that clutter the console
        if "No routes matched location" in message:
            return
        super().javaScriptConsoleMessage(level, message, line_number, source_id)

class ModernGuideView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # WebEngine View
        self.webview = QWebEngineView()

        # Set custom page to filter logs
        self.custom_page = CustomWebEnginePage(self.webview)
        self.webview.setPage(self.custom_page)

        self.webview.show() # Explicitly show

        # QWebChannel Setup for Bridge
        self.channel = QWebChannel()
        self.bridge = GuideBridge()
        self.channel.registerObject("bridge", self.bridge)
        self.webview.page().setWebChannel(self.channel)

        main_layout.addWidget(self.webview)

        # Pre-load immediately
        self.load_guide()

    def load_guide(self):
        # Determine the path to the index.html using universal path resolver
        # Works for Dev mode, PyInstaller, and Nuitka
        if getattr(sys, 'frozen', False):
            # Frozen: guide is bundled as 'guide' (Nuitka/PyInstaller)
            index_path = get_asset_path("guide/index.html")
        else:
            # Development: use guide_frontend/dist
            index_path = get_asset_path("guide_frontend/dist/index.html")

        if not index_path.exists():
            # Fallback explanation
            html_content = f"""
            <html>
            <body style="font-family: sans-serif; text-align: center; padding-top: 50px; background-color: #f0f8ff; color: #1f2937;">
                <h1>Guida non disponibile</h1>
                <p>Il file della guida non &egrave; stato trovato in:</p>
                <code style="background: #e5e7eb; padding: 5px; border-radius: 4px;">{index_path}</code>
                <p>Se sei in ambiente di sviluppo, esegui il comando:</p>
                <pre style="background: #1e3a8a; color: white; padding: 10px; border-radius: 8px; display: inline-block;">npm run build (in guide_frontend/)</pre>
                <p>Oppure usa lo script di build:</p>
                <pre style="background: #1e3a8a; color: white; padding: 10px; border-radius: 8px; display: inline-block;">python tools/build_guide.py</pre>
            </body>
            </html>
            """
            self.webview.setHtml(html_content)
        else:
            self.webview.setUrl(QUrl.fromLocalFile(str(index_path)))
