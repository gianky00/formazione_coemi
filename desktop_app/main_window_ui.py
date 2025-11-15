import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QMenuBar
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QTimer
from desktop_app.views.import_view import ImportView
from desktop_app.views.dashboard_view import DashboardView
from desktop_app.views.config_view import ConfigView
from desktop_app.views.validation_view import ValidationView

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
        self.validation_view = ValidationView()

        # Add views to stacked widget
        self.stacked_widget.addWidget(self.import_view)
        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.config_view)
        self.stacked_widget.addWidget(self.validation_view)

        self.stacked_widget.currentChanged.connect(self.on_view_change)

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

        validation_action = QAction("Convalida Dati", self)
        validation_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.validation_view))
        view_menu.addAction(validation_action)

        config_action = QAction("Configurazione", self)
        config_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.config_view))
        view_menu.addAction(config_action)

    def on_view_change(self, index):
        widget = self.stacked_widget.widget(index)
        if hasattr(widget, 'load_data'):
            widget.load_data()

    def take_screenshot_and_exit(self):
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.winId())
        screenshot.save(self.screenshot_path, 'png')
        QApplication.quit()


