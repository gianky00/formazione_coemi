import os
import sys
import traceback
import requests
import json
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtCore import Qt

# Adjust Path for Imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from desktop_app.api_client import APIClient
from desktop_app.main_window_ui import MainDashboardWidget
from desktop_app.views.login_view import LoginView
from desktop_app.components.custom_dialog import CustomMessageDialog
from desktop_app.ipc_bridge import IPCBridge
from desktop_app.components.animated_widgets import AnimatedStackedWidget
from desktop_app.services.license_manager import LicenseManager
from desktop_app.utils import get_asset_path

def setup_styles(app):
    # Load Inter Font
    # (Assuming fonts are installed or loaded here)
    pass

    # Global Stylesheet
    app.setStyleSheet("""
        QMainWindow {
            background-color: #F0F8FF;
        }
        QLabel {
            font-family: 'Inter', sans-serif;
            color: #1F2937;
        }
        QPushButton {
            font-family: 'Inter', sans-serif;
        }
        QLineEdit {
            font-family: 'Inter', sans-serif;
        }
        QFrame#sidebar {
            background-color: #1E3A8A;
            border-right: 1px solid #E5E7EB;
        }
        QLabel#logo_label {
            color: #FFFFFF;
            font-weight: 800;
            font-size: 22px;
        }
        QLabel#version_label {
            color: #9CA3AF;
        }
    """)

class MasterWindow(QMainWindow):
    def __init__(self, controller, license_ok, license_error):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Intelleo")
        self.resize(1280, 800)

        self.stack = AnimatedStackedWidget()
        self.setCentralWidget(self.stack)

        # Initialize Views
        self.login_view = LoginView(controller.api_client, license_ok=license_ok, license_error=license_error)
        self.login_view.login_success.connect(controller.on_login_success)

        self.dashboard_view = None # Lazy init

        self.stack.addWidget(self.login_view) # Index 0

    def show_login(self):
        self.stack.fade_in(0)

    def show_dashboard(self, dashboard_widget):
        # Ensure added
        if self.stack.indexOf(dashboard_widget) == -1:
            self.stack.addWidget(dashboard_widget)

        index = self.stack.indexOf(dashboard_widget)
        self.stack.fade_in(index)

    def closeEvent(self, event):
        """
        Intercept application close event to ensure robust logout and database cleanup.
        """
        if self.controller and self.controller.api_client.access_token:
            try:
                print("[DEBUG] Application closing: Triggering logout/cleanup...")
                # This call is blocking and triggers backend DB save + unlock
                self.controller.api_client.logout()
            except Exception as e:
                print(f"[ERROR] Cleanup failed during close: {e}")

        event.accept()

