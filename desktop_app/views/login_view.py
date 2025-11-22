from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
                             QFrame, QMessageBox, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon
from desktop_app.utils import get_asset_path, load_colored_icon

class LoginView(QWidget):
    login_success = pyqtSignal(dict) # Emits user_info dict

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.setWindowTitle("Intelleo - Login")
        self.resize(400, 500)
        self.setStyleSheet("background-color: #F0F8FF;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)

        # Card Container
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet("""
            QFrame#card {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(30, 40, 30, 40)

        # Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = get_asset_path("desktop_app/assets/logo.png")
        if logo_path:
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(200, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            logo_label.setText("INTELLEO")
            logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E3A8A;")

        card_layout.addWidget(logo_label)

        # Title
        title = QLabel("Accedi al tuo account")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #6B7280; font-size: 14px; font-weight: 500;")
        card_layout.addWidget(title)

        # Inputs
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nome Utente")
        self.username_input.setFixedHeight(40)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.returnPressed.connect(self.handle_login)

        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)

        # Login Button
        self.login_btn = QPushButton("Accedi")
        self.login_btn.setFixedHeight(40)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_btn)

        # Footer
        footer_label = QLabel("v1.0.0 • Intelleo Security")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("color: #9CA3AF; font-size: 12px; margin-top: 10px;")
        card_layout.addWidget(footer_label)

        layout.addWidget(card)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Errore", "Inserisci nome utente e password.")
            return

        try:
            self.login_btn.setText("Accesso in corso...")
            self.login_btn.setEnabled(False)
            self.repaint()

            response = self.api_client.login(username, password)
            self.api_client.set_token(response)

            self.login_success.emit(self.api_client.user_info)

        except Exception as e:
            error_msg = "Credenziali non valide o errore del server."
            if hasattr(e, 'response') and e.response is not None:
                 try:
                     detail = e.response.json().get('detail')
                     if detail: error_msg = detail
                 except: pass

            QMessageBox.critical(self, "Errore di Accesso", error_msg)
        finally:
            self.login_btn.setText("Accedi")
            self.login_btn.setEnabled(True)
