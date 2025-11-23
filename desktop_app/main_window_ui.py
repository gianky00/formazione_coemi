import os
import sys
from datetime import date, datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QPushButton, QStackedWidget, QLabel, QFrame, QSizePolicy,
                             QScrollArea, QLayout, QApplication)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, pyqtSignal, QPoint, pyqtProperty, QRect
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen

# Import views
from .views.import_view import ImportView
from .views.dashboard_view import DashboardView
from .views.validation_view import ValidationView
from .views.scadenzario_view import ScadenzarioView
from .views.config_view import ConfigView
from .views.modern_guide_view import ModernGuideDialog

# Import Utils
from .utils import get_asset_path, load_colored_icon

class SidebarButton(QPushButton):
    def __init__(self, text, icon_name, parent=None):
        super().__init__(text, parent)
        self.icon_name = icon_name
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("nav_btn", "true") # Keep for reference, though we paint manually

        # Colors
        self._bg_color = QColor(0, 0, 0, 0) # Transparent
        self.default_bg = QColor(0, 0, 0, 0)
        self.hover_bg = QColor(255, 255, 255, 25) # White with low opacity
        self.checked_bg = QColor(29, 78, 216) # Blue-700

        # Animation
        self._anim = QPropertyAnimation(self, b"backgroundColor", self)
        self._anim.setDuration(150)

    @pyqtProperty(QColor)
    def backgroundColor(self):
        return self._bg_color

    @backgroundColor.setter
    def backgroundColor(self, color):
        self._bg_color = color
        self.update()

    def enterEvent(self, event):
        if not self.isChecked():
            self._anim.stop()
            self._anim.setEndValue(self.hover_bg)
            self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.isChecked():
            self._anim.stop()
            self._anim.setEndValue(self.default_bg)
            self._anim.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Determine Background Color
        bg = self._bg_color
        if self.isChecked():
            bg = self.checked_bg

        # Draw Background
        painter.setBrush(QBrush(bg))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)

        # Draw Left Border if Checked
        if self.isChecked():
            painter.setBrush(QBrush(QColor("#60A5FA"))) # Blue-400 Accent
            painter.drawRoundedRect(0, 8, 4, self.height() - 16, 2, 2)

        # Draw Icon
        icon = self.icon()
        if not icon.isNull():
            icon_size = self.iconSize()
            # Center vertically, left margin depends on centered property?
            # Sidebar handles text hiding. If text is empty, center icon.

            if not self.text():
                # Centered
                x = (self.width() - icon_size.width()) // 2
                y = (self.height() - icon_size.height()) // 2
                icon.paint(painter, x, y, icon_size.width(), icon_size.height())
            else:
                # Left Aligned
                x = 16
                y = (self.height() - icon_size.height()) // 2
                icon.paint(painter, x, y, icon_size.width(), icon_size.height())

                # Draw Text
                painter.setPen(QColor("#FFFFFF"))
                font = self.font()
                font.setBold(self.isChecked())
                painter.setFont(font)

                text_rect = self.rect()
                text_rect.setLeft(x + icon_size.width() + 12)
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.text())

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

        self.user_name_label = QLabel("Benvenuto, Utente!")
        self.user_name_label.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 18px;")
        self.user_name_label.setWordWrap(True)
        self.user_info_layout.addWidget(self.user_name_label)

        self.last_access_label = QLabel("Ultimo accesso: -")
        self.last_access_label.setStyleSheet("color: #93C5FD; font-size: 13px;")
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

        # --- License Info ---
        self.license_frame = QFrame()
        self.license_layout = QVBoxLayout(self.license_frame)
        self.license_layout.setContentsMargins(12, 5, 12, 10)
        self.license_layout.setSpacing(4)

        license_data = self.read_license_info()

        if not license_data:
             lbl = QLabel("import dettagli_licenza")
             lbl.setStyleSheet("color: #FF6B6B; font-size: 14px; font-weight: bold;")
             self.license_layout.addWidget(lbl)
        else:
             # Hardware ID
             if "Hardware ID" in license_data:
                  l1 = QLabel(f"Hardware ID:\n{license_data['Hardware ID']}")
                  l1.setStyleSheet("color: #93C5FD; font-size: 12px;")
                  self.license_layout.addWidget(l1)

             # Scadenza
             expiry_str = license_data.get("Scadenza Licenza", "")
             if expiry_str:
                  l2 = QLabel(f"Scadenza Licenza:\n{expiry_str}")
                  l2.setStyleSheet("color: #93C5FD; font-size: 12px;")
                  self.license_layout.addWidget(l2)

                  try:
                      if '/' in expiry_str:
                          d, m, y = map(int, expiry_str.split('/'))
                          expiry_date = date(y, m, d)
                      elif '-' in expiry_str:
                          y, m, d = map(int, expiry_str.split('-'))
                          expiry_date = date(y, m, d)
                      else:
                          raise ValueError

                      days_left = (expiry_date - date.today()).days
                      if days_left >= 0:
                          l3 = QLabel(f"La licenza termina tra {days_left} giorni.")
                      else:
                          l3 = QLabel(f"Licenza SCADUTA da {abs(days_left)} giorni.")

                      l3.setStyleSheet("color: #FFFFFF; font-size: 13px;")
                      self.license_layout.addWidget(l3)
                  except:
                      pass

             # Generato il
             if "Generato il" in license_data:
                  l4 = QLabel(f"Generato il: {license_data['Generato il']}")
                  l4.setStyleSheet("color: #60A5FA; font-size: 11px;")
                  self.license_layout.addWidget(l4)

        self.main_layout.addWidget(self.license_frame)

        # --- Footer ---
        self.disconnect_btn = QPushButton("Disconnetti")
        self.disconnect_btn.setObjectName("disconnect_btn")
        self.disconnect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.disconnect_btn.setIcon(load_colored_icon("log-out.svg", "#FFFFFF"))
        self.disconnect_btn.setStyleSheet("color: white; text-align: left; padding: 10px; background: none; border: none; font-weight: bold; font-size: 15px;")
        self.disconnect_btn.clicked.connect(self.logout_requested.emit)
        self.main_layout.addWidget(self.disconnect_btn)

        self.footer_label = QLabel("v1.0.0 • Intelleo")
        self.footer_label.setObjectName("version_label")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_label.setStyleSheet("font-size: 12px;")
        self.main_layout.addWidget(self.footer_label)

        # Animation State
        self.is_collapsed = False
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.setDuration(300)

    def read_license_info(self):
        path = "dettagli_licenza.txt"

        # Define fallback paths
        possible_paths = [
            path,
            os.path.join("Licenza", path),
        ]

        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            possible_paths.append(os.path.join(exe_dir, path))
            possible_paths.append(os.path.join(exe_dir, "Licenza", path))

        info = {}
        for p in possible_paths:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        for line in f:
                            if ":" in line:
                                key, value = line.split(":", 1)
                                info[key.strip()] = value.strip()
                    if info: break
                except: pass
        return info

    def set_user_info(self, name, last_access):
        self.user_name_label.setText(f"Benvenuto, {name}!")
        self.last_access_label.setText(f"Ultimo accesso:\n{last_access}")

    def add_button(self, key, text, icon_name):
        # Use SidebarButton
        btn = SidebarButton(text, icon_name)
        btn.setProperty("full_text", text) # Store full text
        btn.setIcon(load_colored_icon(icon_name, "#FFFFFF"))
        btn.setIconSize(QSize(20, 20))

        # Ensure styling matches (padding etc set in paintEvent or logic)
        btn.setFixedHeight(45)

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
            self.hide_button_texts()

        def on_finished():
            self.setFixedWidth(end_width)
            if end_width == 260:
                # Expanded
                self.toggle_btn.setIcon(load_colored_icon("chevron-left.svg", "#1E3A8A"))
                self.logo_label.show()
                self.footer_label.show()
                self.user_info_frame.show()
                self.restore_button_texts()

        try: self.animation.finished.disconnect()
        except: pass
        self.animation.finished.connect(on_finished)

        self.animation.start()
        self.is_collapsed = not self.is_collapsed

    def hide_button_texts(self):
        for btn in self.buttons.values():
            btn.setText("")
            btn.setToolTip(btn.property("full_text"))

    def restore_button_texts(self):
        for btn in self.buttons.values():
            btn.setText(btn.property("full_text"))
            btn.setToolTip("")