class ApplicationController:
    def __init__(self, license_ok=True, license_error=""):
        print("[DEBUG] ApplicationController.__init__ started")
        self.api_client = APIClient()
        print("[DEBUG] APIClient initialized. Creating MasterWindow...")
        self.master_window = MasterWindow(self, license_ok, license_error)
        self.dashboard = None
        self.pending_action = None # Generalized from pending_analysis_path

        # Connect IPC Bridge
        self.ipc_bridge = IPCBridge.instance()
        self.ipc_bridge.action_received.connect(self.handle_ipc_action)

        print("[DEBUG] ApplicationController initialized.")

    def start(self):
        print("[DEBUG] ApplicationController.start called. Showing Max Window.")
        self.master_window.showMaximized()
        self.master_window.activateWindow()
        self.master_window.raise_()
        self.setup_jumplist()

        # Check Backend Health to catch Startup Errors (e.g. DB Lock)
        self.check_backend_health()

    def setup_jumplist(self):
        """
        Attempts to create Windows Taskbar Jumplist shortcuts.
        Protected against import errors on non-Windows platforms.
        """
        if os.name != 'nt':
            return
        pass

    def check_backend_health(self):
        try:
            url = f"{self.api_client.base_url}/health"
            # Short timeout check
            response = requests.get(url, timeout=2)

            # 503 Service Unavailable is used for Critical Startup Errors (like DB Lock)
            if response.status_code == 503:
                try:
                    detail = response.json().get("detail", "Errore sconosciuto")
                except:
                    detail = response.text

                CustomMessageDialog.show_error(self.master_window, "Errore Critico Database", f"Impossibile avviare l'applicazione:\n\n{detail}")
                sys.exit(1)

        except Exception as e:
            print(f"[DEBUG] Health Check Warning: {e}")
            # We proceed, as network errors might be temporary or handled by LoginView
            pass

    def handle_ipc_action(self, action: str, payload: dict):
        """
        Handles actions received from external instances (IPC).
        """
        print(f"[CONTROLLER] IPC Action Received: {action} Data: {payload}")

        # Bring window to front
        self.master_window.showMaximized()
        self.master_window.activateWindow()
        self.master_window.raise_()

        if action == "analyze":
            path = payload.get("path")
            if path:
                self.analyze_path(path)
        elif action == "import_csv":
            path = payload.get("path")
            if path:
                self.import_dipendenti_csv(path)
        elif action == "view":
            view_name = payload.get("view_name")
            if view_name and self.dashboard:
                self.dashboard.switch_to(view_name)

    def analyze_path(self, path):
        """
        Triggers analysis (file or folder).
        """
        if self.dashboard and getattr(self.dashboard, 'is_read_only', False):
            CustomMessageDialog.show_warning(self.master_window, "Sola Lettura", "Impossibile avviare l'analisi in modalità Sola Lettura.")
            return

        if self.dashboard:
            self.dashboard.analyze_path(path)
        else:
            self.pending_action = {"action": "analyze", "path": path}

    def import_dipendenti_csv(self, path):
        """
        Triggers CSV import logic.
        """
        if self.dashboard and getattr(self.dashboard, 'is_read_only', False):
            CustomMessageDialog.show_warning(self.master_window, "Sola Lettura", "Impossibile importare CSV in modalità Sola Lettura.")
            return

        if not self.dashboard:
             self.pending_action = {"action": "import_csv", "path": path}
             return

        try:
            response = self.api_client.import_dipendenti_csv(path)
            message = response.get("message", "Importazione riuscita.")
            warnings = response.get("warnings", [])

            msg_text = message
            if warnings:
                msg_text += "\n\nAvvisi:\n" + "\n".join(warnings[:5])
                if len(warnings) > 5:
                    msg_text += f"\n...e altri {len(warnings)-5}"

            CustomMessageDialog.show_info(self.master_window, "Importazione Completata", msg_text)

            # Refresh data if needed (Dashboard usually auto-refreshes on tab switch, but we can force it)
            if self.dashboard:
                # Trigger refresh on validation/dashboard if needed
                pass

        except Exception as e:
            CustomMessageDialog.show_error(self.master_window, "Errore Importazione", f"Impossibile importare il file:\n{e}")

    def on_login_success(self, user_info):
        try:
            # Create Dashboard if not exists
            if not self.dashboard:
                self.dashboard = MainDashboardWidget(self.api_client)
                self.dashboard.logout_requested.connect(self.on_logout)

            # Propagate Read-Only State
            is_read_only = user_info.get("read_only", False)
            self.dashboard.set_read_only_mode(is_read_only)

            # Update User Info in Sidebar
            account_name = user_info.get("account_name") or user_info.get("username")

            prev_login_raw = user_info.get("previous_login")
            if prev_login_raw and str(prev_login_raw).lower() != "none":
                try:
                    # Handle simplified ISO format (remove 'Z' if present)
                    if isinstance(prev_login_raw, str):
                        ts = prev_login_raw.replace('Z', '')
                        from datetime import datetime
                        dt = datetime.fromisoformat(ts)
                        # AGGIUNTO \n per forzare il ritorno a capo
                        display_str = dt.strftime("%d/%m/%Y\n%H:%M")
                    else:
                        display_str = str(prev_login_raw)
                except Exception as e:
                    print(f"[DEBUG] Error parsing previous_login: {e}")
                    display_str = str(prev_login_raw)
            else:
                display_str = "Primo Accesso"

            self.dashboard.sidebar.set_user_info(account_name, display_str)

            # Transition
            self.master_window.show_dashboard(self.dashboard)

            # Handle deferred action
            if self.pending_action:
                if is_read_only:
                    CustomMessageDialog.show_warning(self.master_window, "Sola Lettura",
                                        "L'azione richiesta è stata annullata perché il database è in modalità Sola Lettura.")
                else:
                    action = self.pending_action.get("action")
                    if action == "analyze":
                        self.dashboard.analyze_path(self.pending_action.get("path"))
                    elif action == "import_csv":
                        self.import_dipendenti_csv(self.pending_action.get("path"))

                self.pending_action = None
        except Exception as e:
            traceback.print_exc()
            CustomMessageDialog.show_error(self.master_window, "Errore Dashboard", f"Errore durante il caricamento della dashboard:\n{e}")

    def on_logout(self):
        self.api_client.logout()
        self.master_window.show_login()
        # Optional: Destroy dashboard to reset state completely
        if self.dashboard:
            self.dashboard.deleteLater()
            self.dashboard = None

def restart_app():
    """Restarts the current application."""
    # Find the executable and start a new process
    QApplication.instance().quit()
    os.execv(sys.executable, [sys.executable] + sys.argv)

# Global Exception Hook
def exception_hook(exctype, value, tb):
    traceback.print_exception(exctype, value, tb)
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    print(f"CRITICAL ERROR: {err_msg}")

    # Try to show dialog if App is running
    app = QApplication.instance()
    if app:
        # Create a simple box just in case CustomMessageDialog fails
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText("Errore Critico")
        msg.setInformativeText(f"L'applicazione ha riscontrato un errore imprevisto e deve essere chiusa.\n\n{str(value)}")
        msg.setDetailedText(err_msg)
        msg.exec()
        sys.exit(1)

if __name__ == "__main__":
    sys.excepthook = exception_hook

    # Check for duplicate instance (simple port bind check or lock file is better, but here we assume Launcher did it)
    # Launcher handles port selection.

    app = QApplication(sys.argv)
    setup_styles(app)

    # Check license
    # We should probably do this in a Splash Screen or Controller
    # But for now, Controller handles it via LoginView params

    # NOTE: In frozen build, we might need to check license existence here if we want to block startup?
    # But current design passes checks to Controller/LoginView.

    # Determine license status for initial UI
    license_ok = True
    license_error = ""
    try:
        from desktop_app.services.license_manager import LicenseManager
        # Just check if files exist? No, deep check is in LoginView update logic
        # We assume OK and let LoginView handle expiry/missing.
        pass
    except Exception as e:
        print(f"License check warning: {e}")

    controller = ApplicationController(license_ok=license_ok, license_error=license_error)
    controller.start()

    sys.exit(app.exec())
