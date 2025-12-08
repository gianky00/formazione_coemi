import os
import sys
import socket
import platform
import math
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QMessageBox, QHBoxLayout,
                             QGraphicsDropShadowEffect, QApplication, QPushButton,
                             QDialog, QLineEdit, QDialogButtonBox, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QPoint, QPointF, QEasingCurve, QTimer, QObject, QThread, QThreadPool, QRect
from PyQt6.QtGui import QPixmap, QColor, QFont, QPainter, QLinearGradient, QPen, QBrush
from desktop_app.utils import get_asset_path
import random
from desktop_app.components.animated_widgets import AnimatedButton, AnimatedInput
from desktop_app.components.custom_dialog import CustomMessageDialog
from desktop_app.services.license_manager import LicenseManager
from desktop_app.services.sound_manager import SoundManager
from desktop_app.services.license_updater_service import LicenseUpdaterService
from desktop_app.services.hardware_id_service import get_machine_id
from desktop_app.services.update_checker import UpdateWorker
from desktop_app.components.neural_3d import NeuralNetwork3D
from desktop_app.components.update_dialog import UpdateAvailableDialog
from app import __version__
from desktop_app.constants import STYLE_LICENSE_VALID, STYLE_LICENSE_EXPIRING, LABEL_LICENSE_EXPIRY, LABEL_HARDWARE_ID

class ForcePasswordChangeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazione Password Obbligatoria")
        self.resize(400, 200)
        self.layout = QVBoxLayout(self)

        lbl = QLabel("È il tuo primo accesso. Devi impostare una nuova password.")
        lbl.setWordWrap(True)
        self.layout.addWidget(lbl)

        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password.setPlaceholderText("Nuova Password")
        self.layout.addWidget(self.new_password)

        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password.setPlaceholderText("Conferma Password")
        self.layout.addWidget(self.confirm_password)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

    def get_data(self):
        return self.new_password.text(), self.confirm_password.text()

class LoginWorker(QThread):
    finished_success = pyqtSignal(dict)
    finished_error = pyqtSignal(str)

    def __init__(self, api_client, username, password):
        super().__init__()
        self.api_client = api_client
        self.username = username
        self.password = password

    def run(self):
        try:
            response = self.api_client.login(self.username, self.password)
            self.finished_success.emit(response)
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                 try:
                     detail = e.response.json().get('detail')
                     if detail: error_msg = detail
                 except Exception:
                     # Fallback to string representation if parsing fails
                     pass
            self.finished_error.emit(error_msg)

class LicenseUpdateWorker(QThread):
    """Worker to run license update in a separate thread."""
    update_finished = pyqtSignal(bool, str)

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client

    def run(self):
        hw_id = get_machine_id()
        if not hw_id:
            self.update_finished.emit(False, "Impossibile recuperare l'Hardware ID della macchina.")
            return

        updater = LicenseUpdaterService(self.api_client)
        success, message = updater.update_license(hw_id)
        self.update_finished.emit(success, message)

