from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QProgressBar, QFrame,
                             QGraphicsDropShadowEffect, QPushButton, QApplication, QHBoxLayout,
                             QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QSize, QEventLoop, QTimer, QPropertyAnimation, QEasingCurve, QRectF
from PyQt6.QtGui import QColor, QPixmap, QPainter, QLinearGradient, QBrush, QFont
from desktop_app.utils import get_asset_path

class DynamicProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(24)
        self.setTextVisible(False) # We draw text manually

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        width = rect.width()
        height = rect.height()
        radius = height / 2

        # 1. Background (Grey)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#F3F4F6"))
        painter.drawRoundedRect(QRectF(rect), radius, radius)

        # 2. Chunk (Blue Gradient)
        val = self.value()
        max_val = self.maximum()
        ratio = val / max_val if max_val > 0 else 0

        progress_width = width * ratio

        if progress_width > 0:
            gradient = QLinearGradient(0, 0, progress_width, 0)
            gradient.setColorAt(0, QColor("#2563EB"))
            gradient.setColorAt(1, QColor("#1D4ED8"))

            painter.setBrush(QBrush(gradient))

            # Draw rounded rect for chunk
            chunk_rect = QRectF(0, 0, progress_width, height)
            painter.drawRoundedRect(chunk_rect, radius, radius)

        # 3. Text (Dynamic Contrast)
        text = f"{int(ratio * 100)}%"
        # Use generic font if Inter not found, but try Inter
        font = QFont("Inter", 10, QFont.Weight.Bold)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        painter.setFont(font)

        # Center alignment
        # We need to explicitly cast rect to integer QRect for drawText if strict,
        # but PyQt handles it.

        # Draw Base Text (Dark - for the grey part)
        painter.setPen(QColor("#1F2937")) # Dark blue-grey for better harmony
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

        # Draw Overlay Text (White - for the blue part)
        # We set the clip rect to the progress chunk
        if progress_width > 0:
            # Save painter state before clipping
            painter.save()
            painter.setClipRect(0, 0, int(progress_width), int(height))
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
            painter.restore()

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
            QFrame#splash_container {
                background-color: #FFFFFF;
                border-radius: 16px;
                border: 1px solid #E5E7EB;
            }
            QLabel {
                border: none;
                background-color: transparent;
            }
        """)
        self.container.setObjectName("splash_container")

        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(60)
        shadow.setXOffset(0)
        shadow.setYOffset(30)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.container.setGraphicsEffect(shadow)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(60, 70, 60, 50)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.container_layout.setSpacing(30)

        # Logo
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = get_asset_path("desktop_app/assets/logo.png")
        if logo_path:
            pixmap = QPixmap(logo_path)
            # Slightly bigger
            scaled = pixmap.scaled(QSize(420, 180), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled)
        else:
            self.logo_label.setText("INTELLEO")
            self.logo_label.setStyleSheet("font-size: 56px; font-weight: 800; color: #1E3A8A; font-family: 'Inter'; letter-spacing: -1px;")

        self.container_layout.addWidget(self.logo_label)
        self.container_layout.addSpacing(10)

        # Status Label (Main Step)
        self.status_label = QLabel("Inizializzazione Sistema")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Modern font, slightly darker
        self.status_label.setStyleSheet("color: #111827; font-size: 20px; font-weight: 600; font-family: 'Inter';")
        self.container_layout.addWidget(self.status_label)

        # Detail Label (Technical sub-steps)
        self.detail_label = QLabel("Caricamento configurazione")
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_label.setFixedHeight(20) # Fixed height to prevent jump
        self.detail_label.setStyleSheet("color: #6B7280; font-size: 14px; font-weight: 500; font-family: 'Inter';")
        self.container_layout.addWidget(self.detail_label)

        self.container_layout.addSpacing(10)

        # Progress Bar (Dynamic)
        self.progress_bar = DynamicProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.container_layout.addWidget(self.progress_bar)

        self.container_layout.addStretch()

        # Footer
        footer_layout = QHBoxLayout()
        self.copyright_label = QLabel("© 2025 Intelleo Security")
        self.copyright_label.setStyleSheet("color: #9CA3AF; font-size: 13px; font-family: 'Inter';")
        footer_layout.addWidget(self.copyright_label, alignment=Qt.AlignmentFlag.AlignLeft)

        footer_layout.addStretch()

        self.version_label = QLabel("v1.0.0")
        self.version_label.setStyleSheet("""
            color: #6B7280;
            font-size: 12px;
            font-weight: 600;
            font-family: 'Inter';
            padding: 4px 8px;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
        """)
        footer_layout.addWidget(self.version_label, alignment=Qt.AlignmentFlag.AlignRight)

        self.container_layout.addLayout(footer_layout)

        # Exit Button (Error State)
        self.exit_btn = QPushButton("Chiudi Applicazione")
        self.exit_btn.setFixedSize(180, 50)
        self.exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC2626;
                color: white;
                font-weight: 600;
                font-size: 15px;
                border-radius: 10px;
                font-family: 'Inter';
            }
            QPushButton:hover { background-color: #B91C1C; }
        """)
        self.exit_btn.hide()
        self.exit_btn.clicked.connect(self.close)
        self.container_layout.addWidget(self.exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addWidget(self.container)
        self.resize(800, 550) # Even larger and more spacious

        # Animation Setup
        self.opacity_effect = QGraphicsOpacityEffect(self.container)
        self.container.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

        self.anim_opacity = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_opacity.setDuration(1000) # Slower entrance
        self.anim_opacity.setStartValue(0)
        self.anim_opacity.setEndValue(1)
        self.anim_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Detail Animation Timer
        self.detail_timer = QTimer(self)
        self.detail_timer.timeout.connect(self.next_detail)
        self.current_details = []
        self.detail_index = 0

    def showEvent(self, event):
        super().showEvent(event)
        self.anim_opacity.start()

    def next_detail(self):
        # Move to next detail if available
        if self.current_details and self.detail_index < len(self.current_details) - 1:
            self.detail_index += 1
            # Strip dots just in case
            text = self.current_details[self.detail_index].rstrip('.')
            self.detail_label.setText(text)
        else:
            # Reached end of list, stop timer
            self.detail_timer.stop()

    def update_status(self, message, progress=None):
        # Remove dots
        clean_message = message.rstrip('.')
        self.status_label.setText(clean_message)

        # Determine sub-details based on main message context
        # Define longer lists to fill time
        new_details = []
        if "integrità" in message.lower():
            new_details = ["Verifica firma digitale", "Controllo hash componenti", "Analisi anti-debug", "Scansione integrità memoria"]
        elif "licenza" in message.lower():
            new_details = ["Lettura chiave crittografica", "Decrittazione payload", "Validazione Hardware ID", "Controllo scadenza"]
        elif "orologio" in message.lower():
            new_details = ["Contatto server NTP", "Verifica delta temporale", "Sincronizzazione", "Validazione timestamp"]
        elif "database" in message.lower():
            new_details = ["Inizializzazione SQLite in-memory", "Caricamento schema crittografato", "Applicazione migrazioni", "Ottimizzazione indici", "Verifica consistenza"]
        elif "backend" in message.lower():
            new_details = ["Avvio sottosistema API", "Binding porta locale", "Caricamento router", "Iniezione dipendenze"]
        elif "connessione" in message.lower():
             new_details = ["Ping servizio locale", "Handshake di sicurezza", "Verifica disponibilità endpoint", "Controllo latenza"]
        elif "risorse" in message.lower() or "interfaccia" in message.lower():
            new_details = ["Pre-rendering asset grafici", "Caricamento temi", "Inizializzazione motore di rendering", "Preparazione dashboard", "Avvio completato"]

        if new_details:
            self.current_details = new_details
            self.detail_index = 0
            self.detail_label.setText(new_details[0])

            # Calculate interval to ensure no dead time?
            # Launcher steps are roughly ~2-5% progress jumps, or some seconds.
            # If we assume ~2 seconds per major step:
            count = len(new_details)
            interval = 2000 // count if count > 0 else 500
            # Cap interval
            interval = max(400, min(interval, 800))

            self.detail_timer.start(interval)
        else:
             self.detail_timer.stop()
             # Keep previous detail or clear? Better keep to avoid empty space flicker or set generic
             # self.detail_label.setText("...")

        if progress is not None:
            self.progress_bar.setValue(progress)

        QApplication.processEvents()

    def show_error(self, message):
        self.detail_timer.stop()
        self.status_label.setText("Errore di Avvio")
        self.status_label.setStyleSheet("color: #DC2626; font-size: 22px; font-weight: 700; font-family: 'Inter';")

        self.detail_label.setText(message)
        self.detail_label.setStyleSheet("color: #4B5563; font-size: 15px; padding: 10px; font-family: 'Inter';")
        self.detail_label.setWordWrap(True)
        self.detail_label.setFixedHeight(100) # Allow more space for error

        self.progress_bar.hide()
        self.exit_btn.show()

        loop = QEventLoop()
        self.exit_btn.clicked.connect(loop.quit)
        loop.exec()
        self.close()

    def finish(self, window):
        self.close()
