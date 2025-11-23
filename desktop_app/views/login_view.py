import os
import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QMessageBox, QHBoxLayout,
                             QGraphicsOpacityEffect, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QPoint, QEasingCurve, QTimer
from PyQt6.QtGui import QPixmap, QColor, QFont
from desktop_app.utils import get_asset_path
from desktop_app.components.animated_widgets import AnimatedButton, AnimatedInput

class LoginView(QWidget):
    login_success = pyqtSignal(dict) # Emits user_info dict

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.setStyleSheet("background-color: #F0F8FF;") # Global background match

        # Main Layout (Centering the Container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Container Card (Split View)
        self.container = QFrame()
        self.container.setFixedSize(960, 600)
        self.container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-radius: 16px;
            }
        """)

        # Apply Shadow to Container
        # Note: QGraphicsDropShadowEffect applies to children unless we wrap content in a child frame.
        # But here self.container holds left_panel and right_panel.
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.container.setGraphicsEffect(shadow)

        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # --- LEFT PANEL (Branding) ---
        self.left_panel = QFrame()
        self.left_panel.setStyleSheet("""
            QFrame {
                background-color: #1E3A8A; /* Primary Dark Blue */
                border-top-left-radius: 16px;
                border-bottom-left-radius: 16px;
            }
        """)
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.setContentsMargins(40, 40, 40, 40)

        # Logo on Left
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = get_asset_path("desktop_app/assets/logo.png")

        if logo_path:
            pixmap = QPixmap(logo_path)
            # Scale with better limits (e.g. 360x150) to avoid squashing
            scaled = pixmap.scaled(QSize(360, 150), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled)
        else:
            logo_label.setText("INTELLEO")
            logo_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #1E3A8A;")

        left_layout.addStretch()

        # Container for logo to ensure visibility against blue
        logo_container = QFrame()
        logo_container.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
        """)
        logo_container_layout = QVBoxLayout(logo_container)
        logo_container_layout.setContentsMargins(40, 30, 40, 30) # More generous padding
        logo_container_layout.addWidget(logo_label)

        # Removed setFixedSize to allow natural fit
        left_layout.addWidget(logo_container, alignment=Qt.AlignmentFlag.AlignCenter)

        left_layout.addSpacing(40)

        slogan = QLabel("Predict. Validate. Automate.")
        slogan.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slogan.setStyleSheet("color: #93C5FD; font-size: 18px; font-weight: 500; letter-spacing: 1px;")
        left_layout.addWidget(slogan)

        left_layout.addStretch()

        # --- RIGHT PANEL (Form) ---
        self.right_panel = QFrame()
        self.right_panel.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-top-right-radius: 16px;
                border-bottom-right-radius: 16px;
            }
        """)
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(60, 60, 60, 40)
        right_layout.setSpacing(20)

        right_layout.addStretch()

        # Header
        welcome_title = QLabel("Bentornato")
        welcome_title.setStyleSheet("color: #1F2937; font-size: 32px; font-weight: 700;")
        right_layout.addWidget(welcome_title)

        welcome_sub = QLabel("Accedi al tuo account per continuare")
        welcome_sub.setStyleSheet("color: #6B7280; font-size: 15px;")
        right_layout.addWidget(welcome_sub)

        right_layout.addSpacing(20)

        # Inputs
        self.username_input = AnimatedInput()
        self.username_input.setPlaceholderText("Nome Utente")
        self.username_input.setFixedHeight(50)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding-left: 15px;
                font-size: 14px;
                background-color: #F9FAFB;
                color: #1F2937;
            }
            QLineEdit:focus {
                border: 2px solid #1D4ED8;
                background-color: #FFFFFF;
            }
        """)
        right_layout.addWidget(self.username_input)

        self.password_input = AnimatedInput()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(AnimatedInput.EchoMode.Password)
        self.password_input.setFixedHeight(50)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding-left: 15px;
                font-size: 14px;
                background-color: #F9FAFB;
                color: #1F2937;
            }
            QLineEdit:focus {
                border: 2px solid #1D4ED8;
                background-color: #FFFFFF;
            }
        """)
        self.password_input.returnPressed.connect(self.handle_login)
        right_layout.addWidget(self.password_input)

        right_layout.addSpacing(10)

        # Button
        self.login_btn = AnimatedButton("Accedi")
        self.login_btn.setFixedHeight(50)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.set_colors("#1E3A8A", "#1E40AF", "#172554")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E3A8A;
                color: white;
                font-weight: 600;
                font-size: 16px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        right_layout.addWidget(self.login_btn)

        right_layout.addStretch()

        # License Info & Footer
        license_text = self.read_license_info()
        footer_text = "v1.0.0 • Intelleo Security"

        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(4)

        if license_text:
            lic_label = QLabel(license_text)
            lic_label.setStyleSheet("color: #9CA3AF; font-size: 11px;")
            lic_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            footer_layout.addWidget(lic_label)

        ver_label = QLabel(footer_text)
        ver_label.setStyleSheet("color: #D1D5DB; font-size: 11px;")
        ver_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(ver_label)

        right_layout.addLayout(footer_layout)

        # Add panels to container
        container_layout.addWidget(self.left_panel, 40) # 40% width
        container_layout.addWidget(self.right_panel, 60) # 60% width

        main_layout.addWidget(self.container)

        # Animation Setup
        self.setup_entrance_animation()

    def setup_entrance_animation(self):
        # We animate the container
        self.opacity_effect = QGraphicsOpacityEffect(self.container)
        self.container.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

        self.anim_opacity = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_opacity.setDuration(800)
        self.anim_opacity.setStartValue(0)
        self.anim_opacity.setEndValue(1)
        self.anim_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

    def showEvent(self, event):
        super().showEvent(event)
        self.anim_opacity.start()

    def read_license_info(self):
        path = "dettagli_licenza.txt"

        possible_paths = [
            path,
            os.path.join("Licenza", path),
        ]

        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            possible_paths.append(os.path.join(exe_dir, path))
            possible_paths.append(os.path.join(exe_dir, "Licenza", path))

        content = ""
        for p in possible_paths:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        content = f.read()
                    if content: break
                except: pass
        return content

    def shake_window(self):
        animation = QPropertyAnimation(self.container, b"pos")
        animation.setDuration(100)
        animation.setLoopCount(3)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Note: self.container.pos() works, but since it's centered by layout,
        # manual movement might be fought by layout.
        # But for small shakes it usually works visually.
        current_pos = self.container.pos()
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
            self.login_btn.repaint()

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
