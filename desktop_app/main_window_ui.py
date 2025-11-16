
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QLabel, QFrame, QMessageBox, QMenu, QProgressBar, QGraphicsOpacityEffect
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize, QDate, QPropertyAnimation, QEasingCurve

from desktop_app.views.import_view import ImportView
from desktop_app.views.dashboard_view import DashboardView
from desktop_app.views.config_view import ConfigView
from desktop_app.views.validation_view import ValidationView
from desktop_app.views.scadenzario_view import ScadenzarioView
from desktop_app.views.contact_dialog import ContactDialog
from desktop_app.views.guide_dialog import GuideDialog

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.logo_label = QLabel()
        self.logo_label.setObjectName("logo")
        self.logo_pixmap = QPixmap("desktop_app/assets/logo.png")
        self.logo_label.setPixmap(self.logo_pixmap.scaled(240, 66, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.logo_label)

        self.nav_buttons = QVBoxLayout()
        self.nav_buttons.setSpacing(5)

        self.buttons = {}
        self.add_nav_button("Analizza", "desktop_app/icons/analizza.svg")
        self.add_nav_button("Convalida Dati", "desktop_app/icons/convalida.svg")
        self.add_nav_button("Database", "desktop_app/icons/database.svg")
        self.add_nav_button("Scadenzario", "desktop_app/icons/scadenzario.svg")
        self.add_nav_button("Addestra", "desktop_app/icons/addestra.svg")

        self.layout.addLayout(self.nav_buttons)
        self.layout.addStretch()

        self.help_button = self.add_nav_button("Supporto", "desktop_app/icons/help.svg", bottom=True)

    def add_nav_button(self, text, icon_path, bottom=False):
        button = QPushButton(f"")
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(28, 28))
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
        self.setWindowTitle("Intelleo")
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
        self.content_layout.setContentsMargins(32, 32, 32, 32)
        self.content_layout.setSpacing(24)
        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)
        self.main_layout.addWidget(self.content_area, 1)

        # Status Bar
        self.status_bar = QFrame()
        self.status_bar.setFixedHeight(30)
        self.status_bar_layout = QHBoxLayout(self.status_bar)
        self.status_bar_layout.setContentsMargins(10, 0, 10, 0)

        self.progress_label = QLabel("Pronto.")
        self.status_bar_layout.addWidget(self.progress_label)
        self.status_bar_layout.addStretch()

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setTextVisible(False)

        self.progress_widget = QWidget()
        progress_layout = QHBoxLayout(self.progress_widget)
        progress_layout.setContentsMargins(0,0,0,0)
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        self.status_bar_layout.addWidget(self.progress_widget)
        self.progress_widget.setVisible(False)

        self.content_layout.addWidget(self.status_bar)

        self.import_view = ImportView(
            progress_widget=self.progress_widget,
            progress_bar=self.progress_bar,
            progress_label=self.progress_label
        )
        self.dashboard_view = DashboardView()
        self.config_view = ConfigView()
        self.validation_view = ValidationView()
        self.scadenzario_view = ScadenzarioView()

        self.stacked_widget.addWidget(self.import_view)
        self.stacked_widget.addWidget(self.validation_view)
        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.scadenzario_view)
        self.stacked_widget.addWidget(self.config_view)

        self.current_fade_animation = None

        self.sidebar.buttons["Analizza"].clicked.connect(lambda: self.fade_in_widget(self.import_view))
        self.sidebar.buttons["Convalida Dati"].clicked.connect(lambda: self.fade_in_widget(self.validation_view))
        self.sidebar.buttons["Database"].clicked.connect(lambda: self.fade_in_widget(self.dashboard_view))
        self.sidebar.buttons["Scadenzario"].clicked.connect(self.show_scadenzario)
        self.sidebar.buttons["Addestra"].clicked.connect(lambda: self.fade_in_widget(self.config_view))

        help_menu = QMenu(self)
        legal_action = help_menu.addAction("Avviso Legale")
        legal_action.triggered.connect(self.show_legal_notice)
        contact_action = help_menu.addAction("Contatti")
        contact_action.triggered.connect(self.show_contact_form)
        guide_action = help_menu.addAction("Guida")
        guide_action.triggered.connect(self.show_guide)
        self.sidebar.help_button.setMenu(help_menu)


        self.sidebar.buttons["Analizza"].setChecked(True)
        self.fade_in_widget(self.import_view, immediate=True)

    def show_scadenzario(self):
        self.scadenzario_view.refresh_data()
        self.fade_in_widget(self.scadenzario_view)

    def fade_in_widget(self, widget, immediate=False):
        if self.current_fade_animation:
            self.current_fade_animation.stop()

        if immediate:
            self.stacked_widget.setCurrentWidget(widget)
            return

        opacity_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacity_effect)

        self.current_fade_animation = QPropertyAnimation(opacity_effect, b"opacity")
        self.current_fade_animation.setDuration(300)
        self.current_fade_animation.setStartValue(0.0)
        self.current_fade_animation.setEndValue(1.0)
        self.current_fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.current_fade_animation.finished.connect(lambda: widget.setGraphicsEffect(None))

        self.stacked_widget.setCurrentWidget(widget)
        self.current_fade_animation.start()

    def show_contact_form(self):
        dialog = ContactDialog(self)
        dialog.exec()

    def show_guide(self):
        dialog = GuideDialog(self)
        dialog.exec()

    def show_legal_notice(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Avviso Legale")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        current_year = QDate.currentDate().year()
        msg_box.setText(f"""
            <b>AVVISO LEGALE SU PROPRIETÀ INTELLETTUALE E SEGRETO INDUSTRIALE</b><br><br>
            Questo software, inclusi la sua architettura, logica di funzionamento e interfaccia utente, costituisce Segreto Industriale (Know-How) e informazione confidenziale, protetto ai sensi del <b>Codice della Proprietà Industriale (D.Lgs. 30/2005)</b> e della normativa sui segreti commerciali <b>(Art. 98-99 CPI; Art. 623 Codice Penale)</b>.
            <br><br>
            Inoltre, il software è un'opera dell'ingegno di carattere creativo, protetta dalla <b>Legge sul Diritto d'Autore (L. 633/1941)</b>.
            <br><br>
            <b>È fatto assoluto divieto di:</b>
            <ul>
                <li>Copiare, duplicare o riprodurre il software in qualsiasi forma.</li>
                <li>Decompilare, disassemblare o effettuare reverse engineering.</li>
                <li>Modificare, adattare o creare opere derivate.</li>
                <li>Distribuire, noleggiare, vendere o cedere in licenza a terzi.</li>
                <li>Utilizzare il software per scopi illeciti o non autorizzati.</li>
            </ul>
            La violazione di tali disposizioni costituisce un illecito che comporta <b>sanzioni civili</b> (risarcimento del danno) e <b>penali</b> (reclusione e multa, ai sensi degli art. 171 e seguenti della Legge sul Diritto d'Autore e dell'art. 623 del Codice Penale).
            <br><br>
            Copyright © {current_year}. Tutti i diritti riservati.
        """)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #F9FAFB;
            }
            QLabel {
                font-size: 14px;
                color: #4B5563;
            }
        """)
        msg_box.setMinimumSize(700, 450)
        msg_box.exec()

    def take_screenshot_and_exit(self):
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.winId())
        screenshot.save(self.screenshot_path, 'png')
        QApplication.quit()
