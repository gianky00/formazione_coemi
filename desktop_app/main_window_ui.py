from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QStackedWidget, QPushButton, QLabel,
                             QFrame, QMessageBox, QMenu, QProgressBar,
                             QGraphicsOpacityEffect)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QSize, QDate, QPropertyAnimation, QEasingCurve
from PyQt6.QtSvg import QSvgRenderer
from desktop_app.views.import_view import ImportView
from desktop_app.views.dashboard_view import DashboardView
from desktop_app.views.config_view import ConfigView
from desktop_app.views.validation_view import ValidationView
from desktop_app.views.scadenzario_view import ScadenzarioView
from desktop_app.views.contact_dialog import ContactDialog
from desktop_app.views.guide_dialog import GuideDialog

def create_colored_icon(icon_path: str, color: QColor) -> QIcon:
    renderer = QSvgRenderer(icon_path)
    pixmap = QPixmap(renderer.defaultSize())
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), color)
    painter.end()
    return QIcon(pixmap)

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
        self.update_button_icons()

    def update_button_icons(self):
        for button in self.buttons.values():
            icon_path = button.property("icon_path")
            color = QColor("black") if button.isChecked() else QColor("white")
            button.setIcon(create_colored_icon(icon_path, color))

    def add_nav_button(self, text, icon_path, bottom=False):
        button = QPushButton()
        button.setProperty("icon_path", icon_path)
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
        self._init_status_bar()
        self._init_views()
        self._init_connections()
        self.sidebar.buttons["Analizza"].setChecked(True)
        self.fade_in_widget(self.views["Analizza"], immediate=True)

    def _init_status_bar(self):
        self.status_bar = QFrame()
        self.status_bar.setFixedHeight(30)
        status_bar_layout = QHBoxLayout(self.status_bar)
        status_bar_layout.setContentsMargins(10, 0, 10, 0)
        self.progress_label = QLabel("Pronto.")
        status_bar_layout.addWidget(self.progress_label)
        status_bar_layout.addStretch()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setTextVisible(False)
        self.progress_widget = QWidget()
        progress_layout = QHBoxLayout(self.progress_widget)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        status_bar_layout.addWidget(self.progress_widget)
        self.progress_widget.setVisible(False)
        self.content_layout.addWidget(self.status_bar)

    def _init_views(self):
        self.views = {
            "Analizza": ImportView(
                progress_widget=self.progress_widget,
                progress_bar=self.progress_bar,
                progress_label=self.progress_label
            ),
            "Convalida Dati": ValidationView(),
            "Database": DashboardView(),
            "Scadenzario": ScadenzarioView(),
            "Addestra": ConfigView(),
        }
        for view in self.views.values():
            self.stacked_widget.addWidget(view)

    def _init_connections(self):
        self.views["Analizza"].import_completed.connect(self.views["Convalida Dati"].refresh_data)
        self.views["Convalida Dati"].validation_completed.connect(self.views["Database"].load_data)
        for name, button in self.sidebar.buttons.items():
            if name in self.views:
                button.clicked.connect(lambda checked, view=self.views[name]: self.handle_nav_click(view))
        self.sidebar.buttons["Scadenzario"].clicked.connect(self.show_scadenzario)
        help_menu = QMenu(self)
        help_menu.addAction("Avviso Legale", self.show_legal_notice)
        help_menu.addAction("Contatti", self.show_contact_form)
        help_menu.addAction("Guida", self.show_guide)
        self.sidebar.help_button.setMenu(help_menu)

    def show_scadenzario(self):
        self.sidebar.update_button_icons()
        self.views["Scadenzario"].refresh_data()
        self.fade_in_widget(self.views["Scadenzario"])

    def handle_nav_click(self, widget):
        self.sidebar.update_button_icons()
        self.fade_in_widget(widget)

    def fade_in_widget(self, widget, immediate=False):
        if hasattr(self, 'current_fade_animation') and self.current_fade_animation:
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
        ContactDialog(self).exec()

    def show_guide(self):
        GuideDialog(self).exec()

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