class LoginView(QWidget):
    login_success = pyqtSignal(dict) # Emits user_info dict

    def __init__(self, api_client, license_ok=True, license_error=""):
        super().__init__()
        self.api_client = api_client
        self.threadpool = QThreadPool()
        self._stop_3d_rendering = False # Flag to safely stop 3D engine before view transition
        self.pending_count = 0 # To store the count of documents to validate
        self.login_worker = None
        self.license_worker = None
        self.update_worker = None
        self.update_url = None
        self.update_version = None

        # --- Interactive Neural Background Setup ---
        self.setMouseTracking(True)
        self.mouse_pos_norm = (0.0, 0.0) # Normalized -1 to 1

        # Initialize 3D Engine
        # num_nodes increased to 120 for richer visuals thanks to optimization
        self.neural_engine = NeuralNetwork3D(num_nodes=120, connect_distance=280)

        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._animate_background)
        self._anim_timer.start(16) # ~60 FPS target for smooth 3D rotation

        # Container Card (Split View) - Manual Positioning for Animation
        self.container = QFrame(self)
        self.container.setFixedSize(960, 600)
        self.container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-radius: 16px;
            }
        """)

        # Shadow (Permanently on self.container)
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
            scaled = pixmap.scaled(QSize(350, 160), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled)
        else:
            logo_label.setText("INTELLEO")
            logo_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #1E3A8A;")

        left_layout.addStretch()

        logo_container = QFrame()
        logo_container.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 16px;
        """)
        logo_container_layout = QVBoxLayout(logo_container)
        logo_container_layout.setContentsMargins(15, 20, 15, 20)
        logo_container_layout.addWidget(logo_label)

        left_layout.addWidget(logo_container, alignment=Qt.AlignmentFlag.AlignCenter)
        left_layout.addStretch()

        # License Info
        license_info_container = QFrame()
        license_info_layout = QVBoxLayout(license_info_container)
        license_info_layout.setContentsMargins(15, 15, 15, 15)
        license_info_layout.setSpacing(5)

        # Header with Title and Coherence Pill
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        title_label = QLabel("Dettagli Licenza")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_label.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 600;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Coherence Check Logic
        current_hw_id = get_machine_id()
        _, license_data = self.read_license_info()

        coherence_pill = QLabel()
        coherence_pill.setStyleSheet("""
            QLabel {
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 11px;
                font-weight: 600;
            }
        """)
        # S1192: Use constants
        if license_data and LABEL_HARDWARE_ID in license_data:
            stored_hw_id = license_data[LABEL_HARDWARE_ID]
            if stored_hw_id == current_hw_id:
                coherence_pill.setText("Matched")
                coherence_pill.setStyleSheet(coherence_pill.styleSheet() + "background-color: #065F46; color: #6EE7B7;")
            else:
                coherence_pill.setText("Mismatch")
                coherence_pill.setStyleSheet(coherence_pill.styleSheet() + "background-color: #7F1D1D; color: #FCA5A5;")
        else:
             coherence_pill.hide() # Should not happen usually if lic exists

        header_layout.addWidget(coherence_pill)

        # Header container to draw the bottom border
        header_container = QFrame()
        header_container.setLayout(header_layout)
        header_container.setStyleSheet("border-bottom: 1px solid #60A5FA; padding-bottom: 5px;")
        license_info_layout.addWidget(header_container)

        license_text, _ = self.read_license_info()

        license_label = QLabel(license_text)
        license_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # S1192: Use constants for duplicated strings
        if LicenseManager.is_license_expiring_soon(license_data):
            license_label.setStyleSheet(STYLE_LICENSE_EXPIRING)
        else:
            license_label.setStyleSheet(STYLE_LICENSE_VALID)
        license_label.setWordWrap(True)
        license_info_layout.addWidget(license_label)

        # PC Details
        pc_details_layout = QVBoxLayout()
        pc_details_layout.setContentsMargins(15, 15, 15, 15)
        pc_details_layout.setSpacing(5)

        pc_title_label = QLabel("Dettagli PC")
        pc_title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        pc_title_label.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 600; border-bottom: 1px solid #60A5FA; padding-bottom: 5px;")
        pc_details_layout.addWidget(pc_title_label)

        # Hostname
        hostname = socket.gethostname()
        hostname_label = QLabel(f"Hostname: {hostname}")
        hostname_label.setStyleSheet(STYLE_LICENSE_VALID)
        pc_details_layout.addWidget(hostname_label)

        # OS
        os_name = f"{platform.system()} {platform.release()}"
        os_label = QLabel(f"Sistema Operativo: {os_name}")
        os_label.setStyleSheet(STYLE_LICENSE_VALID)
        pc_details_layout.addWidget(os_label)

        license_info_layout.addLayout(pc_details_layout)
        left_layout.addWidget(license_info_container)

        left_layout.addSpacing(20)

        # Update License Button
        self.update_btn = QPushButton("Aggiorna Licenza")
        self.update_btn.setFixedHeight(48)
        self.update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                font-weight: 600;
                font-size: 15px;
                border-radius: 6px;
                border: 1px solid #60A5FA;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-color: #93C5FD;
            }
        """)
        self.update_btn.clicked.connect(self.handle_update_license)
        left_layout.addWidget(self.update_btn)

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

        # We hold references to these widgets for animation
        self.animated_widgets = []

        self.welcome_title = QLabel("Area Riservata")
        self.welcome_title.setStyleSheet("color: #1F2937; font-size: 32px; font-weight: 700;")
        right_layout.addWidget(self.welcome_title)
        self.animated_widgets.append((self.welcome_title, True)) # (Widget, CanFade)

        self.welcome_sub = QLabel("Autenticati per accedere al workspace")
        self.welcome_sub.setStyleSheet("color: #6B7280; font-size: 15px;")
        right_layout.addWidget(self.welcome_sub)
        self.animated_widgets.append((self.welcome_sub, True))

        right_layout.addSpacing(20)

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
        # Disable Opacity Effect for Inputs to avoid Painter conflict
        self.animated_widgets.append((self.username_input, False))

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
        self.animated_widgets.append((self.password_input, False))

        right_layout.addSpacing(10)

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
        self.animated_widgets.append((self.login_btn, False))

        right_layout.addStretch()
        right_layout.addStretch(1)

        # Footer Layout
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(5)

        # Version & Update Status Line
        self.version_label = QLabel(f"Intelleo Security • v{__version__}")
        self.version_label.setStyleSheet("color: #6B7280; font-size: 13px;")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)

        # Enable link activation manually
        self.version_label.linkActivated.connect(self.on_footer_click)

        footer_layout.addWidget(self.version_label)

        # Copyright Line
        current_year = datetime.now().year
        copyright_text = f"Copyright © {current_year} Intelleo. All rights reserved."
        copyright_label = QLabel(copyright_text)
        copyright_label.setStyleSheet("color: #9CA3AF; font-size: 11px;")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(copyright_label)

        right_layout.addLayout(footer_layout)
        
        # Add labels to animated widgets list
        self.animated_widgets.append((self.version_label, True))
        self.animated_widgets.append((copyright_label, True))

        container_layout.addWidget(self.left_panel, 40)
        container_layout.addWidget(self.right_panel, 60)

        # REMOVED setup_entrance_animation (staggered fades) to fix QPainter crashes
        # We use showEvent for a stable Slide Up animation

        if not license_ok:
            self.username_input.setEnabled(False)
            self.password_input.setEnabled(False)
            self.login_btn.setEnabled(False)
            error_label = QLabel("Licenza non valida o scaduta. Aggiornala per continuare.")
            error_label.setStyleSheet("color: #DC2626; font-size: 14px; font-weight: 500;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            right_layout.insertWidget(5, error_label)

        self._auto_update_if_needed()

    def check_updates(self):
        """Starts the update worker to check for updates."""
        if self.update_worker and self.update_worker.isRunning():
            return

        self.update_worker = UpdateWorker(self)
        self.update_worker.update_available.connect(self.on_update_available)
        self.update_worker.up_to_date.connect(self.on_up_to_date)
        self.update_worker.check_failed.connect(self.on_check_failed)
        self.update_worker.start()

    def on_update_available(self, version, url):
        self.update_version = version
        self.update_url = url
        
        # Text: Intelleo Security • v1.0.0 • Aggiornamento disponibile (Orange)
        base_text = f"Intelleo Security • v{__version__}"
        # We use HTML-like formatting for clickable area or color
        # But QLabel linkActivated works better with HTML anchor tags.
        # However, the user wants clickable text.
        
        # We can construct the full HTML string.
        # "Aggiornamento disponibile" should be clickable.
        
        full_text = f'{base_text} • <a href="update" style="color: #F97316; text-decoration: none;">Aggiornamento disponibile</a>'
        self.version_label.setText(full_text)
        self.version_label.setTextFormat(Qt.TextFormat.RichText)
        self.version_label.setOpenExternalLinks(False) # We handle it manually
        
        # Automatically show dialog
        self.show_update_dialog()

    def on_up_to_date(self):
        base_text = f"Intelleo Security • v{__version__}"
        # Green text
        full_text = f'{base_text} • <span style="color: #10B981;">Sistema aggiornato</span>'
        self.version_label.setText(full_text)
        self.version_label.setTextFormat(Qt.TextFormat.RichText)

    def on_check_failed(self):
        base_text = f"Intelleo Security • v{__version__}"
        # Grey/Yellow text
        full_text = f'{base_text} • <span style="color: #9CA3AF;">Modalità Offline</span>'
        self.version_label.setText(full_text)
        self.version_label.setTextFormat(Qt.TextFormat.RichText)

    def on_footer_click(self, link):
        if link == "update" and self.update_version and self.update_url:
            self.show_update_dialog()

    def show_update_dialog(self):
        dialog = UpdateAvailableDialog(self.update_version, self.update_url, self)
        dialog.exec()

    def _animate_background(self):
        # Update physics
        self.neural_engine.update(self.mouse_pos_norm[0], self.mouse_pos_norm[1])
        # Trigger repaint
        self.update()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        # Normalized coordinates (-1.0 to 1.0) for 3D engine rotation
        w_half = self.width() / 2
        h_half = self.height() / 2
        
        nx = (pos.x() - w_half) / w_half
        ny = (pos.y() - h_half) / h_half
        self.mouse_pos_norm = (nx, ny)

        # --- 3D Tilt / Parallax Effect for the Login Card ---
        # 1. Move Shadow
        shadow = self.container.graphicsEffect()
        if isinstance(shadow, QGraphicsDropShadowEffect):
            shadow.setXOffset(int(-15 * nx))
            shadow.setYOffset(int(10 - (10 * ny)))
            
        # 2. Move Container (Parallax)
        # Only apply if not entrance-animating
        if not (hasattr(self, 'anim_slide') and self.anim_slide.state() == QPropertyAnimation.State.Running):
            # Calculate new target position relative to base center
            target_x = self.center_pos.x() + (12 * nx)
            target_y = self.center_pos.y() + (12 * ny)
            self.container.move(int(target_x), int(target_y))

    def hideEvent(self, event):
        super().hideEvent(event)
        # Bug 7 Fix: Stop animation timer when view is hidden to save resources
        if self._anim_timer.isActive():
            self._anim_timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True) # Enable AA for smooth lines

        # 1. Deep Space Background
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor("#1E3A8A")) # Dark Blue
        grad.setColorAt(1, QColor("#0F172A")) # Slate 900
        painter.fillRect(self.rect(), grad)
        
        # Check if we should skip 3D rendering (e.g. during view transitions)
        if self._stop_3d_rendering:
            return

        # 2. Render 3D Engine
        # The engine handles projection, connections, pulses, and drawing
        try:
            self.neural_engine.project_and_render(painter, self.width(), self.height())
        except Exception as e:
            # Prevent crash during resize or close
            print(f"3D Render Error: {e}")

    def _auto_update_if_needed(self):
        from desktop_app.services.path_service import get_license_dir
        license_dir = get_license_dir()
        required_files = ["pyarmor.rkey", "config.dat", "manifest.json"]
        if any(not os.path.exists(os.path.join(license_dir, f)) for f in required_files):
            QTimer.singleShot(1000, self.handle_update_license)

    def handle_update_license(self):
        if self.license_worker and self.license_worker.isRunning():
            return

        self.update_btn.setText("Aggiornamento in corso...")
        self.update_btn.setEnabled(False)

        self.license_worker = LicenseUpdateWorker(self.api_client)
        self.license_worker.update_finished.connect(self.on_update_finished)
        self.license_worker.finished.connect(self._cleanup_license_worker)
        self.license_worker.start()

    def _cleanup_license_worker(self):
        self.license_worker = None

    def on_update_finished(self, success, message):
        self.update_btn.setText("Aggiorna Licenza")
        self.update_btn.setEnabled(True)

        if success:
            if "già aggiornata" in message:
                CustomMessageDialog.show_info(self, "Info Licenza", "La licenza risulta aggiornata.")
            else:
                from desktop_app.main import restart_app
                CustomMessageDialog.show_info(self, "Successo", f"{message}\n\nÈ necessario riavviare l'applicazione per applicare le modifiche.")
                restart_app()
        else:
            CustomMessageDialog.show_error(self, "Errore Aggiornamento", message)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Keep container centered
        if hasattr(self, 'container'):
            cx = (self.width() - self.container.width()) // 2
            cy = (self.height() - self.container.height()) // 2
            self.center_pos = QPoint(cx, cy)
            
            # If animating, update target to new center
            if hasattr(self, 'anim_slide') and self.anim_slide.state() == QPropertyAnimation.State.Running:
                self.anim_slide.setEndValue(QPoint(cx, cy))
            else:
                self.container.move(cx, cy)

    def closeEvent(self, event):
        """
        Force quit all running threads when the view is closed.
        This prevents 'Zombie' processes and 'Thread Destroyed' crashes.
        """
        # 1. Stop Login Worker
        if self.login_worker and self.login_worker.isRunning():
            print("[LoginView] Stopping LoginWorker...")
            self.login_worker.quit()
            self.login_worker.wait()

        # 2. Stop License Worker
        if self.license_worker and self.license_worker.isRunning():
            print("[LoginView] Stopping LicenseWorker...")
            self.license_worker.quit()
            self.license_worker.wait()

        # 3. Stop Background Animation Timer
        if self._anim_timer.isActive():
            self._anim_timer.stop()
            
        # 4. Stop Update Worker
        if self.update_worker and self.update_worker.isRunning():
            self.update_worker.quit()
            self.update_worker.wait()

        event.accept()

    def reset_view(self):
        """Resets the UI state for a fresh login attempt."""
        self.username_input.setEnabled(True)
        self.password_input.setEnabled(True)
        self.login_btn.setEnabled(True)
        self.login_btn.set_loading(False)
        self.password_input.clear()

        self._stop_3d_rendering = False # Re-enable rendering

        # --- FIX: Reset Neural Engine & UI State ---
        self.neural_engine.reset()

        # Restore Shadow Effect (removing opacity effect from transition)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.container.setGraphicsEffect(shadow)

        # Ensure background animation is running
        if not self._anim_timer.isActive():
            self._anim_timer.start(16)

    def showEvent(self, event):
        super().showEvent(event)
        
        self.reset_view()

        # Stable "Slide Up" Entrance Animation
        x = (self.width() - self.container.width()) // 2
        final_y = (self.height() - self.container.height()) // 2
        start_y = final_y + 60 # Start lower

        self.container.move(x, start_y)

        self.anim_slide = QPropertyAnimation(self.container, b"pos")
        self.anim_slide.setDuration(800)
        self.anim_slide.setStartValue(QPoint(x, start_y))
        self.anim_slide.setEndValue(QPoint(x, final_y))
        self.anim_slide.setEasingCurve(QEasingCurve.Type.OutBack) # Modern bouncy feel
        self.anim_slide.start()
        
        # Trigger update check on show
        self.check_updates()

    def read_license_info(self):
        data = LicenseManager.get_license_data()

        if not data:
            # FIX: Returns a tuple consistent with the signature (text, dict)
            return "Dettagli licenza non disponibili. Procedere con l'aggiornamento.", {}

        lines = []
        if "Cliente" in data:
            lines.append(f"Cliente: {data['Cliente']}")
        if LABEL_LICENSE_EXPIRY in data:
            lines.append(f"Scadenza: {data[LABEL_LICENSE_EXPIRY]}")
        if LABEL_HARDWARE_ID in data:
            lines.append(f"ID Licenza: {data[LABEL_HARDWARE_ID]}")

        return "\n".join(lines), data

    def shake_window(self):
        animation = QPropertyAnimation(self.container, b"pos")
        animation.setDuration(100)
        animation.setLoopCount(3)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        current_pos = self.container.pos()

        animation.setKeyValueAt(0, current_pos)
        animation.setKeyValueAt(0.25, current_pos + QPoint(-5, 0))
        animation.setKeyValueAt(0.75, current_pos + QPoint(5, 0))
        animation.setKeyValueAt(1, current_pos)
        animation.start()

    def handle_login(self):
        if self.login_worker and self.login_worker.isRunning():
            return

        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.shake_window()
            CustomMessageDialog.show_warning(self, "Errore", "Inserisci nome utente e password.")
            return

        _, license_data = self.read_license_info()
        if license_data and LABEL_HARDWARE_ID in license_data:
            stored_hw_id = license_data[LABEL_HARDWARE_ID]
            current_hw_id = get_machine_id()
            if stored_hw_id != current_hw_id:
                CustomMessageDialog.show_error(self, "Errore di Licenza",
                                     "L'Hardware ID della licenza non corrisponde a quello di questa macchina.\n"
                                     "Contattare il supporto per una nuova licenza.")
                return

        # Start Threaded Login
        self.login_btn.set_loading(True)

        self.login_worker = LoginWorker(self.api_client, username, password)
        self.login_worker.finished_success.connect(self.on_login_success)
        self.login_worker.finished_error.connect(self._on_login_error)
        self.login_worker.finished.connect(self._cleanup_login_worker)
        self.login_worker.start()

    def _cleanup_login_worker(self):
        self.login_worker = None

    def _on_login_error(self, error_msg):
        self.login_btn.set_loading(False)
        self.shake_window()
        CustomMessageDialog.show_error(self, "Errore di Accesso", error_msg)

    def _prepare_welcome_message(self, user_info):
        """Prepares user context and welcome speech."""
        username = user_info.get("account_name") or user_info.get("username", "Operatore")
        gender = user_info.get("gender")
        welcome_word = "Bentornata" if gender == 'F' else "Bentornato"
        speech_text = f"Ciao {username}, {welcome_word} in Intellèo."

        if self.pending_count == 1:
            speech_text += " C'è un documento da convalidare."
        elif self.pending_count > 1:
            speech_text += f" Ci sono {self.pending_count} documenti da convalidare."

        user_info["welcome_speech"] = speech_text
        user_info["pending_documents_count"] = self.pending_count

    def _handle_password_change(self):
        """Helper to handle forced password change workflow."""
        while True:
            dialog = ForcePasswordChangeDialog(self)
            if dialog.exec():
                new_pw, confirm_pw = dialog.get_data()
                if not new_pw:
                    CustomMessageDialog.show_warning(self, "Errore", "Password vuota.")
                    continue
                if new_pw != confirm_pw:
                    CustomMessageDialog.show_warning(self, "Errore", "Le password non coincidono.")
                    continue

                try:
                    self.api_client.change_password("primoaccesso", new_pw)
                    CustomMessageDialog.show_info(self, "Successo", "Password aggiornata. Procedi pure.")
                    return True
                except Exception as e:
                    err = str(e)
                    if hasattr(e, 'response'):
                        try: err = e.response.json()['detail']
                        except Exception: pass
                    CustomMessageDialog.show_error(self, "Errore", f"Errore cambio password: {err}")
            else:
                self.api_client.logout()
                self.login_btn.set_loading(False)
                return False

    def _check_read_only(self, user_info):
        """Displays warning if read-only."""
        if user_info.get("read_only"):
            owner = user_info.get("lock_owner") or {}
            msg = f"⚠️ DATABASE IN USO\n\nUtente: {owner.get('username', 'N/A')}\nHost: {owner.get('hostname', 'N/A')}\nPID: {owner.get('pid', 'N/A')}\n\nL'applicazione si avvierà in modalità SOLA LETTURA.\nNon sarà possibile salvare nuove modifiche."
            CustomMessageDialog.show_warning(self, "Modalità Sola Lettura", msg)

    def _fetch_pending_count(self):
        """Fetches pending certificates count."""
        try:
            cert_list = self.api_client.get("certificati", params={"validated": "false"})
            self.pending_count = len(cert_list)
        except Exception as e:
            print(f"[LoginView] Error fetching pending count: {e}")
            self.pending_count = 0

    def on_login_success(self, response):
        # S3776: Refactored to reduce complexity
        try:
            self.api_client.set_token(response)
            user_info = self.api_client.user_info

            if user_info.get("require_password_change"):
                if user_info.get("read_only"):
                     CustomMessageDialog.show_warning(self, "Attenzione", "È richiesto il cambio password, ma il database è in sola lettura. Riprova più tardi.")
                elif not self._handle_password_change():
                    return

            self._check_read_only(user_info)
            self._fetch_pending_count()
            self._prepare_welcome_message(user_info)
            self._animate_success_exit()

        except Exception as e:
            self._on_login_error(str(e))
            self.login_btn.set_loading(False)

    def _animate_success_exit(self):
        """
        Triggers the 'Spectacular' Cinematic 3D Warp Transition.
        """
        # Fade Out UI
        self.opacity_effect = QGraphicsOpacityEffect(self.container)
        self.container.setGraphicsEffect(self.opacity_effect)
        
        self.anim_fade = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_fade.setDuration(200)
        self.anim_fade.setStartValue(1.0)
        self.anim_fade.setEndValue(0.0)
        self.anim_fade.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim_fade.start()

        # Trigger Neural Warp
        self.neural_engine.start_warp()

        # Schedule Completion
        QTimer.singleShot(1200, self._finish_login_transition)

    def _finish_login_transition(self):
        self._stop_3d_rendering = True
        self._anim_timer.stop()
        self.login_success.emit(self.api_client.user_info)
