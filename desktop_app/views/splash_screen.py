from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QProgressBar, QFrame,
                             QGraphicsDropShadowEffect, QPushButton, QApplication, QHBoxLayout,
                             QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QSize, QEventLoop, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QPixmap
from desktop_app.utils import get_asset_path

class CustomSplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Container
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
            }
        """)

        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setXOffset(0)
        shadow.setYOffset(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.container.setGraphicsEffect(shadow)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(50, 60, 50, 40)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.container_layout.setSpacing(25)

        # Logo
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = get_asset_path("desktop_app/assets/logo.png")
        if logo_path:
            pixmap = QPixmap(logo_path)
            scaled = pixmap.scaled(QSize(400, 150), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled)
        else:
            self.logo_label.setText("INTELLEO")
            self.logo_label.setStyleSheet("font-size: 52px; font-weight: 700; color: #1E3A8A; font-family: 'Inter';")

        self.container_layout.addWidget(self.logo_label)
        self.container_layout.addSpacing(20)

        # Status Label (Main Step)
        self.status_label = QLabel("Inizializzazione Sistema...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #1F2937; font-size: 18px; font-weight: 600; font-family: 'Inter';")
        self.container_layout.addWidget(self.status_label)

        # Detail Label (Technical sub-steps)
        self.detail_label = QLabel("Caricamento configurazione...")
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_label.setStyleSheet("color: #6B7280; font-size: 13px; font-weight: 400; font-family: 'Consolas', 'Monospace';")
        self.container_layout.addWidget(self.detail_label)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #F3F4F6;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #2563EB, stop:1 #1E40AF);
                border-radius: 3px;
            }
        """)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.container_layout.addWidget(self.progress_bar)

        self.container_layout.addStretch()

        # Footer
        footer_layout = QHBoxLayout()
        self.copyright_label = QLabel("© 2025 Intelleo Security")
        self.copyright_label.setStyleSheet("color: #9CA3AF; font-size: 12px;")
        footer_layout.addWidget(self.copyright_label, alignment=Qt.AlignmentFlag.AlignLeft)

        footer_layout.addStretch()

        self.version_label = QLabel("v1.0.0")
        self.version_label.setStyleSheet("color: #9CA3AF; font-size: 12px; font-weight: 500;")
        footer_layout.addWidget(self.version_label, alignment=Qt.AlignmentFlag.AlignRight)

        self.container_layout.addLayout(footer_layout)

        # Exit Button (Error State)
        self.exit_btn = QPushButton("Chiudi Applicazione")
        self.exit_btn.setFixedSize(160, 45)
        self.exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC2626;
                color: white;
                font-weight: 600;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #B91C1C; }
        """)
        self.exit_btn.hide()
        self.exit_btn.clicked.connect(self.close)
        self.container_layout.addWidget(self.exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addWidget(self.container)
        self.resize(720, 520)

        # Animation Setup
        self.opacity_effect = QGraphicsOpacityEffect(self.container)
        self.container.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

        self.anim_opacity = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_opacity.setDuration(800)
        self.anim_opacity.setStartValue(0)
        self.anim_opacity.setEndValue(1)
        self.anim_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Detail Animation Timer
        self.detail_timer = QTimer(self)
        self.detail_timer.timeout.connect(self.rotate_details)
        self.current_details = []
        self.detail_index = 0

    def showEvent(self, event):
        super().showEvent(event)
        self.anim_opacity.start()

    def rotate_details(self):
        if self.current_details:
            self.detail_index = (self.detail_index + 1) % len(self.current_details)
            self.detail_label.setText(self.current_details[self.detail_index])

    def update_status(self, message, progress=None):
        self.status_label.setText(message)

        # Determine sub-details based on main message context
        new_details = []
        if "integrità" in message.lower():
            new_details = ["Verifica firma digitale...", "Controllo hash componenti...", "Analisi anti-debug...", "Scansione integrità memoria..."]
        elif "licenza" in message.lower():
            new_details = ["Lettura chiave crittografica...", "Decrittazione payload...", "Validazione Hardware ID...", "Controllo scadenza..."]
        elif "orologio" in message.lower():
            new_details = ["Contatto server NTP...", "Verifica delta temporale...", "Sincronizzazione...", "Validazione timestamp..."]
        elif "database" in message.lower():
            new_details = ["Inizializzazione SQLite in-memory...", "Caricamento schema crittografato...", "Applicazione migrazioni...", "Ottimizzazione indici..."]
        elif "backend" in message.lower():
            new_details = ["Avvio sottosistema API...", "Binding porta locale...", "Caricamento router...", "Iniezione dipendenze..."]
        elif "connessione" in message.lower():
             new_details = ["Ping servizio locale...", "Handshake di sicurezza...", "Verifica disponibilità endpoint...", "Controllo latenza..."]
        elif "risorse" in message.lower() or "interfaccia" in message.lower():
            new_details = ["Pre-rendering asset grafici...", "Caricamento temi...", "Inizializzazione motore di rendering...", "Preparazione dashboard..."]

        if new_details:
            self.current_details = new_details
            self.detail_index = 0
            self.detail_label.setText(new_details[0])
            self.detail_timer.start(300) # Fast rotation
        else:
             self.detail_timer.stop()
             self.detail_label.setText("...")

        if progress is not None:
            self.progress_bar.setValue(progress)

        QApplication.processEvents()

    def show_error(self, message):
        self.detail_timer.stop()
        self.status_label.setText("Errore di Avvio")
        self.status_label.setStyleSheet("color: #DC2626; font-size: 20px; font-weight: 700;")

        self.detail_label.setText(message)
        self.detail_label.setStyleSheet("color: #4B5563; font-size: 14px; padding: 10px;")
        self.detail_label.setWordWrap(True)

        self.progress_bar.hide()
        self.exit_btn.show()

        loop = QEventLoop()
        self.exit_btn.clicked.connect(loop.quit)
        loop.exec()
        self.close()

    def finish(self, window):
        self.close()
