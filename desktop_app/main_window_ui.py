
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QLabel, QFrame, QMessageBox
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize, QDate

from desktop_app.views.import_view import ImportView
from desktop_app.views.dashboard_view import DashboardView
from desktop_app.views.config_view import ConfigView
from desktop_app.views.validation_view import ValidationView

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.logo_label = QLabel()
        self.logo_pixmap = QPixmap("desktop_app/icons/logo.svg")
        self.logo_label.setPixmap(self.logo_pixmap.scaled(160, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.logo_label)

        self.nav_buttons = QVBoxLayout()
        self.nav_buttons.setSpacing(5)

        self.buttons = {}
        self.add_nav_button("Analizza", "desktop_app/icons/analizza.svg")
        self.add_nav_button("Convalida Dati", "desktop_app/icons/convalida.svg")
        self.add_nav_button("Database", "desktop_app/icons/database.svg")
        self.add_nav_button("Addestra", "desktop_app/icons/addestra.svg")

        self.layout.addLayout(self.nav_buttons)
        self.layout.addStretch()

        self.help_button = self.add_nav_button("Supporto", "desktop_app/icons/help.svg", bottom=True)

    def add_nav_button(self, text, icon_path, bottom=False):
        button = QPushButton(f"  {text}")
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(24, 24))
        button.setCheckable(True)
        button.setAutoExclusive(True)
        if bottom:
            self.layout.addWidget(button)
        else:
            self.nav_buttons.addWidget(button)
        self.buttons[text] = button
        return button

class MainWindow(QMainWindow):
    def __init__(self, screenshot_path=None):
        super().__init__()
        self.setWindowTitle("CertiSync AI")
        self.setGeometry(100, 100, 1200, 800)
        self.screenshot_path = screenshot_path

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.main_layout.addWidget(self.sidebar)

        self.content_area = QFrame()
        self.content_layout = QVBoxLayout(self.content_area)
        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)
        self.main_layout.addWidget(self.content_area, 1)

        self.import_view = ImportView()
        self.dashboard_view = DashboardView()
        self.config_view = ConfigView()
        self.validation_view = ValidationView()

        self.stacked_widget.addWidget(self.import_view)
        self.stacked_widget.addWidget(self.validation_view)
        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.config_view)

        self.sidebar.buttons["Analizza"].clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.import_view))
        self.sidebar.buttons["Convalida Dati"].clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.validation_view))
        self.sidebar.buttons["Database"].clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.dashboard_view))
        self.sidebar.buttons["Addestra"].clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.config_view))
        self.sidebar.help_button.clicked.connect(self.show_legal_notice)

        self.sidebar.buttons["Analizza"].setChecked(True)

    def show_legal_notice(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Avviso Legale")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        current_year = QDate.currentDate().year()
        msg_box.setText(f"""
            <b>AVVISO LEGALE SU PROPRIETÀ INTELLETTUALE E SEGRETO INDUSTRIALE</b><br><br>
            Questo software, inclusi la sua architettura, logica di funzionamento e interfaccia utente, costituisce Segreto Industriale (Know-How) e informazione confidenziale.<br><br>
            Esso è protetto ai sensi della normativa vigente...
        """)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
            }
            QLabel {
                font-size: 14px;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 14px;
                background-color: #0052CC;
                color: white;
            }
        """)
        msg_box.exec()

    def take_screenshot_and_exit(self):
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.winId())
        screenshot.save(self.screenshot_path, 'png')
        QApplication.quit()
