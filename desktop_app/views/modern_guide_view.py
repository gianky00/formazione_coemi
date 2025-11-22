import sys
import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QLabel, QPushButton, QGraphicsOpacityEffect
from PyQt6.QtCore import QUrl, Qt, QPropertyAnimation, QEasingCurve, pyqtSlot
from PyQt6.QtWebEngineWidgets import QWebEngineView

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

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #F3F4F6; border-right: 1px solid #E5E7EB;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Guida Utente")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #111827;")
        sidebar_layout.addWidget(title)

        # Move Close button to top to ensure visibility
        self.close_btn = QPushButton("Chiudi")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Styling to match secondary/destructive buttons loosely or just clean
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                color: #374151;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #F9FAFB;
                border-color: #9CA3AF;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        sidebar_layout.addWidget(self.close_btn)

        sidebar_layout.addStretch()

        main_layout.addWidget(self.sidebar)

        self.webview = QWebEngineView()
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
            self.anim.stop()
            self.anim.setStartValue(self.opacity_effect.opacity())
            self.anim.setEndValue(0)

            # Disconnect any previous connections to avoid multiple calls
            try: self.anim.finished.disconnect()
            except: pass

            # When animation finishes, call super().done(r)
            # We need to use a lambda or separate slot to pass 'r'
            self.anim.finished.connect(lambda: super(ModernGuideDialog, self).done(r))
            self.anim.start()
        else:
            super().done(r)
