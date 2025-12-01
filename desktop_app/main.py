import sys
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer

# --- IMPORT FONDAMENTALE ---
from .main_window_ui import MainDashboardWidget
from .views.login_view import LoginView
from .api_client import APIClient
from .components.animated_stacked_widget import AnimatedStackedWidget
from .components.custom_dialog import CustomMessageDialog
from .components.toast import ToastNotification
from .ipc_bridge import IPCBridge
import os

def setup_styles(app: QApplication):
    """
    Configura il font e il foglio di stile (CSS) dell'applicazione.
    """
    # Set a modern font
    font = QFont("Inter")
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    # Global stylesheet for a modern look
    app.setStyleSheet("""
            /* Global Styles */
            QMainWindow, QWidget {
                font-family: "Inter", "Segoe UI";
                background-color: #F0F8FF;
                color: #1F2937;
            }

            /* Card Styles */
            .card, QFrame#card {
                background-color: #FFFFFF;
                border-radius: 12px;
                padding: 24px;
                border: 1px solid #E5E7EB;
            }

            /* Sidebar Styles */
            Sidebar {
                background-color: #1E3A8A; /* Blue-900 */
                border-right: 1px solid #1E3A8A;
            }
            Sidebar QWidget {
                background-color: transparent;
                color: #FFFFFF;
            }
            Sidebar QFrame#sidebar_header {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E5E7EB;
            }
            Sidebar QPushButton#toggle_btn {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 4px;
                margin: 0px;
                color: #FFFFFF;
            }
            Sidebar QPushButton#toggle_btn:hover {
                background-color: rgba(31, 41, 55, 0.1);
            }
            Sidebar QPushButton[nav_btn="true"] {
                text-align: left;
                padding: 12px 16px;
                border: none;
                font-size: 15px;
                font-weight: 500;
                border-radius: 8px;
                margin: 4px 12px;
                color: #FFFFFF;
                background-color: transparent;
            }
            Sidebar QPushButton[nav_btn="true"][centered="true"] {
                text-align: center;
                padding: 12px;
                margin: 4px 8px;
            }
            Sidebar QPushButton[nav_btn="true"]:hover {
                background-color: rgba(29, 78, 216, 0.4);
            }
            Sidebar QPushButton[nav_btn="true"]:checked {
                background-color: #1D4ED8;
                color: #FFFFFF;
                font-weight: 600;
                border-left: 3px solid #60A5FA;
            }
            Sidebar QLabel#version_label {
                color: #93C5FD;
                font-size: 14px;
                padding: 10px;
                font-weight: 500;
            }

            /* Table Styles */
            QTableView {
                border: none;
                gridline-color: #E5E7EB;
                background-color: #FFFFFF;
                border-radius: 12px;
            }
            QTableView::item {
                padding: 12px;
                border-bottom: 1px solid #E5E7EB;
                color: #1F2937;
            }
            QTableView::item:selected {
                background-color: #EFF6FF;
                color: #1E40AF;
            }
            QHeaderView {
                background-color: #F9FAFB;
            }
            QHeaderView::section {
                background-color: #F9FAFB;
                padding: 12px;
                border: none;
                border-bottom: 1px solid #E5E7EB;
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                color: #6B7280;
            }

            /* Buttons */
            QPushButton {
                padding: 10px 20px;
                border: 1px solid #1D4ED8;
                border-radius: 8px;
                background-color: #1D4ED8;
                color: white;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
            QPushButton:pressed {
                background-color: #1E3A8A;
            }
            QPushButton:disabled {
                background-color: #E5E7EB;
                border-color: #D1D5DB;
                color: #9CA3AF;
            }
            QPushButton.secondary, QPushButton#secondary {
                background-color: #FFFFFF;
                color: #1F2937;
                border: 1px solid #D1D5DB;
            }
            QPushButton.secondary:hover, QPushButton#secondary:hover {
                background-color: #F9FAFB;
                border-color: #9CA3AF;
            }
            QPushButton.destructive, QPushButton#destructive {
                background-color: #DC2626;
                border-color: #DC2626;
                color: white;
            }
            QPushButton.destructive:hover, QPushButton#destructive:hover {
                background-color: #B91C1C;
            }
            QPushButton#primary {
                 /* Same as default */
            }

            /* Inputs (LineEdit, DateEdit, TextEdit) */
            QLineEdit, QDateEdit, QTextEdit {
                padding: 8px 12px;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                font-size: 14px;
                background-color: #FFFFFF;
                color: #1F2937;
            }
            QLineEdit:hover, QDateEdit:hover, QTextEdit:hover {
                border-color: #3B82F6; /* Blue-500 */
            }
            QLineEdit:focus, QDateEdit:focus, QTextEdit:focus {
                border: 2px solid #2563EB; /* Blue-600 */
                padding: 7px 11px; /* Adjust padding to prevent layout shift */
            }

            /* ComboBox Styles */
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                color: #1F2937;
                min-width: 120px;
            }
            QComboBox:hover {
                border-color: #3B82F6; /* Blue-500 */
                background-color: #F9FAFB;
            }
            QComboBox:focus {
                border: 2px solid #2563EB; /* Blue-600 */
                padding: 7px 11px; /* Compensate for border width */
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 0px;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                background-color: transparent;
            }
            QComboBox::down-arrow {
                image: url(desktop_app/icons/lucide/chevron-down.svg);
                width: 16px;
                height: 16px;
            }
            /* Popup (Drop-down list) */
            QComboBox QAbstractItemView {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background-color: #FFFFFF;
                selection-background-color: #EFF6FF;
                selection-color: #1E3A8A;
                outline: none;
                padding: 4px;
                min-width: 140px; /* Ensure popup isn't too thin */
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                min-height: 24px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #F3F4F6;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #EFF6FF;
                color: #1E40AF;
                font-weight: 600;
            }

            /* ScrollBar Styling for cleanliness */
            QScrollBar:vertical {
                border: none;
                background: #F1F5F9;
                width: 8px;
                margin: 0px 0px 0px 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }

            /* Calendar Widget Styling Fix */
            QCalendarWidget QToolButton {
                color: #1F2937;
                background-color: transparent;
                icon-size: 16px;
            }
            QCalendarWidget QMenu {
                background-color: #FFFFFF;
                color: #1F2937;
            }
            QCalendarWidget QSpinBox {
                color: #1F2937;
                background-color: #FFFFFF;
                selection-background-color: #1D4ED8;
                selection-color: #FFFFFF;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #F9FAFB;
                border-bottom: 1px solid #E5E7EB;
            }
            /* Override generic QTableView styles for Calendar to prevent squashing */
            QCalendarWidget QTableView {
                border: none;
                background-color: #FFFFFF;
                selection-background-color: #EFF6FF;
            }
            QCalendarWidget QTableView::item {
                padding: 4px; /* Reset padding from 12px to 4px */
                border: none;
                color: #1F2937;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #1F2937;
                background-color: #FFFFFF;
                selection-background-color: #1D4ED8;
                selection-color: #FFFFFF;
            }
            QCalendarWidget QAbstractItemView:disabled {
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
        self.notification = None # Store reference to prevent GC
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

        # NOTE: Full Jumplist creation via ICustomDestinationList is complex in Python.
        # However, we rely on the OS's native "Recent" file list which populates automatically
        # for registered file types (.pdf, .csv).
        # Static tasks are best handled by the Installer or simplified "Pin to Taskbar" actions.
        # This method is a placeholder for future advanced implementation if pywin32 extensions are fully leveraged.
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

    def show_notification(self, title, message, icon_name="file-text.svg"):
        """Displays a toast notification."""
        self.notification = ToastNotification(self.master_window, title, message, icon_name=icon_name)
        self.notification.show_toast()

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

        # Show notification that import is starting? Or just do it.
        # It's blocking via API Client usually, better to run in thread?
        # API Client calls are synchronous requests. UI might freeze for large files.
        # But CSVs are small.
        try:
            response = self.api_client.import_dipendenti_csv(path)
            message = response.get("message", "Importazione riuscita.")
            # We simplify the message for the toast
            self.show_notification("Importazione Completata", message, icon_name="users.svg")

            # Refresh data if needed (Dashboard usually auto-refreshes on tab switch, but we can force it)
            if self.dashboard:
                # Trigger refresh on validation/dashboard if needed
                pass

        except Exception as e:
            CustomMessageDialog.show_error(self.master_window, "Errore Importazione", f"Impossibile importare il file:\n{e}")

    def on_login_success(self, user_info):
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

        # Connect notification signal from dashboard
        self.dashboard.notification_requested.connect(self.show_notification)

        # Transition
        self.master_window.show_dashboard(self.dashboard)

        # Check for pending documents notification
        pending_count = user_info.get("pending_documents_count", 0)
        if pending_count > 0:
            msg_title = "Convalida Dati"
            if pending_count == 1:
                msg_text = "C'è un documento da convalidare."
            else:
                msg_text = f"Ci sono {pending_count} documenti da convalidare."

            # Delay toast slightly to allow dashboard transition to complete
            QTimer.singleShot(800, lambda: self.show_notification(msg_title, msg_text, "file-text.svg"))

        # Check for expiring certificates (Business Logic)
        try:
            # We fetch all certificates to check for expiring ones (simple client-side filter)
            # This is acceptable for the expected volume (3-4 docs/employee * ~100 employees)
            all_certs = self.api_client.get("certificati")
            expiring_count = 0
            for cert in all_certs:
                status = cert.get("stato_certificato")
                if status == "in_scadenza" or status == "scaduto":
                    expiring_count += 1

            if expiring_count > 0:
                scad_title = "Scadenze Imminenti"
                scad_text = f"Ci sono {expiring_count} certificati in scadenza o scaduti."
                # Schedule this toast to appear after the first one (e.g. 4 seconds later)
                delay = 4500 if pending_count > 0 else 1000
                QTimer.singleShot(delay, lambda: self.show_notification(scad_title, scad_text, "calendar.svg"))
        except Exception as e:
            print(f"[Controller] Error fetching expiring certs: {e}")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    setup_styles(app)

    controller = ApplicationController()
    controller.start()

    sys.exit(app.exec())
