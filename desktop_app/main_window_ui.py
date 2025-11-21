import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QPushButton, QStackedWidget, QLabel, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap

# Import views
from .views.import_view import ImportView
from .views.dashboard_view import DashboardView
from .views.validation_view import ValidationView
from .views.scadenzario_view import ScadenzarioView
from .views.config_view import ConfigView
from .views.guide_dialog import GuideDialog

def get_asset_path(relative_path):
    """
    Resolve path to assets, handling both dev environment and frozen app.
    """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # In dev, we assume running from root, but let's be robust
        base_path = os.getcwd()

    return os.path.join(base_path, relative_path)

class Sidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setObjectName("sidebar")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)

        # Logo
        self.logo_label = QLabel()
        self.logo_label.setObjectName("logo")

        logo_path = get_asset_path("desktop_app/assets/logo.png")

        if os.path.exists(logo_path) and not QIcon(logo_path).isNull():
             pixmap = QPixmap(logo_path)
             # Scaled for sidebar
             self.logo_label.setPixmap(pixmap.scaled(220, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
             self.logo_label.setText("INTELLEO")
             self.logo_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold; padding: 20px;")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.logo_label)

        # Navigation Buttons
        self.buttons = {}
        self.add_button("import", "Analisi Documenti", "analizza.svg")
        self.add_button("validation", "Convalida Dati", "convalida.svg")
        self.add_button("dashboard", "Database Certificati", "database.svg")
        self.add_button("scadenzario", "Scadenzario", "scadenzario.svg")

        self.layout.addStretch()

        self.add_button("config", "Configurazione", "icon.ico")
        self.add_button("help", "Guida Utente", "help.svg")

    def add_button(self, key, text, icon_name):
        btn = QPushButton(text)
        btn.setCheckable(True)
        icon_path = get_asset_path(f"desktop_app/icons/{icon_name}")
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(24, 24))
        self.layout.addWidget(btn)
        self.buttons[key] = btn

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intelleo - Predict. Validate. Automate")
        self.resize(1280, 800)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.main_layout.addWidget(self.sidebar)

        # Content Area
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        # Top Bar (Title)
        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(60)
        self.top_bar.setStyleSheet("background-color: #FFFFFF; border-bottom: 1px solid #E5E7EB;")
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.page_title = QLabel("Dashboard")
        self.page_title.setStyleSheet("font-size: 20px; font-weight: 600; color: #1F2937; margin-left: 20px;")
        self.top_bar_layout.addWidget(self.page_title)

        self.content_layout.addWidget(self.top_bar)

        # Stacked Widget
        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)

        self.main_layout.addWidget(self.content_area)

        # Initialize Views
        self.views = {}
        self._init_views()
        self._connect_signals()

        # Default Page (can be overridden by analysis trigger)
        self.switch_to("dashboard")

    def _init_views(self):
        self.views["import"] = ImportView()
        self.views["validation"] = ValidationView()
        self.views["dashboard"] = DashboardView()
        self.views["scadenzario"] = ScadenzarioView()
        self.views["config"] = ConfigView()

        for key in ["import", "validation", "dashboard", "scadenzario", "config"]:
            self.stacked_widget.addWidget(self.views[key])

    def _connect_signals(self):
        self.sidebar.buttons["import"].clicked.connect(lambda: self.switch_to("import"))
        self.sidebar.buttons["validation"].clicked.connect(lambda: self.switch_to("validation"))
        self.sidebar.buttons["dashboard"].clicked.connect(lambda: self.switch_to("dashboard"))
        self.sidebar.buttons["scadenzario"].clicked.connect(lambda: self.switch_to("scadenzario"))
        self.sidebar.buttons["config"].clicked.connect(lambda: self.switch_to("config"))
        self.sidebar.buttons["help"].clicked.connect(self.show_help)

    def switch_to(self, key):
        if key not in self.views: return

        # Update Sidebar State
        for k, btn in self.sidebar.buttons.items():
            if k in self.sidebar.buttons and k != "help":
                btn.setChecked(k == key)

        # Update Title
        if key in self.sidebar.buttons:
             self.page_title.setText(self.sidebar.buttons[key].text())

        # Switch Page
        self.stacked_widget.setCurrentWidget(self.views[key])

    def show_help(self):
        dialog = GuideDialog(self)
        dialog.exec()

    def analyze_folder(self, folder_path):
        """
        Switch to Import view and trigger analysis for the given folder.
        """
        self.switch_to("import")
        # Pass the folder path to the view logic
        self.views["import"].upload_folder(folder_path)