class MainDashboardWidget(QWidget):
    logout_requested = pyqtSignal()

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client

        # Main Layout
        self.main_layout = QHBoxLayout(self)
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
        self.views["import"] = ImportView()
        self.views["import"].api_client = self.api_client

        self.views["validation"] = ValidationView()
        self.views["validation"].api_client = self.api_client

        self.views["dashboard"] = DashboardView()
        if hasattr(self.views["dashboard"], 'view_model'):
             self.views["dashboard"].view_model.api_client = self.api_client

        self.views["scadenzario"] = ScadenzarioView()
        self.views["scadenzario"].api_client = self.api_client

        self.views["config"] = ConfigView()
        self.views["config"].api_client = self.api_client

        for key in ["import", "validation", "dashboard", "scadenzario", "config"]:
            self.stacked_widget.addWidget(self.views[key])

    def _connect_signals(self):
        self.sidebar.buttons["import"].clicked.connect(lambda: self.switch_to("import"))
        self.sidebar.buttons["validation"].clicked.connect(lambda: self.switch_to("validation"))
        self.sidebar.buttons["dashboard"].clicked.connect(lambda: self.switch_to("dashboard"))
        self.sidebar.buttons["scadenzario"].clicked.connect(lambda: self.switch_to("scadenzario"))
        self.sidebar.buttons["config"].clicked.connect(lambda: self.switch_to("config"))
        self.sidebar.buttons["help"].clicked.connect(self.show_help)

        self.views["import"].import_completed.connect(self.views["validation"].refresh_data)
        self.views["validation"].validation_completed.connect(self.views["dashboard"].load_data)
        self.views["validation"].validation_completed.connect(self.views["scadenzario"].refresh_data)
        self.views["dashboard"].database_changed.connect(self.views["scadenzario"].refresh_data)

    def switch_to(self, key):
        if key not in self.views: return

        for k, btn in self.sidebar.buttons.items():
            if k in self.sidebar.buttons and k != "help":
                btn.setChecked(k == key)
                btn.update() # Force repaint for SidebarButton

        if key in self.sidebar.buttons:
             self.page_title.setText(self.sidebar.buttons[key].property("full_text"))

        self.stacked_widget.setCurrentWidget(self.views[key])

    def show_help(self):
        dialog = ModernGuideDialog(self)
        dialog.show() # Use show() instead of exec() for animation?
        # Dialogs usually need exec() to be modal.
        # But if we want animation, we can use exec() and animate inside.
        # ModernGuideDialog.exec() calls show() internally.
        dialog.exec()

    def analyze_folder(self, folder_path):
        self.switch_to("import")
        self.views["import"].upload_folder(folder_path)
