import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QPushButton, QStackedWidget, QLabel, QFrame, QSizePolicy,
                             QScrollArea, QLayout, QApplication)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap

# Import views
from .views.import_view import ImportView
from .views.dashboard_view import DashboardView
from .views.validation_view import ValidationView
from .views.scadenzario_view import ScadenzarioView
from .views.config_view import ConfigView
from .views.modern_guide_view import ModernGuideDialog

# Import Utils
from .utils import get_asset_path, load_colored_icon

class Sidebar(QFrame):
    logout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setObjectName("sidebar")

        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- Header (Toggle Left, Logo Right) ---
        self.header_frame = QFrame()
        self.header_frame.setObjectName("sidebar_header") # For White Background
        self.header_frame.setFixedHeight(64)
        self.header_layout = QHBoxLayout(self.header_frame)
        self.header_layout.setContentsMargins(12, 0, 12, 0)
        self.header_layout.setSpacing(10)

        # Toggle Button (Blue Icon for White Background)
        self.toggle_btn = QPushButton()
        self.toggle_btn.setObjectName("toggle_btn")
        self.toggle_btn.setFixedSize(32, 32)
        self.toggle_btn.setIcon(load_colored_icon("chevron-left.svg", "#1E3A8A"))
        self.toggle_btn.setIconSize(QSize(20, 20))
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        self.header_layout.addWidget(self.toggle_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # Logo (Image)
        self.logo_label = QLabel()
        self.logo_label.setObjectName("logo_label")

        logo_path = get_asset_path("desktop_app/assets/logo.png")
        if os.path.exists(logo_path) and not QIcon(logo_path).isNull():
             pixmap = QPixmap(logo_path)
             # Scaled for header - Larger as requested
             self.logo_label.setPixmap(pixmap.scaled(180, 55, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
             self.logo_label.setText("INTELLEO")
             self.logo_label.setStyleSheet("color: #1E3A8A; font-weight: bold; font-size: 18px;")

        self.header_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignRight)

        self.main_layout.addWidget(self.header_frame)

        # --- User Info Section ---
        self.user_info_frame = QFrame()
        self.user_info_frame.setStyleSheet("background-color: transparent; padding: 10px 12px;")
        self.user_info_layout = QVBoxLayout(self.user_info_frame)
        self.user_info_layout.setContentsMargins(0, 0, 0, 0)
        self.user_info_layout.setSpacing(4)

        self.user_name_label = QLabel("Ciao, Utente")
        self.user_name_label.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 14px;")
        self.user_info_layout.addWidget(self.user_name_label)

        self.last_access_label = QLabel("Ultimo accesso: -")
        self.last_access_label.setStyleSheet("color: #93C5FD; font-size: 11px;")
        self.user_info_layout.addWidget(self.last_access_label)

        self.main_layout.addWidget(self.user_info_frame)

        # --- Navigation Items ---
        self.nav_container = QWidget()
        self.nav_layout = QVBoxLayout(self.nav_container)
        self.nav_layout.setContentsMargins(0, 10, 0, 10)
        self.nav_layout.setSpacing(4)
        self.nav_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.buttons = {}
        # Nav Icons are White
        self.add_button("dashboard", "Dashboard", "layout-dashboard.svg")
        self.add_button("import", "Analisi Documenti", "file-text.svg")
        self.add_button("validation", "Convalida Dati", "database.svg")
        self.add_button("scadenzario", "Scadenzario", "calendar.svg")

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: rgba(59, 130, 246, 0.3); max-height: 1px; margin: 10px 12px;")
        self.nav_layout.addWidget(line)

        self.add_button("config", "Configurazione", "settings.svg")
        self.add_button("help", "Guida Utente", "book-open.svg")

        self.main_layout.addWidget(self.nav_container)

        # Spacer
        self.main_layout.addStretch()

        # --- Footer ---
        self.disconnect_btn = QPushButton("Disconnetti")
        self.disconnect_btn.setObjectName("disconnect_btn")
        self.disconnect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.disconnect_btn.setIcon(load_colored_icon("log-out.svg", "#FFFFFF"))
        self.disconnect_btn.setStyleSheet("color: white; text-align: left; padding: 10px; background: none; border: none; font-weight: bold;")
        self.disconnect_btn.clicked.connect(self.logout_requested.emit)
        self.main_layout.addWidget(self.disconnect_btn)

        self.footer_label = QLabel("v1.0.0 • Intelleo")
        self.footer_label.setObjectName("version_label")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.footer_label)

        # Animation State
        self.is_collapsed = False
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.setDuration(300)

    def set_user_info(self, name, last_access):
        self.user_name_label.setText(f"Ciao, {name}")
        self.last_access_label.setText(f"Ultimo accesso:\n{last_access}")

    def add_button(self, key, text, icon_name):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setProperty("nav_btn", "true") # For styling
        btn.setProperty("full_text", text) # Store full text

        # White Icon
        btn.setIcon(load_colored_icon(icon_name, "#FFFFFF"))
        btn.setIconSize(QSize(20, 20))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.nav_layout.addWidget(btn)
        self.buttons[key] = btn

    def toggle_sidebar(self):
        start_width = self.width()
        end_width = 260 if self.is_collapsed else 64

        self.animation.stop()
        self.animation.setStartValue(start_width)
        self.animation.setEndValue(end_width)

        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)

        if not self.is_collapsed:
            # Collapsing
            self.toggle_btn.setIcon(load_colored_icon("chevron-right.svg", "#1E3A8A"))
            self.logo_label.hide()
            self.footer_label.hide()
            self.user_info_frame.hide()
            self.update_buttons_layout(centered=True)
            self.hide_button_texts()

        def on_finished():
            self.setFixedWidth(end_width)
            if end_width == 260:
                # Expanded
                self.toggle_btn.setIcon(load_colored_icon("chevron-left.svg", "#1E3A8A"))
                self.logo_label.show()
                self.footer_label.show()
                self.user_info_frame.show()
                self.update_buttons_layout(centered=False)
                self.restore_button_texts()

        try: self.animation.finished.disconnect()
        except: pass
        self.animation.finished.connect(on_finished)

        self.animation.start()
        self.is_collapsed = not self.is_collapsed

    def update_buttons_layout(self, centered):
        for btn in self.buttons.values():
            btn.setProperty("centered", str(centered).lower())
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def hide_button_texts(self):
        for btn in self.buttons.values():
            btn.setText("")
            btn.setToolTip(btn.property("full_text"))

    def restore_button_texts(self):
        for btn in self.buttons.values():
            btn.setText(btn.property("full_text"))
            btn.setToolTip("")

