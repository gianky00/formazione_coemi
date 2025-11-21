import sys
import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QMessageBox
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView

class ModernGuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guida Interattiva Intelleo")
        self.resize(1280, 800)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.webview = QWebEngineView()
        layout.addWidget(self.webview)

        self.load_guide()

    def load_guide(self):
        # Determine the path to the index.html
        if hasattr(sys, '_MEIPASS'):
            # Frozen environment
            base_dir = os.path.join(sys._MEIPASS, 'guide')
        else:
            # Development environment
            # Assuming run from root
            base_dir = os.path.abspath(os.path.join(os.getcwd(), 'guide_frontend', 'dist'))

        index_path = os.path.join(base_dir, 'index.html')

        if not os.path.exists(index_path):
            # Fallback explanation for dev mode if build is missing
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
