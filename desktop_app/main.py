import sys
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer, QObject, pyqtSignal, QEvent
import sentry_sdk
import os
import traceback as tb

# --- IMPORT FONDAMENTALE ---
from .main_window_ui import MainDashboardWidget
from .views.login_view import LoginView
from .api_client import APIClient
from .components.animated_stacked_widget import AnimatedStackedWidget
from .components.custom_dialog import CustomMessageDialog
from .components.toast import ToastNotification
from .components.floating_chat_widget import FloatingChatWidget
from .services.voice_service import VoiceService
from .ipc_bridge import IPCBridge
import os
from app.core.db_security import db_security

# --- CONSTANTS ---
STR_SOLA_LETTURA = "Sola Lettura"

class InactivityFilter(QObject):
    reset_timer = pyqtSignal()

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.Type.MouseMove, QEvent.Type.KeyPress, QEvent.Type.MouseButtonPress):
            self.reset_timer.emit()
        return False

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
        
        # --- Floating Chat Widget ---
        # Add to window (absolute positioning over central widget)
        self.chat_widget = FloatingChatWidget(controller.api_client, controller.voice_service, self)
        self.chat_widget.hide() # Hidden until login

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Position Floating Chat at Bottom-Right ONLY if user hasn't moved it
        if hasattr(self, 'chat_widget'):
            if not getattr(self.chat_widget, 'user_has_moved', False):
                padding = 20
                w = self.chat_widget.width()
                h = self.chat_widget.height()
                self.chat_widget.move(self.width() - w - padding, self.height() - h - padding)

    def show_login(self):
        self.stack.fade_in(0)
        self.chat_widget.hide()

    def show_dashboard(self, dashboard_widget):
        # Ensure added
        if self.stack.indexOf(dashboard_widget) == -1:
            self.stack.addWidget(dashboard_widget)

        index = self.stack.indexOf(dashboard_widget)
        self.stack.fade_in(index)
        
        # Show Chat Widget
        self.chat_widget.show()
        self.chat_widget.raise_()
        # Ensure correct position
        self.resizeEvent(None)

    def closeEvent(self, event):
        """
        Intercept application close event to ensure robust logout and database cleanup.
        """
        print("[DEBUG] MasterWindow closing...")
        
        # Stop voice
        if self.controller and hasattr(self.controller, 'voice_service'):
            self.controller.voice_service.cleanup()

        # Stop Dashboard Threads (Graceful Shutdown)
        if self.controller and self.controller.dashboard:
            try:
                print("[DEBUG] Cleaning up dashboard threads...")
                self.controller.dashboard.cleanup()
            except Exception as e:
                print(f"[ERROR] Dashboard cleanup failed: {e}")

        # 1. API Logout (Triggers backend token invalidation)
        if self.controller and self.controller.api_client.access_token:
            try:
                print("[DEBUG] Triggering API logout...")
                # This call is blocking
                self.controller.api_client.logout()
            except Exception as e:
                print(f"[ERROR] API Logout failed during close: {e}")

        # 2. Database Security Cleanup (Release Lock & Save)
        try:
            print("[DEBUG] Releasing Database Lock...")
            db_security.cleanup()
        except Exception as e:
            print(f"[CRITICAL] Database cleanup failed: {e}")

        event.accept()

        # 3. Force Process Termination
        print("[DEBUG] Forcing Application Quit...")
        QApplication.quit()

