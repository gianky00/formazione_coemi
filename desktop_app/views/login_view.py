import os
import sys
import socket
import platform
import math
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QMessageBox, QHBoxLayout,
                             QGraphicsOpacityEffect, QGraphicsDropShadowEffect, QApplication, QPushButton,
                             QDialog, QLineEdit, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QPoint, QEasingCurve, QTimer, QObject, QThread, QThreadPool, QParallelAnimationGroup, QSequentialAnimationGroup, QRect
from PyQt6.QtGui import QPixmap, QColor, QFont, QPainter, QLinearGradient
from desktop_app.utils import get_asset_path
from desktop_app.components.animated_widgets import AnimatedButton, AnimatedInput
from desktop_app.components.custom_dialog import CustomMessageDialog
from desktop_app.services.license_manager import LicenseManager
from desktop_app.services.license_updater_service import LicenseUpdaterService
from desktop_app.services.hardware_id_service import get_machine_id
from desktop_app.workers.worker import Worker

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

class LicenseUpdateWorker(QObject):
    """Worker to run license update in a separate thread."""
    finished = pyqtSignal(bool, str)

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client

    def run(self):
        hw_id = get_machine_id()
        if not hw_id:
            self.finished.emit(False, "Impossibile recuperare l'Hardware ID della macchina.")
            return

        updater = LicenseUpdaterService(self.api_client)
        success, message = updater.update_license(hw_id)
        self.finished.emit(success, message)


