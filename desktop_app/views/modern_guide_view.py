import sys
import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QLabel, QPushButton, QGraphicsOpacityEffect
from PyQt6.QtCore import QUrl, Qt, QPropertyAnimation, QEasingCurve, pyqtSlot, QObject, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

class GuideBridge(QObject):
    """
    A bridge object to expose limited functionality to the frontend.
    Using a dedicated QObject avoids exposing all QWidget properties to QWebChannel,
    preventing 'property has no notify signal' warnings.
    """
    closeRequested = pyqtSignal()

    @pyqtSlot()
    def closeWindow(self):
        """Slot accessible from JavaScript to request closing the dialog."""
        self.closeRequested.emit()

class ModernGuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guida Interattiva Intelleo")
        self.resize(1280, 800)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)

        # Animation Setup
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(400)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        self._pending_result = 0

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # WebEngine View
        self.webview = QWebEngineView()

        # QWebChannel Setup for Bridge
        self.channel = QWebChannel()

        # Use a dedicated bridge object
        self.bridge = GuideBridge()
        self.bridge.closeRequested.connect(self.accept)

        self.channel.registerObject("bridge", self.bridge)
        self.webview.page().setWebChannel(self.channel)

        main_layout.addWidget(self.webview)

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

    def showEvent(self, event):
        super().showEvent(event)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

    def done(self, r):
        # Animate Fade Out
        if self.opacity_effect.opacity() > 0:
            self._pending_result = r
            self.anim.stop()
            self.anim.setStartValue(self.opacity_effect.opacity())
            self.anim.setEndValue(0)

            # Disconnect any previous connections to avoid multiple calls
            try: self.anim.finished.disconnect()
            except: pass

            self.anim.finished.connect(self._on_fade_out_finished)
            self.anim.start()
        else:
            super().done(r)

    def _on_fade_out_finished(self):
        super().done(self._pending_result)
