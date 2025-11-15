
import sys
import time
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt
from desktop_app.main_window_ui import MainWindow

def main():
    app = QApplication(sys.argv)

    # Splash Screen
    splash_pix = QPixmap("desktop_app/assets/logo.png")
    splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
    splash.show()

    # Set a modern font
    font = QFont("Segoe UI")
    app.setFont(font)

    # Global stylesheet for a modern look
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #F7F8FC;
            color: #212121;
        }

        /* Sidebar Styles */
        Sidebar {
            background-color: #FFFFFF;
            border-right: 1px solid #E0E0E0;
        }
        Sidebar QLabel#logo {
            padding: 10px;
        }
        Sidebar QPushButton {
            text-align: left;
            padding: 12px;
            border: none;
            font-size: 14px;
            color: #000000;
            border-radius: 5px;
            margin: 5px 10px;
        }
        Sidebar QPushButton:hover {
            background-color: #E8F0FE;
            color: #0052CC;
        }
        Sidebar QPushButton:checked {
            background-color: #0052CC;
            color: white;
            font-weight: bold;
        }

        /* Table Styles */
        QTableView {
            border: none;
            gridline-color: #E0E0E0;
            selection-background-color: #0052CC;
            alternate-background-color: #F7F8FC;
        }
        QTableView::item:selected {
            color: white;
        }
        QHeaderView::section {
            background-color: #FFFFFF;
            padding: 10px;
            border: none;
            border-bottom: 2px solid #E0E0E0;
            font-weight: bold;
            font-size: 13px;
        }
        QTableView::item {
            padding: 5px;
            border-bottom: 1px solid #E0E0E0;
        }

        /* Checkbox Styles */
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        QCheckBox::indicator:unchecked {
            border: 2px solid #B0B0B0;
            border-radius: 4px;
        }
        QCheckBox::indicator:checked {
            background-color: #4A90E2;
            border: 2px solid #4A90E2;
            border-radius: 4px;
            image: url(desktop_app/icons/check.svg);
        }

        /* Button Styles */
        QPushButton {
            padding: 8px 16px;
            border: 1px solid #4A90E2;
            border-radius: 5px;
            background-color: #4A90E2;
            color: white;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #357ABD;
        }
        QPushButton:disabled {
            background-color: #D3D3D3;
            border-color: #C0C0C0;
            color: #A0A0A0;
        }

        /* ComboBox and LineEdit Styles */
        QComboBox, QLineEdit, QDateEdit {
            padding: 8px;
            border: 1px solid #E0E0E0;
            border-radius: 5px;
            font-size: 14px;
            background-color: #FDFDFD;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left-width: 1px;
            border-left-color: #E0E0E0;
            border-left-style: solid;
            border-top-right-radius: 5px;
            border-bottom-right-radius: 5px;
        }
        QComboBox::down-arrow {
            image: url(desktop_app/icons/down-arrow.svg);
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
    main_win.showMaximized()

    # Simulate loading time
    time.sleep(2)
    splash.finish(main_win)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
