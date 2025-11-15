
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from desktop_app.main_window_ui import MainWindow

def main():
    app = QApplication(sys.argv)

    # Set a modern font
    font = QFont("Segoe UI")
    app.setFont(font)

    # Global stylesheet for a modern look
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #F7F8FC;
        }

        /* Sidebar Styles */
        Sidebar > QVBoxLayout {
            background-color: #FFFFFF;
            border-right: 1px solid #E0E0E0;
        }
        Sidebar QLabel {
            padding-top: 10px;
            padding-bottom: 10px;
        }
        Sidebar QPushButton {
            text-align: left;
            padding: 12px;
            border: none;
            font-size: 14px;
            color: #555;
            border-radius: 5px;
            margin: 5px;
        }
        Sidebar QPushButton:hover {
            background-color: #E8F0FE;
        }
        Sidebar QPushButton:checked {
            background-color: #D6E4FF;
            color: #0052CC;
            font-weight: bold;
        }

        /* Content Area Styles */
        QFrame {
            background-color: #FFFFFF;
            border: none;
        }

        /* Table Styles */
        QTableView {
            border: 1px solid #E0E0E0;
            gridline-color: #E0E0E0;
            selection-background-color: #D6E4FF;
            alternate-background-color: #F7F8FC;
            background-color: #FFFFFF;
        }
        QHeaderView::section {
            background-color: #F7F8FC;
            padding: 8px;
            border: none;
            border-bottom: 1px solid #E0E0E0;
            font-weight: bold;
        }

        /* Button Styles */
        QPushButton {
            padding: 8px 16px;
            border: 1px solid #0052CC;
            border-radius: 5px;
            background-color: #0052CC;
            color: white;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #0065FF;
        }
        QPushButton:disabled {
            background-color: #E0E0E0;
            border-color: #E0E0E0;
            color: #999;
        }

        /* ComboBox and LineEdit Styles */
        QComboBox, QLineEdit, QDateEdit {
            padding: 8px;
            border: 1px solid #E0E0E0;
            border-radius: 5px;
            font-size: 14px;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox::down-arrow {
            image: url(desktop_app/icons/down-arrow.svg); /* You'll need an icon for this */
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
    main_win.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