class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
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
        self.sidebar.logout_requested.connect(self.logout_requested.emit)
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

        # Default Page
        self.switch_to("dashboard")

    def _init_views(self):
        # Pass api_client to views if they accept it
        # For now, views like ImportView instantiate their own APIClient.
        # To fix this properly, I need to update the views to accept APIClient.
        # But I cannot edit all files at once. I'll do it incrementally or monkey patch.
        # Better: I will patch the views' api_client attribute after instantiation.

        self.views["import"] = ImportView()
        self.views["import"].api_client = self.api_client # Inject authenticated client

        self.views["validation"] = ValidationView()
        self.views["validation"].api_client = self.api_client # Inject authenticated client

        self.views["dashboard"] = DashboardView()
        # DashboardView uses a ViewModel.
        if hasattr(self.views["dashboard"], 'view_model'):
             self.views["dashboard"].view_model.api_client = self.api_client

        self.views["scadenzario"] = ScadenzarioView()
        self.views["scadenzario"].api_client = self.api_client

        self.views["config"] = ConfigView()
        self.views["config"].api_client = self.api_client # Inject authenticated client

        for key in ["import", "validation", "dashboard", "scadenzario", "config"]:
            self.stacked_widget.addWidget(self.views[key])

    def _connect_signals(self):
        self.sidebar.buttons["import"].clicked.connect(lambda: self.switch_to("import"))
        self.sidebar.buttons["validation"].clicked.connect(lambda: self.switch_to("validation"))
        self.sidebar.buttons["dashboard"].clicked.connect(lambda: self.switch_to("dashboard"))
        self.sidebar.buttons["scadenzario"].clicked.connect(lambda: self.switch_to("scadenzario"))
        self.sidebar.buttons["config"].clicked.connect(lambda: self.switch_to("config"))
        self.sidebar.buttons["help"].clicked.connect(self.show_help)

        # Cross-view updates logic
        self.views["import"].import_completed.connect(self.views["validation"].refresh_data)
        self.views["validation"].validation_completed.connect(self.views["dashboard"].load_data)
        self.views["validation"].validation_completed.connect(self.views["scadenzario"].refresh_data)
        self.views["dashboard"].database_changed.connect(self.views["scadenzario"].refresh_data)

    def switch_to(self, key):
        if key not in self.views: return

        # Update Sidebar State
        for k, btn in self.sidebar.buttons.items():
            if k in self.sidebar.buttons and k != "help":
                btn.setChecked(k == key)

        # Update Title
        if key in self.sidebar.buttons:
             self.page_title.setText(self.sidebar.buttons[key].property("full_text"))

        # Switch Page
        self.stacked_widget.setCurrentWidget(self.views[key])

    def show_help(self):
        dialog = ModernGuideDialog(self)
        dialog.exec()

    def analyze_folder(self, folder_path):
        """
        Switch to Import view and trigger analysis for the given folder.
        """
        self.switch_to("import")
        self.views["import"].upload_folder(folder_path)
