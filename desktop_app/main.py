import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

# --- IMPORT FONDAMENTALE ---
# Rendiamo disponibile MainWindow per il launcher
# Il punto (.) indica che il file è nella stessa cartella
from .main_window_ui import MainWindow

def setup_styles(app: QApplication):
    """
    Configura il font e il foglio di stile (CSS) dell'applicazione.
    Viene chiamata dal launcher.py all'avvio.
    """
    # Set a modern font
    font = QFont("Inter")
    # Fallback se Inter non è installato
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
            .card {
                background-color: #FFFFFF;
                border-radius: 12px;
                padding: 24px;
                /* Box shadow is not directly supported in QSS, this is a simulated border */
                border: 1px solid #E5E7EB;
            }

            /* Sidebar Styles */
            Sidebar {
                background-color: #1E3A8A; /* Blue-900 */
                border-right: 1px solid #1E3A8A;
            }

            /* FIX: Ensure all children of Sidebar have transparent background
               to inherit the Blue-900 color, and White text */
            Sidebar QWidget {
                background-color: transparent;
                color: #FFFFFF;
            }

            /* Sidebar Header Frame (Specific override) */
            Sidebar QFrame#sidebar_header {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E5E7EB;
            }

            /* Sidebar Toggle Button */
            Sidebar QPushButton#toggle_btn {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 4px;
                margin: 0px;
                color: #FFFFFF;
            }
            Sidebar QPushButton#toggle_btn:hover {
                background-color: rgba(31, 41, 55, 0.1); /* Dark hover because on white bg */
            }

            /* Sidebar Navigation Buttons */
            Sidebar QPushButton[nav_btn="true"] {
                text-align: left;
                padding: 12px 16px;
                border: none;
                font-size: 15px;
                font-weight: 500;
                border-radius: 8px;
                margin: 4px 12px;
                color: #FFFFFF; /* Pure White for better contrast */
                background-color: transparent;
            }

            /* Centered state (collapsed) */
            Sidebar QPushButton[nav_btn="true"][centered="true"] {
                text-align: center;
                padding: 12px;
                margin: 4px 8px; /* Slightly tighter margins */
            }

            Sidebar QPushButton[nav_btn="true"]:hover {
                background-color: rgba(29, 78, 216, 0.4); /* Blue-700 with opacity */
            }

            Sidebar QPushButton[nav_btn="true"]:checked {
                background-color: #1D4ED8; /* Blue-700 (Accent) */
                color: #FFFFFF;
                font-weight: 600;
                border-left: 3px solid #60A5FA; /* Optional: Indicator line */
            }

            /* Sidebar Footer */
            Sidebar QLabel#version_label {
                color: #93C5FD; /* Blue-300 */
                font-size: 14px; /* Increased from 13px */
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
                color: #1F2937; /* Ensure text is dark in white table */
            }
            QTableView::item:selected {
                background-color: #EFF6FF; /* Light blue */
                color: #1E40AF; /* Darker blue */
            }
            QHeaderView {
                background-color: #F9FAFB;
            }
            QHeaderView::section {
                background-color: #F9FAFB;
                padding: 12px;
                border: none;
                border-bottom: 1px solid #E5E7EB;
                font-weight: 600; /* Semibold */
                font-size: 12px;
                text-transform: uppercase;
                color: #6B7280;
            }
            QTableView QScrollBar:vertical {
                border: none;
                background: #F1F5F9;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QTableView QScrollBar::handle:vertical {
                background: #D1D5DB;
                min-height: 20px;
                border-radius: 5px;
            }

            /* Pill/Badge Styles */
            QLabel[status="attivo"], QLabel[status="archiviato"] {
                background-color: #ECFDF5;
                color: #059669;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
            }
            QLabel[status="scaduto"] {
                background-color: #FEF2F2;
                color: #DC2626;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
            }
            QLabel[status="in_scadenza"] {
                background-color: #FFFBEB;
                color: #F59E0B;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
            }

            /* Checkbox Styles */
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #D1D5DB;
                border-radius: 6px;
                background-color: #FFFFFF;
            }
            QCheckBox::indicator:checked {
                background-color: #1D4ED8;
                border: 2px solid #1D4ED8;
                border-radius: 6px;
            }

            /* Button Styles */
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
                background-color: #1E40AF; /* Darker Blue */
            }
            QPushButton:disabled {
                background-color: #E5E7EB;
                border-color: #D1D5DB;
                color: #9CA3AF;
            }

            /* Secondary Button */
            QPushButton.secondary {
                background-color: #FFFFFF;
                color: #1F2937;
                border: 1px solid #D1D5DB;
            }
            QPushButton.secondary:hover {
                background-color: #F9FAFB;
            }

            /* Destructive Button */
            QPushButton.destructive {
                background-color: #DC2626;
                border-color: #DC2626;
            }
            QPushButton.destructive:hover {
                background-color: #B91C1C;
            }

            /* ComboBox, LineEdit, DateEdit Styles */
            QComboBox, QLineEdit, QDateEdit {
                padding: 10px;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                font-size: 14px;
                background-color: #FFFFFF;
                color: #1F2937;
            }
            QComboBox:focus, QLineEdit:focus, QDateEdit:focus {
                border: 1px solid #1D4ED8;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: none;
            }
    """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    setup_styles(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
