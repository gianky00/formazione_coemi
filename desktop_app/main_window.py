import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QMenuBar
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QTimer
from desktop_app.import_view import ImportView
from desktop_app.dashboard_view import DashboardView
from desktop_app.config_view import ConfigView

class MainWindow(QMainWindow):
    def __init__(self, screenshot_path=None):
        super().__init__()
        self.setWindowTitle("Scadenziario IA")
        self.setGeometry(100, 100, 1200, 800)
        self.screenshot_path = screenshot_path

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Instantiate views
        self.import_view = ImportView()
        self.dashboard_view = DashboardView()
        self.config_view = ConfigView()

        # Add views to stacked widget
        self.stacked_widget.addWidget(self.import_view)
        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.config_view)

        self.create_menu()

        if self.screenshot_path:
            QTimer.singleShot(1000, self.take_screenshot_and_exit)

    def create_menu(self):
        menu_bar = self.menuBar()
        view_menu = menu_bar.addMenu("Viste")

        import_action = QAction("Importa", self)
        import_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.import_view))
        view_menu.addAction(import_action)

        dashboard_action = QAction("Dashboard", self)
        dashboard_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.dashboard_view))
        view_menu.addAction(dashboard_action)

        config_action = QAction("Configurazione", self)
        config_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.config_view))
        view_menu.addAction(config_action)

    def take_screenshot_and_exit(self):
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.winId())
        screenshot.save(self.screenshot_path, 'png')
        QApplication.quit()


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
    main_win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
