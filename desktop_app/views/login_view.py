import os
import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QMessageBox, QHBoxLayout,
                             QGraphicsOpacityEffect, QGraphicsDropShadowEffect, QApplication, QPushButton,
                             QDialog, QLineEdit, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QPoint, QEasingCurve, QTimer, QObject, QThread
from PyQt6.QtGui import QPixmap, QColor, QFont
from desktop_app.utils import get_asset_path
from desktop_app.components.animated_widgets import AnimatedButton, AnimatedInput
from desktop_app.services.license_manager import LicenseManager
from desktop_app.services.license_updater_service import LicenseUpdaterService
from desktop_app.services.hardware_id_service import get_machine_id

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
            # Scale to maximize width within the 40% left panel (approx 380px width available)
            # We leave slight padding. Target width ~340-350px.
            scaled = pixmap.scaled(QSize(350, 160), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled)
        else:
            logo_label.setText("INTELLEO")
            logo_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #1E3A8A;")

        left_layout.addStretch()

        # Container for logo to ensure visibility against blue
        logo_container = QFrame()
        logo_container.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 16px;
        """)
        logo_container_layout = QVBoxLayout(logo_container)
        # Reduced margins to eliminate empty space on sides
        logo_container_layout.setContentsMargins(15, 20, 15, 20)
        logo_container_layout.addWidget(logo_label)

        # Removed setFixedSize to allow natural fit
        left_layout.addWidget(logo_container, alignment=Qt.AlignmentFlag.AlignCenter)

        left_layout.addStretch()

        # Container for license info at the bottom-left
        license_info_container = QFrame()
        license_info_layout = QVBoxLayout(license_info_container)
        license_info_layout.setContentsMargins(15, 15, 15, 15)
        license_info_layout.setSpacing(5)

        title_label = QLabel("Dettagli Licenza")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_label.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 600; border-bottom: 1px solid #60A5FA; padding-bottom: 5px;")
        license_info_layout.addWidget(title_label)

        license_text, license_data = self.read_license_info()

        license_label = QLabel(license_text)
        license_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # --- SECURITY FEATURE: Grace Period Warning ---
        if LicenseManager.is_license_expiring_soon(license_data):
            license_label.setStyleSheet("color: #FBBF24; font-size: 13px; font-weight: 600;") # Yellow color for warning
        else:
            license_label.setStyleSheet("color: #93C5FD; font-size: 13px; font-weight: 500;")
        license_label.setWordWrap(True)
        license_info_layout.addWidget(license_label)

        # --- PC DETAILS SECTION ---
        pc_details_layout = QVBoxLayout()
        pc_details_layout.setContentsMargins(15, 15, 15, 15)
        pc_details_layout.setSpacing(5)

        pc_title_label = QLabel("Dettagli PC")
        pc_title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        pc_title_label.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 600; border-bottom: 1px solid #60A5FA; padding-bottom: 5px;")
        pc_details_layout.addWidget(pc_title_label)

        current_hw_id = get_machine_id()
        pc_hw_id_label = QLabel(f"ID Hardware PC: {current_hw_id}")
        pc_hw_id_label.setStyleSheet("color: #93C5FD; font-size: 13px; font-weight: 500;")
        pc_details_layout.addWidget(pc_hw_id_label)

        # --- COHERENCE CHECK ---
        coherence_label = QLabel("")
        coherence_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        if license_data and "Hardware ID" in license_data:
            stored_hw_id = license_data["Hardware ID"]
            if stored_hw_id == current_hw_id:
                coherence_label.setText("Coerenza: Matched")
                coherence_label.setStyleSheet("color: #22C55E; font-size: 13px; font-weight: 600;") # Green
            else:
                coherence_label.setText("Coerenza: Mismatch")
                coherence_label.setStyleSheet("color: #EF4444; font-size: 13px; font-weight: 600;") # Red
        pc_details_layout.addWidget(coherence_label)

        license_info_layout.addLayout(pc_details_layout)

        left_layout.addWidget(license_info_container)

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

        right_layout.addStretch(1)

        # License Update Section
        update_layout = QVBoxLayout()
        update_layout.setSpacing(10)

        hw_id_label = QLabel(f"ID Hardware PC: {get_machine_id()}")
        hw_id_label.setStyleSheet("color: #6B7280; font-size: 11px; font-weight: 500;")
        hw_id_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        update_layout.addWidget(hw_id_label)

        self.update_btn = QPushButton("Aggiorna Licenza")
        self.update_btn.setFixedHeight(35)
        self.update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: #E5E7EB; color: #374151;
                font-weight: 600; font-size: 12px;
                border-radius: 6px; border: 1px solid #D1D5DB;
            }
            QPushButton:hover { background-color: #D1D5DB; }
        """)
        self.update_btn.clicked.connect(self.handle_update_license)
        update_layout.addWidget(self.update_btn)

        right_layout.addLayout(update_layout)
        right_layout.addStretch(2)

        # Footer
        footer_text = "v1.0.0 • Intelleo Security"

        footer_layout = QVBoxLayout()

        ver_label = QLabel(footer_text)
        ver_label.setStyleSheet("color: #6B7280; font-size: 13px;")
        ver_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(ver_label)

        right_layout.addLayout(footer_layout)

        # Add panels to container
        container_layout.addWidget(self.left_panel, 40) # 40% width
        container_layout.addWidget(self.right_panel, 60) # 60% width

        main_layout.addWidget(self.container)

        # Animation Setup
        self.setup_entrance_animation()

        # Handle invalid license state
        if not license_ok:
            self.username_input.setEnabled(False)
            self.password_input.setEnabled(False)
            self.login_btn.setEnabled(False)

            # Add a clear error message
            error_label = QLabel("Licenza non valida o scaduta. Aggiornala per continuare.")
            error_label.setStyleSheet("color: #DC2626; font-size: 14px; font-weight: 500;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            right_layout.insertWidget(5, error_label) # Insert after welcome_sub

        # Auto-trigger license update if files are missing
        self._auto_update_if_needed()

    def _auto_update_if_needed(self):
        from desktop_app.services.path_service import get_license_dir
        license_dir = get_license_dir()
        required_files = ["pyarmor.rkey", "config.dat", "manifest.json"]

        # Check if any of the essential files are missing
        if any(not os.path.exists(os.path.join(license_dir, f)) for f in required_files):
            QTimer.singleShot(1000, self.handle_update_license) # Delay to allow UI to show

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
            # Specific check for the "already up to date" message
            if "già aggiornata" in message:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setText("La licenza risulta aggiornata.")
                msg_box.setWindowTitle("Info Licenza")
                msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
                msg_box.exec()
            else:
                from desktop_app.main import restart_app
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setText(f"{message}\n\nÈ necessario riavviare l'applicazione per applicare le modifiche.")
                msg_box.setWindowTitle("Successo")
                restart_button = msg_box.addButton("Riavvia Ora", QMessageBox.ButtonRole.AcceptRole)
                msg_box.exec()

                if msg_box.clickedButton() == restart_button:
                    restart_app()
        else:
            QMessageBox.critical(self, "Errore Aggiornamento", message)

        self.thread.quit()
        self.thread.wait()

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
        data = LicenseManager.get_license_data()
        hw_id = get_machine_id()

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

        # --- SECURITY CHECK: Hardware ID Mismatch ---
        _, license_data = self.read_license_info()
        if license_data and "Hardware ID" in license_data:
            stored_hw_id = license_data["Hardware ID"]
            current_hw_id = get_machine_id()
            if stored_hw_id != current_hw_id:
                QMessageBox.critical(self, "Errore di Licenza",
                                     "L'Hardware ID della licenza non corrisponde a quello di questa macchina.\n"
                                     "Contattare il supporto per una nuova licenza.")
                return

        try:
            self.login_btn.setText("Accesso in corso...")
            self.login_btn.setEnabled(False)
            self.login_btn.repaint()

            response = self.api_client.login(username, password)
            self.api_client.set_token(response)

            user_info = self.api_client.user_info

            if user_info.get("require_password_change"):
                if user_info.get("read_only"):
                     QMessageBox.warning(self, "Attenzione", "È richiesto il cambio password, ma il database è in sola lettura. Riprova più tardi.")
                else:
                    while True: # Loop until success or cancel
                        dialog = ForcePasswordChangeDialog(self)
                        if dialog.exec():
                            new_pw, confirm_pw = dialog.get_data()
                            if not new_pw:
                                QMessageBox.warning(self, "Errore", "Password vuota.")
                                continue
                            if new_pw != confirm_pw:
                                QMessageBox.warning(self, "Errore", "Le password non coincidono.")
                                continue

                            try:
                                self.api_client.change_password("primoaccesso", new_pw)
                                QMessageBox.information(self, "Successo", "Password aggiornata. Procedi pure.")
                                break
                            except Exception as e:
                                err = str(e)
                                if hasattr(e, 'response'):
                                    try: err = e.response.json()['detail']
                                    except: pass
                                QMessageBox.critical(self, "Errore", f"Errore cambio password: {err}")
                        else:
                            # User cancelled. Disconnect?
                            self.api_client.logout()
                            self.login_btn.setText("Accedi")
                            self.login_btn.setEnabled(True)
                            return

            if user_info.get("read_only"):
                owner = user_info.get("lock_owner") or {}
                msg = "⚠️ DATABASE IN USO\n\n"
                msg += f"Utente: {owner.get('username', 'N/A')}\n"
                msg += f"Host: {owner.get('hostname', 'N/A')}\n"
                msg += f"PID: {owner.get('pid', 'N/A')}\n\n"
                msg += "L'applicazione si avvierà in modalità SOLA LETTURA.\n"
                msg += "Non sarà possibile salvare nuove modifiche."
                QMessageBox.warning(self, "Modalità Sola Lettura", msg)

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
