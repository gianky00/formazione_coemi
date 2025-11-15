import sys
from PyQt6.QtWidgets import QApplication
from desktop_app.main_window_ui import MainWindow

def main():
    app = QApplication(sys.argv)

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
