import logging
import sys
import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtGui import QFont, QShortcut, QKeySequence

from app import __version__ as app_version
from app.core.path_resolver import get_asset_path

try:
    from desktop_app.services.notification_center import NotificationBell, NotificationPanel
except ImportError:
    NotificationBell = None
    NotificationPanel = None

from desktop_app.views.config_view import ConfigView
from desktop_app.views.database_view import DatabaseView
from desktop_app.views.dipendenti_view import DipendentiView
from desktop_app.views.import_view import ImportView
from desktop_app.views.lyra_view import LyraView
from desktop_app.views.scadenzario_view import ScadenzarioView
from desktop_app.views.validation_view import ValidationView

logger = logging.getLogger(__name__)


class DashboardView(QWidget):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        
        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        self.header = QFrame()
        self.header.setObjectName("HeaderFrame")
        self.header.setFixedHeight(70)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        # Logo/Title
        self.lbl_title = QLabel("Intelleo")
        self.lbl_title.setObjectName("HeaderTitle")
        header_layout.addWidget(self.lbl_title)
        
        header_layout.addStretch()

        # User Info
        user_info = self.controller.api_client.user_info or {}
        username = user_info.get("account_name") or user_info.get("username") or "Utente"
        
        self.lbl_user = QLabel(f"👤 {username}")
        self.lbl_user.setStyleSheet("color: white; font-size: 11pt;")
        header_layout.addWidget(self.lbl_user)

        # Notification Bell
        if NotificationBell and hasattr(self.controller, "notification_center"):
            self.notification_bell = NotificationBell(self.controller.notification_center, self._show_notification_panel)
            header_layout.addWidget(self.notification_bell)

        # Guide Button
        self.btn_guide = QPushButton("Guida")
        self.btn_guide.setObjectName("GuideButton")
        self.btn_guide.setProperty("class", "SuccessButton")
        self.btn_guide.setCursor(Qt.PointingHandCursor)
        self.btn_guide.clicked.connect(self.open_guide)
        header_layout.addWidget(self.btn_guide)

        # Logout Button
        self.btn_logout = QPushButton("Esci")
        self.btn_logout.setProperty("class", "DangerButton")
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.clicked.connect(self.controller.logout)
        header_layout.addWidget(self.btn_logout)

        main_layout.addWidget(self.header)

        # Read-Only Warning Banner
        if user_info.get("read_only"):
            self.warning_banner = QFrame()
            self.warning_banner.setObjectName("StatusBanner")
            self.warning_banner.setFixedHeight(35)
            banner_layout = QHBoxLayout(self.warning_banner)
            banner_layout.setContentsMargins(0, 0, 0, 0)
            
            lbl_warning = QLabel("⚠ MODALITÀ SOLA LETTURA - Il database è bloccato da un altro utente")
            lbl_warning.setObjectName("StatusLabel")
            lbl_warning.setAlignment(Qt.AlignCenter)
            banner_layout.addWidget(lbl_warning)
            main_layout.addWidget(self.warning_banner)

        # Tabs
        self.tabs = QTabWidget()
        
        # Instantiate Tabs
        self.tab_import = ImportView(self.controller)
        self.tab_validation = ValidationView(self.controller)
        self.tab_database = DatabaseView(self.controller)
        self.tab_scadenzario = ScadenzarioView(self.controller)
        self.tab_dipendenti = DipendentiView(self.controller)
        self.tab_lyra = LyraView(self.controller)
        self.tab_config = ConfigView(self.controller)

        # Add Tabs
        self.tabs.addTab(self.tab_import, "Importa")
        self.tabs.addTab(self.tab_validation, "Convalida")
        self.tabs.addTab(self.tab_database, "Database")
        self.tabs.addTab(self.tab_scadenzario, "Scadenzario")
        self.tabs.addTab(self.tab_dipendenti, "Dipendenti")
        self.tabs.addTab(self.tab_lyra, "Lyra IA")
        self.tabs.addTab(self.tab_config, "Configurazione")

        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 5)
        content_layout.addWidget(self.tabs)
        main_layout.addLayout(content_layout)

        # Footer
        self.footer = QFrame()
        self.footer.setFixedHeight(30)
        footer_layout = QHBoxLayout(self.footer)
        footer_layout.setContentsMargins(15, 0, 15, 0)
        
        lbl_version = QLabel(f"v{app_version}")
        lbl_version.setStyleSheet("color: #6B7280; font-size: 9pt;")
        footer_layout.addWidget(lbl_version)
        footer_layout.addStretch()
        
        main_layout.addWidget(self.footer)

    def setup_shortcuts(self):
        for i in range(7):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i+1}"), self)
            shortcut.activated.connect(lambda idx=i: self.tabs.setCurrentIndex(idx))
        QShortcut(QKeySequence("F1"), self).activated.connect(self.open_guide)
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.controller.logout)

    def on_tab_changed(self, index):
        tab_widget = self.tabs.widget(index)
        if hasattr(tab_widget, "refresh_data"):
            tab_widget.refresh_data()

    def _show_notification_panel(self):
        if NotificationPanel and hasattr(self.controller, "notification_center"):
            panel = NotificationPanel(self.notification_bell, self.controller.notification_center, self.controller)
            panel.show()

    def open_guide(self):
        candidates = ["guide/index.html", "guide_frontend/dist/index.html"]
        found_uri = None
        for rel_path in candidates:
            try:
                path = get_asset_path(rel_path)
                if path.exists():
                    found_uri = path.absolute().as_uri()
                    break
            except Exception: continue

        if found_uri: webbrowser.open(found_uri)
        else:
            if not getattr(sys, "frozen", False): webbrowser.open("http://localhost:5173")
            else: QMessageBox.information(self, "Guida", "La guida interattiva non è disponibile.")