class LoginView(QWidget):
    login_success = pyqtSignal(dict) # Emits user_info dict

    def __init__(self, api_client, license_ok=True, license_error=""):
        super().__init__()
        self.api_client = api_client
        self.threadpool = QThreadPool()

        # --- Animated Gradient Background Setup ---
        self._gradient_shift = 0
        self._gradient_timer = QTimer(self)
        self._gradient_timer.timeout.connect(self._update_gradient)
        self._gradient_timer.start(50) # 20 FPS is enough for slow background

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
        if license_data and "Hardware ID" in license_data:
            stored_hw_id = license_data["Hardware ID"]
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
        if LicenseManager.is_license_expiring_soon(license_data):
            license_label.setStyleSheet("color: #FBBF24; font-size: 13px; font-weight: 600;")
        else:
            license_label.setStyleSheet("color: #93C5FD; font-size: 13px; font-weight: 500;")
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
        hostname_label.setStyleSheet("color: #93C5FD; font-size: 13px; font-weight: 500;")
        pc_details_layout.addWidget(hostname_label)

        # OS
        os_name = f"{platform.system()} {platform.release()}"
        os_label = QLabel(f"Sistema Operativo: {os_name}")
        os_label.setStyleSheet("color: #93C5FD; font-size: 13px; font-weight: 500;")
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

        self.welcome_title = QLabel("Bentornato")
        self.welcome_title.setStyleSheet("color: #1F2937; font-size: 32px; font-weight: 700;")
        right_layout.addWidget(self.welcome_title)
        self.animated_widgets.append(self.welcome_title)

        self.welcome_sub = QLabel("Accedi al tuo account per continuare")
        self.welcome_sub.setStyleSheet("color: #6B7280; font-size: 15px;")
        right_layout.addWidget(self.welcome_sub)
        self.animated_widgets.append(self.welcome_sub)

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
        self.animated_widgets.append(self.username_input)

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
        self.animated_widgets.append(self.password_input)

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
        self.animated_widgets.append(self.login_btn)

        right_layout.addStretch()
        right_layout.addStretch(1)

        footer_text = "v1.0.0 • Intelleo Security"
        footer_layout = QVBoxLayout()
        ver_label = QLabel(footer_text)
        ver_label.setStyleSheet("color: #6B7280; font-size: 13px;")
        ver_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(ver_label)
        right_layout.addLayout(footer_layout)
        self.animated_widgets.append(ver_label) # Animate footer too

        container_layout.addWidget(self.left_panel, 40)
        container_layout.addWidget(self.right_panel, 60)

        main_layout.addWidget(self.container)

        self.setup_entrance_animation()

        if not license_ok:
            self.username_input.setEnabled(False)
            self.password_input.setEnabled(False)
            self.login_btn.setEnabled(False)
            error_label = QLabel("Licenza non valida o scaduta. Aggiornala per continuare.")
            error_label.setStyleSheet("color: #DC2626; font-size: 14px; font-weight: 500;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            right_layout.insertWidget(5, error_label)

        self._auto_update_if_needed()

    def _update_gradient(self):
        self._gradient_shift += 0.005
        if self._gradient_shift > 1:
            self._gradient_shift = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw Animated Gradient
        width = self.width()
        height = self.height()

        # Oscillate color factor based on shift
        factor = (math.sin(self._gradient_shift * 2 * math.pi) + 1) / 2 # 0 to 1

        c1 = QColor("#F0F8FF") # Alice Blue
        c2 = QColor("#DBEAFE") # Blue 100

        # Interpolate
        r = int(c1.red() + (c2.red() - c1.red()) * factor)
        g = int(c1.green() + (c2.green() - c1.green()) * factor)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * factor)

        painter.fillRect(self.rect(), QColor(r, g, b))

    def _auto_update_if_needed(self):
        from desktop_app.services.path_service import get_license_dir
        license_dir = get_license_dir()
        required_files = ["pyarmor.rkey", "config.dat", "manifest.json"]
        if any(not os.path.exists(os.path.join(license_dir, f)) for f in required_files):
            QTimer.singleShot(1000, self.handle_update_license)

    def handle_update_license(self):
        self.update_btn.setText("Aggiornamento in corso...")
        self.update_btn.setEnabled(False)

        self.thread = QThread()
        self.worker = LicenseUpdateWorker(self.api_client)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_update_finished)

        self.thread.start()

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

        self.thread.quit()
        self.thread.wait()

    def setup_entrance_animation(self):
        # 1. Main Container Entrance
        self.opacity_effect = QGraphicsOpacityEffect(self.container)
        self.container.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

        self.anim_opacity = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_opacity.setDuration(1000)
        self.anim_opacity.setStartValue(0)
        self.anim_opacity.setEndValue(1)
        self.anim_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 2. Staggered Entrance for Right Panel Elements
        self.staggered_group = QSequentialAnimationGroup(self)

        # Prepare widgets for animation
        self.widget_effects = []
        for widget in self.animated_widgets:
            eff = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(eff)
            eff.setOpacity(0)
            self.widget_effects.append(eff)

        # Add animations to group with small delays
        # But QSequential runs one after another.
        # If we want overlap (cascade), we use QParallel with delays?
        # Or simpler: QTimer triggers?
        # QSequential is fine if durations are short.
        # Let's use a Parallel group where each animation has a StartDelay.

        self.cascade_group = QParallelAnimationGroup(self)

        # Add Container animation to the mix? No, separate start.

        delay = 200 # Start after container is visible
        for i, effect in enumerate(self.widget_effects):
            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(600)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.Type.OutQuad)

            # Since QPropertyAnimation doesn't have setStartDelay (only in AnimationGroup via pausing?),
            # Wait, QAnimationGroup has no setStartDelay for children easily.
            # We can pause the animation?
            # Actually, standard way is creating a Sequential Group [Pause(delay), Anim].

            seq = QSequentialAnimationGroup()
            seq.addPause(delay + (i * 100)) # Stagger by 100ms
            seq.addAnimation(anim)

            self.cascade_group.addAnimation(seq)

    def showEvent(self, event):
        super().showEvent(event)
        self.anim_opacity.start()
        self.cascade_group.start()

    def read_license_info(self):
        data = LicenseManager.get_license_data()

        if not data:
            return "Dettagli licenza non disponibili. Procedere con l'aggiornamento.", None

        lines = []
        if "Cliente" in data:
            lines.append(f"Cliente: {data['Cliente']}")
        if "Scadenza Licenza" in data:
            lines.append(f"Scadenza: {data['Scadenza Licenza']}")
        if "Hardware ID" in data:
            lines.append(f"ID Licenza: {data['Hardware ID']}")

        return "\n".join(lines), data

    def shake_window(self):
        animation = QPropertyAnimation(self.container, b"pos")
        animation.setDuration(100)
        animation.setLoopCount(3)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        current_pos = self.container.pos()

        # Create keyframes relative to current position
        # But if container moves (resize), current_pos is stale?
        # QPropertyAnimation on pos works in global coords usually or parent coords.
        # Here parent is "self" (centered).
        # Better to animate property "geometry"? Or just use the existing logic.

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
            CustomMessageDialog.show_warning(self, "Errore", "Inserisci nome utente e password.")
            return

        _, license_data = self.read_license_info()
        if license_data and "Hardware ID" in license_data:
            stored_hw_id = license_data["Hardware ID"]
            current_hw_id = get_machine_id()
            if stored_hw_id != current_hw_id:
                CustomMessageDialog.show_error(self, "Errore di Licenza",
                                     "L'Hardware ID della licenza non corrisponde a quello di questa macchina.\n"
                                     "Contattare il supporto per una nuova licenza.")
                return

        # Start Threaded Login
        self.login_btn.set_loading(True)
        worker = Worker(self.api_client.login, username=username, password=password)
        worker.signals.result.connect(self._on_login_success_internal)
        worker.signals.error.connect(self._on_login_error)
        self.threadpool.start(worker)

    def _on_login_error(self, error_tuple):
        self.login_btn.set_loading(False)
        self.shake_window()

        exctype, value, tb = error_tuple
        error_msg = "Credenziali non valide o errore del server."

        # Extract detail from requests exception if available
        e = value
        if hasattr(e, 'response') and e.response is not None:
             try:
                 detail = e.response.json().get('detail')
                 if detail: error_msg = detail
             except: pass

        CustomMessageDialog.show_error(self, "Errore di Accesso", error_msg)

    def _on_login_success_internal(self, response):
        try:
            self.api_client.set_token(response)
            user_info = self.api_client.user_info

            if user_info.get("require_password_change"):
                if user_info.get("read_only"):
                     CustomMessageDialog.show_warning(self, "Attenzione", "È richiesto il cambio password, ma il database è in sola lettura. Riprova più tardi.")
                else:
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
                                # This is sync, but acceptable for modal dialog
                                self.api_client.change_password("primoaccesso", new_pw)
                                CustomMessageDialog.show_info(self, "Successo", "Password aggiornata. Procedi pure.")
                                break
                            except Exception as e:
                                err = str(e)
                                if hasattr(e, 'response'):
                                    try: err = e.response.json()['detail']
                                    except: pass
                                CustomMessageDialog.show_error(self, "Errore", f"Errore cambio password: {err}")
                        else:
                            self.api_client.logout()
                            self.login_btn.set_loading(False)
                            return

            if user_info.get("read_only"):
                owner = user_info.get("lock_owner") or {}
                msg = "⚠️ DATABASE IN USO\n\n"
                msg += f"Utente: {owner.get('username', 'N/A')}\n"
                msg += f"Host: {owner.get('hostname', 'N/A')}\n"
                msg += f"PID: {owner.get('pid', 'N/A')}\n\n"
                msg += "L'applicazione si avvierà in modalità SOLA LETTURA.\n"
                msg += "Non sarà possibile salvare nuove modifiche."
                CustomMessageDialog.show_warning(self, "Modalità Sola Lettura", msg)

            # Trigger Fly-Out Animation before emitting success
            self._animate_success_exit()

        except Exception as e:
            self._on_login_error((type(e), e, None))
            self.login_btn.set_loading(False)

    def _animate_success_exit(self):
        # Stop background animation
        self._gradient_timer.stop()

        # Fly Out Animation
        # We animate opacity out and maybe scale up or down

        self.anim_exit = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_exit.setDuration(500)
        self.anim_exit.setStartValue(1)
        self.anim_exit.setEndValue(0)
        self.anim_exit.setEasingCurve(QEasingCurve.Type.InBack)

        # Connect finished signal to actual emit
        self.anim_exit.finished.connect(lambda: self.login_success.emit(self.api_client.user_info))
        self.anim_exit.start()
