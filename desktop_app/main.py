import sys
import time
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt, QTimer
from desktop_app.main_window_ui import MainWindow

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: white; border-radius: 10px;")

        layout = QVBoxLayout(self)
        self.logo_label = QLabel()
        pixmap = QPixmap("desktop_app/assets/logo.png").scaled(
            950, 228, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo_label)

        self.message_label = QLabel("Inizializzazione...")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("color: black; font-size: 16px;")
        layout.addWidget(self.message_label)

        self.setFixedSize(1000, 300)

        self.opacity = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fade_in)
        self.timer.start(10)

    def fade_in(self):
        if self.opacity >= 1.0:
            self.timer.stop()
        else:
            self.opacity += 0.01
            self.setWindowOpacity(self.opacity)

    def show_message(self, message):
        self.message_label.setText(message)
        QApplication.processEvents()


def main():
    app = QApplication(sys.argv)

    splash = SplashScreen()
    splash.show()

    splash.show_message("Inizializzazione del motore AI...")
    time.sleep(1)
    splash.show_message("Connessione al database...")
    time.sleep(1)
    splash.show_message("Avvio dell'interfaccia...")
    time.sleep(1)

    # Set a modern font
    font = QFont("Inter")
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
            background-color: #1E3A8A; /* Blue/Dark */
            border-right: 1px solid #E5E7EB;
        }
        Sidebar QLabel#logo {
            padding: 20px;
        }
        Sidebar QPushButton {
            text-align: left;
            padding: 15px 20px;
            border: none;
            font-size: 16px;
            border-radius: 10px;
            margin: 8px 12px;
            color: white; /* Ensure text is white */
        }
        /* Style for the hamburger button */
        Sidebar QPushButton#toggle_btn {
            margin: 8px 12px 20px 12px; /* Add some margin below */
        }
        Sidebar QPushButton:hover {
            background-color: rgba(29, 78, 216, 0.1);
        }
        Sidebar QPushButton:checked {
            background-color: #2563EB; /* Brighter Blue for Selection */
            font-weight: 600; /* Semibold */
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
        }
        QComboBox:focus, QLineEdit:focus, QDateEdit:focus {
            border: 1px solid #1D4ED8;
            /* Simulating focus ring with a border */
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 30px;
            border-left: none;
        }
    """)

    screenshot_path = None
    if "--screenshot" in sys.argv:
        try:
            screenshot_path = sys.argv[sys.argv.index("--screenshot") + 1]
        except IndexError:
            print("Usage: --screenshot <path>")
            sys.exit(1)


    main_win = MainWindow(screenshot_path=screenshot_path)
    main_win.setWindowIcon(QIcon("desktop_app/assets/logo.png"))

    # Simulate loading time then show main window and close splash
    time.sleep(2)
    main_win.showMaximized()
    splash.close()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
