import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

# --- IMPORT FONDAMENTALE ---
from .main_window_ui import MainWindow
from .views.login_view import LoginView
from .api_client import APIClient

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

            /* Inputs */
            QComboBox, QLineEdit, QDateEdit, QTextEdit {
                padding: 10px;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                font-size: 14px;
                background-color: #FFFFFF;
                color: #1F2937;
            }
            QComboBox:focus, QLineEdit:focus, QDateEdit:focus, QTextEdit:focus {
                border: 1px solid #1D4ED8;
            }
    """)

class ApplicationController:
    def __init__(self):
        self.api_client = APIClient()
        self.login_view = None
        self.main_window = None

    def start(self):
        self.show_login()

    def show_login(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        # Reset API client token
        self.api_client.clear_token()

        self.login_view = LoginView(self.api_client)
        self.login_view.login_success.connect(self.on_login_success)
        self.login_view.show()

    def on_login_success(self, user_info):
        if self.login_view:
            self.login_view.close()
            self.login_view = None

        self.show_main_window(user_info)

    def show_main_window(self, user_info):
        self.main_window = MainWindow(self.api_client)

        # Set User Info in Sidebar
        account_name = user_info.get("account_name") or user_info.get("username")
        # For last_access, the backend updates it on login.
        # But the returned user_info might not have the *current* login time yet
        # (since the token was just created).
        # Actually, the /login endpoint updates last_login.
        # We can just display "Adesso" or fetch user info again.
        # For now, I'll just put "Oggi" or leave it as stored.
        # Wait, the requirement says "sotto quando è stato fatto l'ultimo accesso".
        # If I just logged in, my last access is now.
        import datetime
        now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        self.main_window.sidebar.set_user_info(account_name, now_str)

        self.main_window.logout_requested.connect(self.show_login)
        self.main_window.showMaximized()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    setup_styles(app)

    controller = ApplicationController()
    controller.start()

    sys.exit(app.exec())
