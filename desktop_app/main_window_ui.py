import sys
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QMenuBar, QProgressBar, QMessageBox, QLabel, QHBoxLayout
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QTimer, QDate, Qt
from desktop_app.views.import_view import ImportView
from desktop_app.views.dashboard_view import DashboardView
from desktop_app.views.config_view import ConfigView
from desktop_app.views.validation_view import ValidationView

class MainWindow(QMainWindow):
    def __init__(self, screenshot_path=None):
        super().__init__()
        self.setWindowTitle("CertiSync AI")
        self.setGeometry(100, 100, 1200, 800)
        self.screenshot_path = screenshot_path

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Progress Bar
        self.progress_layout = QHBoxLayout()
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar = QProgressBar(self)
        self.progress_layout.addWidget(self.progress_label)
        self.progress_layout.addWidget(self.progress_bar)
        self.progress_widget = QWidget()
        self.progress_widget.setLayout(self.progress_layout)
        self.progress_widget.setVisible(False)
        self.layout.addWidget(self.progress_widget)

        # Instantiate views
        self.import_view = ImportView(self.progress_widget, self.progress_bar, self.progress_label)
        self.dashboard_view = DashboardView()
        self.config_view = ConfigView()
        self.validation_view = ValidationView()

        # Add views to stacked widget
        self.stacked_widget.addWidget(self.import_view)
        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.config_view)
        self.stacked_widget.addWidget(self.validation_view)

        # Introduce a delay before loading data to prevent race condition
        time.sleep(6)

        self.menu_actions = {}
        self.create_menu()
        self.stacked_widget.currentChanged.connect(self.on_view_change)

        # Set initial style
        self.update_menu_styles(self.stacked_widget.currentIndex())

        if self.screenshot_path:
            QTimer.singleShot(1000, self.take_screenshot_and_exit)

    def create_menu(self):
        menu_bar = self.menuBar()

        # Analizza Menu
        self.menu_actions["Analizza"] = QAction("Analizza", self)
        self.menu_actions["Analizza"].triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.import_view))
        menu_bar.addAction(self.menu_actions["Analizza"])

        # Convalida Dati Menu
        self.menu_actions["Convalida Dati"] = QAction("Convalida Dati", self)
        self.menu_actions["Convalida Dati"].triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.validation_view))
        menu_bar.addAction(self.menu_actions["Convalida Dati"])

        # Database Menu
        self.menu_actions["Database"] = QAction("Database", self)
        self.menu_actions["Database"].triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.dashboard_view))
        menu_bar.addAction(self.menu_actions["Database"])

        # Addestra Menu
        self.menu_actions["Addestra"] = QAction("Addestra", self)
        self.menu_actions["Addestra"].triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.config_view))
        menu_bar.addAction(self.menu_actions["Addestra"])

        # Help Menu
        help_menu = menu_bar.addMenu("?")
        legal_action = QAction("Avviso Legale", self)
        legal_action.triggered.connect(self.show_legal_notice)
        help_menu.addAction(legal_action)

    def show_legal_notice(self):
        current_year = QDate.currentDate().year()
        legal_text = f"""
        <b>AVVISO LEGALE SU PROPRIETÀ INTELLETTUALE E SEGRETO INDUSTRIALE</b><br><br>
        Questo software, inclusi la sua architettura, logica di funzionamento e interfaccia utente, costituisce Segreto Industriale (Know-How) e informazione confidenziale.<br><br>
        Esso è protetto ai sensi della normativa vigente sulla concorrenza sleale e sulla protezione dei segreti commerciali (in Italia: Artt. 98 e 99 del Codice della Proprietà Industriale - D.Lgs. 10 febbraio 2005, n. 30, come modificato in attuazione della Direttiva UE 2016/943).<br>
        L'accesso e l'utilizzo di questo software sono strettamente limitati ai soli soggetti autorizzati dal legittimo titolare per scopi operativi interni.<br><br>
        <b>Sono severamente vietate, salvo espressa autorizzazione scritta:</b><br>
        <ul>
            <li>La duplicazione, riproduzione o distribuzione a terzi.</li>
            <li>La modifica, la traduzione o la creazione di opere derivate.</li>
            <li>Qualsiasi attività di decompilazione, disassemblaggio o reverse engineering volta a risalire al codice sorgente o alla logica interna.</li>
        </ul>
        L'acquisizione, l'utilizzo o la rivelazione illecita di questo software costituiscono un illecito civile e penale e saranno perseguiti a norma di legge.<br><br>
        Copyright © {current_year} - Tutti i diritti riservati.
        """
        QMessageBox.information(self, "Avviso Legale", legal_text)

    def on_view_change(self, index):
        self.update_menu_styles(index)
        widget = self.stacked_widget.widget(index)
        if hasattr(widget, 'load_data'):
            widget.load_data()

    def update_menu_styles(self, current_index):
        current_widget = self.stacked_widget.widget(current_index)
        active_action = None

        for name, action in self.menu_actions.items():
            font = action.font()
            is_active = False
            if name == "Analizza" and current_widget == self.import_view:
                is_active = True
            elif name == "Convalida Dati" and current_widget == self.validation_view:
                is_active = True
            elif name == "Database" and current_widget == self.dashboard_view:
                is_active = True
            elif name == "Addestra" and current_widget == self.config_view:
                is_active = True

            font.setBold(is_active)
            action.setFont(font)
            if is_active:
                active_action = action

        stylesheet = """
            QMenuBar::item {
                padding: 5px 10px;
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: #3e3e3e;
                color: white;
            }
            QMenuBar::item:pressed {
                background-color: #555555;
            }
        """

        if active_action:
            # A more reliable way to style the active item is to target it by text.
            # Using custom properties on QMenuBar::item is not universally supported.
            stylesheet += f"""
            QMenuBar::item:contains("{active_action.text()}") {{
                background-color: #0078d7;
                color: white;
                font-weight: bold;
            }}
            """

        self.menuBar().setStyleSheet(stylesheet)

    def take_screenshot_and_exit(self):
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.winId())
        screenshot.save(self.screenshot_path, 'png')
        QApplication.quit()
