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
