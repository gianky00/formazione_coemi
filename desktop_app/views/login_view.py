import threading
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QFont, QCursor

from app import __version__ as app_version
from desktop_app.services.license_manager import LicenseManager


class LoginView(QWidget):
    # Signals for thread-safe UI updates
    login_success = Signal(dict)
    login_failure = Signal(str)

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        
        # Style
        self.setStyleSheet("background-color: #F0F8FF;")
        
        self.setup_ui()
        
        # Connect signals
        self.login_success.connect(self.controller.on_login_success)
        self.login_failure.connect(self._on_login_failed)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Center container
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
            }
        """)
        self.container.setFixedSize(400, 450)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        container_layout.setSpacing(15)

        # Logo/Title
        self.lbl_title = QLabel("Intelleo")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1E3A8A; border: none;")
        container_layout.addWidget(self.lbl_title)

        self.lbl_subtitle = QLabel("Predict. Validate. Automate.")
        self.lbl_subtitle.setAlignment(Qt.AlignCenter)
        self.lbl_subtitle.setStyleSheet("font-size: 14px; font-style: italic; color: #6B7280; border: none;")
        container_layout.addWidget(self.lbl_subtitle)
        
        container_layout.addSpacing(20)

        # Username
        lbl_user = QLabel("Username")
        lbl_user.setStyleSheet("font-weight: bold; color: #374151; border: none;")
        container_layout.addWidget(lbl_user)
        
        self.entry_user = QLineEdit()
        self.entry_user.setPlaceholderText("Inserisci username")
        self.entry_user.setStyleSheet("padding: 10px; border: 1px solid #D1D5DB; border-radius: 4px;")
        container_layout.addWidget(self.entry_user)

        # Password
        lbl_pass = QLabel("Password")
        lbl_pass.setStyleSheet("font-weight: bold; color: #374151; border: none;")
        container_layout.addWidget(lbl_pass)
        
        self.entry_pass = QLineEdit()
        self.entry_pass.setEchoMode(QLineEdit.Password)
        self.entry_pass.setPlaceholderText("Inserisci password")
        self.entry_pass.setStyleSheet("padding: 10px; border: 1px solid #D1D5DB; border-radius: 4px;")
        self.entry_pass.returnPressed.connect(self.do_login)
        container_layout.addWidget(self.entry_pass)

        # Button
        self.btn_login = QPushButton("ACCEDI")
        self.btn_login.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #1D4ED8;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
            QPushButton:disabled {
                background-color: #9CA3AF;
            }
        """)
        self.btn_login.clicked.connect(self.do_login)
        container_layout.addWidget(self.btn_login)

        # Status Label
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("color: red; border: none;")
        container_layout.addWidget(self.lbl_status)

        # Centering the container in the main view
        h_spacer_layout = QHBoxLayout()
        h_spacer_layout.addStretch()
        h_spacer_layout.addWidget(self.container)
        h_spacer_layout.addStretch()
        
        main_layout.addStretch()
        main_layout.addLayout(h_spacer_layout)
        main_layout.addStretch()

        # --- License Info Footer ---
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(10, 10, 10, 10)
        
        try:
            lic_data = LicenseManager.get_license_data()
            if lic_data:
                client_name = lic_data.get("Cliente", "N/D")
                expiry = lic_data.get("Scadenza Licenza", "N/D")
                hwid = lic_data.get("Hardware ID", "N/D")
                info_text = f"Cliente: {client_name} | Scadenza: {expiry} | HWID: {hwid} | Versione: {app_version}"
            else:
                info_text = f"Versione: {app_version}"
        except Exception:
            info_text = f"Versione: {app_version}"
            
        lbl_lic = QLabel(info_text)
        lbl_lic.setStyleSheet("color: #6B7280; font-size: 11px;")
        footer_layout.addStretch()
        footer_layout.addWidget(lbl_lic)
        
        main_layout.addLayout(footer_layout)

    def do_login(self):
        username = self.entry_user.text().strip()
        password = self.entry_pass.text().strip()

        if not username or not password:
            self.lbl_status.setText("Inserisci username e password")
            return

        # Disable UI
        self.entry_user.setEnabled(False)
        self.entry_pass.setEnabled(False)
        self.btn_login.setEnabled(False)
        
        self.lbl_status.setText("Connessione in corso...")
        self.lbl_status.setStyleSheet("color: blue; border: none;")

        # Threading for login
        thread = threading.Thread(target=self._login_thread, args=(username, password), daemon=True)
        thread.start()

    def _login_thread(self, username, password):
        try:
            token_data = self.controller.api_client.login(username, password)
            self.login_success.emit(token_data)
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg:
                error_msg = "Credenziali non valide."
            elif "ConnectionError" in str(type(e).__name__):
                error_msg = "Impossibile connettersi al server."
            self.login_failure.emit(error_msg)

    @Slot(str)
    def _on_login_failed(self, error_msg):
        self.lbl_status.setText(error_msg)
        self.lbl_status.setStyleSheet("color: red; border: none;")
        self.entry_user.setEnabled(True)
        self.entry_pass.setEnabled(True)
        self.btn_login.setEnabled(True)
        self.entry_pass.clear()
