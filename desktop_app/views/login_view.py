from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QMessageBox, QHBoxLayout, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QPoint, QEasingCurve, QTimer
from PyQt6.QtGui import QPixmap, QColor
from desktop_app.utils import get_asset_path
from desktop_app.components.animated_widgets import AnimatedButton, AnimatedInput

class LoginView(QWidget):
    login_success = pyqtSignal(dict) # Emits user_info dict

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.resize(400, 500)
        self.setStyleSheet("background-color: #F0F8FF;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)

        # Card Container
        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFixedWidth(450)
        self.card.setStyleSheet("""
            QFrame#card {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
            }
        """)
        card_layout = QVBoxLayout(self.card)
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

        # Inputs - Using AnimatedInput
        self.username_input = AnimatedInput()
        self.username_input.setPlaceholderText("Nome Utente")
        self.username_input.setFixedHeight(40)

        self.password_input = AnimatedInput()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(AnimatedInput.EchoMode.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.returnPressed.connect(self.handle_login)

        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)

        # Login Button - Using AnimatedButton
        self.login_btn = AnimatedButton("Accedi")
        self.login_btn.setFixedHeight(40)
        self.login_btn.set_colors("#1D4ED8", "#1E40AF", "#1E3A8A") # Default, Hover, Pressed
        self.login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_btn)

        # Footer
        footer_label = QLabel("v1.0.0 • Intelleo Security")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("color: #9CA3AF; font-size: 12px; margin-top: 10px;")
        card_layout.addWidget(footer_label)

        layout.addWidget(self.card)

        # Setup Entrance Animation (Fade In + Slide Up)
        self.opacity_effect = QGraphicsOpacityEffect(self.card)
        self.card.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

        self.anim_opacity = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_opacity.setDuration(800)
        self.anim_opacity.setStartValue(0)
        self.anim_opacity.setEndValue(1)
        self.anim_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

        # For Slide Up, we can animate the pos of the card, but since it's in a layout,
        # altering pos might be fighting the layout.
        # Better: Animate the window or just the opacity for now.
        # Alternatively, use a temporary margin animation?
        # Let's stick to Opacity + a slight "scale" effect using geometry if possible?
        # Actually, layout handles geometry.
        # We'll stick to a clean Fade In for robustness.

    def showEvent(self, event):
        super().showEvent(event)
        self.anim_opacity.start()

    def shake_window(self):
        # Shake the CARD, not the whole window (since window is now MasterWindow)
        animation = QPropertyAnimation(self.card, b"pos")
        animation.setDuration(100)
        animation.setLoopCount(3)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        current_pos = self.card.pos()
        animation.setKeyValueAt(0, current_pos)
        animation.setKeyValueAt(0.25, current_pos + QPoint(-5, 0))
        animation.setKeyValueAt(0.75, current_pos + QPoint(5, 0))
        animation.setKeyValueAt(1, current_pos)

        animation.start()

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.shake_window()
            QMessageBox.warning(self, "Errore", "Inserisci nome utente e password.")
            return

        try:
            self.login_btn.setText("Accesso in corso...")
            self.login_btn.setEnabled(False)
            self.login_btn.repaint() # Force redraw

            response = self.api_client.login(username, password)
            self.api_client.set_token(response)

            self.login_success.emit(self.api_client.user_info)

        except Exception as e:
            self.shake_window()
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
