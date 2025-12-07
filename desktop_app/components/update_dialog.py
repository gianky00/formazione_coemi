from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDesktopServices, QUrl

class UpdateAvailableDialog(QDialog):
    def __init__(self, version, url, parent=None):
        super().__init__(parent)
        self.version = version
        self.url = url
        self.setWindowTitle("Aggiornamento Disponibile")
        self.setFixedWidth(400)
        
        # Apply style to match the application theme
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border-radius: 12px;
            }
            QLabel {
                color: #1F2937;
            }
            QPushButton {
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)

        # Title
        title = QLabel(f"È disponibile una nuova versione: {self.version}")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #1E3A8A;")
        title.setWordWrap(True)
        layout.addWidget(title)

        # Message
        msg = QLabel("Ti consigliamo di scaricare l'aggiornamento per ottenere le ultime funzionalità e patch di sicurezza.")
        msg.setStyleSheet("font-size: 14px; color: #4B5563;")
        msg.setWordWrap(True)
        layout.addWidget(msg)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        ignore_btn = QPushButton("Ignora")
        ignore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ignore_btn.setStyleSheet("""
            QPushButton {
                background-color: #F3F4F6;
                color: #4B5563;
                border: 1px solid #E5E7EB;
            }
            QPushButton:hover {
                background-color: #E5E7EB;
            }
        """)
        ignore_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ignore_btn)

        download_btn = QPushButton("Scarica Ora")
        download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        download_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E3A8A;
                color: #FFFFFF;
                border: none;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
        """)
        download_btn.clicked.connect(self.download_update)
        btn_layout.addWidget(download_btn)

        layout.addLayout(btn_layout)

    def download_update(self):
        QDesktopServices.openUrl(QUrl(self.url))
        self.accept()
