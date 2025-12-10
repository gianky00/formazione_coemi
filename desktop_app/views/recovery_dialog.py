from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                             QProgressBar, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont

from desktop_app.services.license_updater_service import LicenseUpdaterService
from desktop_app.services.hardware_id_service import get_machine_id
from desktop_app.utils import get_asset_path
from app.core.config import settings

class UpdateWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        try:
            hw_id = get_machine_id()
            # Standalone mode: provide config directly
            updater = LicenseUpdaterService(api_client=None, config=self.config)
            success, msg = updater.update_license(hw_id)
            self.finished.emit(success, msg)
        except Exception as e:
            self.finished.emit(False, str(e))

class RecoveryDialog(QDialog):
    """
    A blocking dialog that appears when the license is missing or invalid.
    It allows the user to perform an emergency license update.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Intelleo - Recovery Mode")
        self.setFixedSize(450, 350)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        self.setModal(True)

        # Load Styles
        self.setStyleSheet("""
            QDialog {
                background-color: #F0F9FF;
            }
            QLabel {
                color: #1F2937;
            }
            QPushButton {
                background-color: #1D4ED8;
                color: white;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
            QPushButton:disabled {
                background-color: #9CA3AF;
            }
            QProgressBar {
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                text-align: center;
                background-color: #FFFFFF;
            }
            QProgressBar::chunk {
                background-color: #1D4ED8;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Icon
        icon_lbl = QLabel()
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Use warning emoji as fallback if icon fails
        icon_lbl.setText("⚠️")
        icon_lbl.setStyleSheet("font-size: 48px;")
        layout.addWidget(icon_lbl)

        # Title
        title = QLabel("Licenza Non Valida")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #DC2626;")
        layout.addWidget(title)

        # Message
        self.msg_label = QLabel(
            "Il sistema non rileva una licenza valida per questa macchina.\n\n"
            "Hardware ID: " + str(get_machine_id()) + "\n\n"
            "Puoi tentare di scaricare una licenza aggiornata dai server."
        )
        self.msg_label.setWordWrap(True)
        self.msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg_label.setStyleSheet("font-size: 13px; color: #4B5563;")
        layout.addWidget(self.msg_label)

        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0) # Indeterminate
        self.progress.hide()
        layout.addWidget(self.progress)

        # Buttons
        self.btn_update = QPushButton("Scarica e Aggiorna Licenza")
        self.btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update.clicked.connect(self.start_update)
        layout.addWidget(self.btn_update)

        self.btn_exit = QPushButton("Esci")
        self.btn_exit.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #4B5563;
                border: 1px solid #D1D5DB;
            }
            QPushButton:hover {
                background-color: #F3F4F6;
            }
        """)
        self.btn_exit.clicked.connect(self.reject)
        layout.addWidget(self.btn_exit)

    def start_update(self):
        self.btn_update.setEnabled(False)
        self.btn_exit.setEnabled(False)
        self.progress.show()
        self.msg_label.setText("Connessione al server licenze in corso...")

        # Prepare config for standalone update
        update_config = {
            "repo_owner": settings.LICENSE_REPO_OWNER,
            "repo_name": settings.LICENSE_REPO_NAME,
            "github_token": settings.LICENSE_GITHUB_TOKEN
        }

        self.worker = UpdateWorker(update_config)
        self.worker.finished.connect(self.on_update_finished)
        self.worker.start()

    def on_update_finished(self, success, message):
        self.progress.hide()
        self.btn_update.setEnabled(True)
        self.btn_exit.setEnabled(True)

        if success:
            QMessageBox.information(self, "Successo", "Licenza aggiornata con successo!\nL'applicazione verrà riavviata.")
            self.accept()
        else:
            self.msg_label.setText(f"Errore: {message}")
            QMessageBox.critical(self, "Errore Aggiornamento", message)