class ApplicationController:
    def __init__(self, license_ok=True, license_error=""):
        print("[DEBUG] ApplicationController.__init__ started")
        self.api_client = APIClient()
        
        # Init Voice Service
        self.voice_service = VoiceService()
        
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

        # Phase 2: Check for Updates (Non-blocking)
        QTimer.singleShot(3000, self.start_update_check)

    def start_update_check(self):
        """Starts the async update check worker."""
        try:
            from desktop_app.services.update_checker import UpdateWorker
            self.update_worker = UpdateWorker()
            self.update_worker.update_available.connect(self.prompt_update)
            # Ensure cleanup
            self.update_worker.finished.connect(self.update_worker.deleteLater)
            self.update_worker.start()
        except Exception as e:
            print(f"[ERROR] Failed to start update check: {e}")

    def prompt_update(self, version, url):
        """Displays a dialog asking the user to update."""
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl

        reply = QMessageBox.question(
            self.master_window,
            "Aggiornamento Disponibile",
            f"È disponibile una nuova versione ({version}).\n"
            "Vuoi scaricarla ora?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            QDesktopServices.openUrl(QUrl(url))

    def setup_jumplist(self):
        """
        Attempts to create Windows Taskbar Jumplist shortcuts.
        Protected against import errors on non-Windows platforms.
        """
        if os.name != 'nt':
            return
        # S2772: Removed useless pass

    def check_backend_health(self):
        try:
            url = f"{self.api_client.base_url}/health"
            # Short timeout check
            response = requests.get(url, timeout=2)

            # 503 Service Unavailable is used for Critical Startup Errors (like DB Lock)
            if response.status_code == 503:
                try:
                    detail = response.json().get("detail", "Errore sconosciuto")
                except Exception: # S5754: Specify exception
                    detail = response.text

                CustomMessageDialog.show_error(self.master_window, "Errore Critico Database", f"Impossibile avviare l'applicazione:\n\n{detail}")
                sys.exit(1)

        except Exception as e:
            print(f"[DEBUG] Health Check Warning: {e}")
            # We proceed, as network errors might be temporary or handled by LoginView
            # S2772: Removed useless pass

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

    def _execute_or_defer_action(self, action_name, path, method):
        """Helper to execute method if dashboard exists, else defer."""
        if self.dashboard and method:
            method(path)
        else:
            self.pending_action = {"action": action_name, "path": path}

    def analyze_path(self, path):
        """
        Triggers analysis (file or folder).
        """
        if self.dashboard and getattr(self.dashboard, 'is_read_only', False):
            CustomMessageDialog.show_warning(self.master_window, STR_SOLA_LETTURA, "Impossibile avviare l'analisi in modalità Sola Lettura.")
            return

        self._execute_or_defer_action("analyze", path, self.dashboard.analyze_path if self.dashboard else None)

    def import_dipendenti_csv(self, path):
        """
        Triggers CSV import logic.
        """
        if self.dashboard and getattr(self.dashboard, 'is_read_only', False):
            CustomMessageDialog.show_warning(self.master_window, STR_SOLA_LETTURA, "Impossibile importare CSV in modalità Sola Lettura.")
            return

        if not self.dashboard:
             self.pending_action = {"action": "import_csv", "path": path}
             return

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
        self._ensure_dashboard_created()

        # Setup Session Managers
        self._setup_session_managers()

        # Propagate Read-Only State
        is_read_only = user_info.get("read_only", False)
        self.dashboard.set_read_only_mode(is_read_only)

        # Update User Info in Sidebar
        self._update_sidebar_user_info(user_info)

        # Connect Signals
        self._connect_dashboard_signals()
        
        # Transition
        self.master_window.show_dashboard(self.dashboard)

        # Voice Welcome
        self._play_welcome_message(user_info)

        # Handle deferred action
        if self.pending_action:
            self._handle_deferred_action(is_read_only)

    def _ensure_dashboard_created(self):
        if not self.dashboard:
            self.dashboard = MainDashboardWidget(self.api_client)
            self.dashboard.logout_requested.connect(self.on_logout)

    def _setup_session_managers(self):
        # Start Inactivity Timer (1 hour)
        self.inactivity_timer = QTimer()
        self.inactivity_timer.setInterval(3600 * 1000) # 1 hour
        self.inactivity_timer.timeout.connect(self.on_session_timeout)
        self.inactivity_timer.start()

        # Install Event Filter
        self.inactivity_filter = InactivityFilter()
        self.inactivity_filter.reset_timer.connect(self.reset_inactivity_timer)
        QApplication.instance().installEventFilter(self.inactivity_filter)

    def _update_sidebar_user_info(self, user_info):
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

    def _connect_dashboard_signals(self):
        # Connect notification signal from dashboard
        try:
            self.dashboard.notification_requested.connect(self.show_notification)
            # Connect Analysis Completion for Voice
            self.dashboard.analysis_finished.connect(self.on_analysis_finished)
        except Exception:
            pass # Already connected

    def _play_welcome_message(self, user_info):
        try:
            account_name = user_info.get("account_name") or user_info.get("username")
            all_certs = self.api_client.get("certificati")
            expiring_count = 0
            for cert in all_certs:
                status = cert.get("stato_certificato")
                if status == "in_scadenza":
                    expiring_count += 1
            
            expired_count = sum(1 for c in all_certs if c.get("stato_certificato") == "scaduto")
            total_issues = expiring_count + expired_count
            
            message_text = f"Bentornato {account_name}."
            if total_issues > 0:
                message_text += f" Ci sono {total_issues} certificati che richiedono attenzione."
            else:
                message_text += " La situazione è sotto controllo."
                
            QTimer.singleShot(1500, lambda: self.voice_service.speak(message_text))
            
        except Exception as e:
            print(f"[Controller] Error fetching expiring certs for welcome message: {e}")

    def _handle_deferred_action(self, is_read_only):
        """Executes any pending action after login."""
        if is_read_only:
            CustomMessageDialog.show_warning(self.master_window, STR_SOLA_LETTURA,
                                "L'azione richiesta è stata annullata perché il database è in modalità Sola Lettura.")
        else:
            action = self.pending_action.get("action")
            path = self.pending_action.get("path")
            if action == "analyze":
                self.dashboard.analyze_path(path)
            elif action == "import_csv":
                self.import_dipendenti_csv(path)

        self.pending_action = None

    def on_analysis_finished(self, archived, verify):
        user_name = "Utente"
        if self.api_client.user_info:
            user_name = self.api_client.user_info.get("account_name") or self.api_client.user_info.get("username")
        
        msg = f"Ehi {user_name}, ho terminato. {archived} documenti archiviati, {verify} da verificare."
        self.voice_service.speak(msg)

    def reset_inactivity_timer(self):
        if hasattr(self, 'inactivity_timer') and self.inactivity_timer.isActive():
            self.inactivity_timer.start() # Reset

    def on_session_timeout(self):
        CustomMessageDialog.show_warning(self.master_window, "Sessione Scaduta", "Sei stato disconnesso per inattività.")
        self.on_logout()

    def on_logout(self):
        if hasattr(self, 'inactivity_timer'):
            self.inactivity_timer.stop()
        if hasattr(self, 'inactivity_filter'):
            QApplication.instance().removeEventFilter(self.inactivity_filter)

        self.api_client.logout()
        self.master_window.show_login()
        self.voice_service.stop()
        
        # Optional: Destroy dashboard to reset state completely
        if self.dashboard:
            self.dashboard.deleteLater()
            self.dashboard = None

def restart_app():
    """Restarts the current application."""
    # Find the executable and start a new process
    QApplication.instance().quit()
    os.execv(sys.executable, [sys.executable] + sys.argv)

def exception_hook(exctype, value, traceback):
    """
    Global exception handler to ensure database cleanup on crash.
    """
    # 1. Capture to Sentry (if initialized here)
    if sentry_sdk.is_initialized():
        sentry_sdk.capture_exception(value)

    # 2. Print Traceback
    print(f"[CRITICAL] Unhandled exception: {exctype}, {value}")
    import traceback as tb
    tb.print_tb(traceback)

    # 3. DB Cleanup
    try:
        print("[CRITICAL] Attempting emergency DB cleanup...")
        db_security.cleanup()
    except Exception as e:
        print(f"[CRITICAL] Emergency cleanup failed: {e}")
        if sentry_sdk.is_initialized():
             sentry_sdk.capture_exception(e)
    sys.exit(1)

if __name__ == "__main__":
    # --- SENTRY INTEGRATION FOR DEV ---
    if not sentry_sdk.is_initialized():
        environment = "production" if getattr(sys, 'frozen', False) else "development"
        SENTRY_DSN = os.environ.get("SENTRY_DSN", "https://f252d598aaf7e70fe94d533474b76639@o4510490492600320.ingest.de.sentry.io/4510490526744656")

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            environment=environment,
            traces_sample_rate=1.0,
            send_default_pii=True
        )

    sys.excepthook = exception_hook
    app = QApplication(sys.argv)
    setup_styles(app)

    controller = ApplicationController()
    controller.start()

    sys.exit(app.exec())
