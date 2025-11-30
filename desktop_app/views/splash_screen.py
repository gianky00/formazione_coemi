from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QProgressBar, QFrame,
                             QGraphicsDropShadowEffect, QPushButton, QApplication, QHBoxLayout,
                             QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QSize, QEventLoop, QTimer, QPropertyAnimation, QEasingCurve, QRectF, QParallelAnimationGroup, QSequentialAnimationGroup, QPointF
from PyQt6.QtGui import QColor, QPixmap, QPainter, QLinearGradient, QBrush, QFont, QRadialGradient, QPen
from desktop_app.utils import get_asset_path, load_colored_icon
import random

class ChecklistItem(QWidget):
    def __init__(self, icon_name, label, color, parent=None):
        super().__init__(parent)
        self.active = False
        self.target_color = color

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(8)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(20, 20)

        # Load inactive icon (Grey)
        self.inactive_icon = load_colored_icon(icon_name, "#9CA3AF") # Gray-400
        self.icon_label.setPixmap(self.inactive_icon.pixmap(20, 20))

        self.text_label = QLabel(label)
        self.text_label.setStyleSheet("color: #9CA3AF; font-size: 13px; font-weight: 500; font-family: 'Inter';")

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)

        # Preload active icon
        self.active_icon = load_colored_icon(icon_name, self.target_color)

    def activate(self):
        if self.active: return
        self.active = True

        self.icon_label.setPixmap(self.active_icon.pixmap(20, 20))
        self.text_label.setStyleSheet(f"color: {self.target_color}; font-size: 13px; font-weight: 700; font-family: 'Inter';")

class HolographicChecklist(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(25)
        layout.setContentsMargins(0, 10, 0, 10)

        # Icons available: settings, file-text, database
        self.item_security = ChecklistItem("settings.svg", "Sistema", "#10B981") # Green
        self.item_license = ChecklistItem("file-text.svg", "Licenza", "#3B82F6") # Blue
        self.item_ai = ChecklistItem("database.svg", "Intelligenza", "#8B5CF6") # Purple

        layout.addWidget(self.item_security)
        layout.addWidget(self.item_license)
        layout.addWidget(self.item_ai)

    def update_state(self, status_text):
        lower = status_text.lower()
        if "integrità" in lower or "avvio" in lower:
            self.item_security.activate()
        if "licenza" in lower:
            self.item_security.activate()
            self.item_license.activate()
        if "database" in lower or "backend" in lower or "risorse" in lower:
            self.item_security.activate()
            self.item_license.activate()
            self.item_ai.activate()

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(0.5, 2.5) # Move forward
        self.vy = random.uniform(-1.0, 1.0) # Spread vertical
        self.life = 1.0
        self.decay = random.uniform(0.03, 0.08)
        self.size = random.uniform(1.5, 3.5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        return self.life > 0

class DynamicProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self.setTextVisible(False)
        self._shimmer_offset = 0
        self.particles = []

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(16) # ~60 FPS for fluid particles

    def _animate(self):
        # Update Shimmer
        self._shimmer_offset += 4
        if self._shimmer_offset > self.width() + 150:
            self._shimmer_offset = -150

        # Emit Particles (only if moving and not full)
        val = self.value()
        max_val = self.maximum()
        if val > 0 and val < max_val:
             ratio = val / max_val
             tip_x = self.width() * ratio
             # Emit near the vertical center with some spread
             tip_y = self.height() / 2 + random.uniform(-5, 5)

             # Emit multiple particles for density
             if random.random() < 0.4:
                 self.particles.append(Particle(tip_x, tip_y))

        # Update existing particles
        self.particles = [p for p in self.particles if p.update()]

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        width = rect.width()
        height = rect.height()
        radius = height / 2

        # 1. Track Background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#F1F5F9")) # Light Slate
        painter.drawRoundedRect(QRectF(rect), radius, radius)

        # 2. Fill (Electric Gradient)
        val = self.value()
        max_val = self.maximum()
        ratio = val / max_val if max_val > 0 else 0

        progress_width = width * ratio

        if progress_width > 0:
            # Main Beam Gradient
            gradient = QLinearGradient(0, 0, progress_width, 0)
            gradient.setColorAt(0, QColor("#3B82F6"))   # Blue-500
            gradient.setColorAt(0.5, QColor("#60A5FA")) # Blue-400
            gradient.setColorAt(1, QColor("#8B5CF6"))   # Violet-500 (Energy Tip)

            painter.setBrush(QBrush(gradient))
            fill_rect = QRectF(0, 0, progress_width, height)
            painter.drawRoundedRect(fill_rect, radius, radius)

            # 3. High-Speed Shimmer
            painter.save()
            painter.setClipRect(fill_rect)
            shimmer_grad = QLinearGradient(self._shimmer_offset, 0, self._shimmer_offset + 80, 0)
            shimmer_grad.setColorAt(0, QColor(255, 255, 255, 0))
            shimmer_grad.setColorAt(0.5, QColor(255, 255, 255, 160)) # Bright streak
            shimmer_grad.setColorAt(1, QColor(255, 255, 255, 0))
            painter.setBrush(QBrush(shimmer_grad))
            painter.drawRect(fill_rect)
            painter.restore()

            # 4. Tip Glow (Energy Ball)
            # Draw a soft white glow at the leading edge
            glow_radius = height * 1.5
            glow = QRadialGradient(progress_width, height/2, glow_radius)
            glow.setColorAt(0, QColor(255, 255, 255, 180))
            glow.setColorAt(1, QColor(255, 255, 255, 0))
            painter.setBrush(QBrush(glow))
            painter.drawEllipse(QPointF(progress_width, height/2), glow_radius, glow_radius)

        # 5. Particles Rendering
        for p in self.particles:
            alpha = int(255 * p.life)
            # Fade from Violet to Transparent
            color = QColor("#A78BFA")
            color.setAlpha(alpha)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPointF(p.x, p.y), p.size, p.size)

        # 6. Text (Modern Overlay)
        text = f"{int(ratio * 100)}%"
        font = QFont("Inter", 11, QFont.Weight.Bold)
        painter.setFont(font)

        # Draw Base Text (Dark Grey)
        painter.setPen(QColor("#374151"))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

        # Draw Overlay Text (White) for contrast over the bar
        if progress_width > 0:
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
            scaled = pixmap.scaled(QSize(420, 180), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled)
        else:
            self.logo_label.setText("INTELLEO")
            self.logo_label.setStyleSheet("font-size: 56px; font-weight: 800; color: #1E3A8A; font-family: 'Inter'; letter-spacing: -1px;")

        # Logo Animation Effects
        # REMOVED QGraphicsOpacityEffect to prevent QPainter errors and threading issues.
        # We rely on Window Opacity for entrance.

        self.container_layout.addWidget(self.logo_label)
        self.container_layout.addSpacing(40) # Increased spacing to prevent overlap

        # Status Label (Main Step)
        self.status_label = QLabel("") # Empty initial text to prevent ghost artifacts
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #111827; font-size: 20px; font-weight: 600; font-family: 'Inter';")
        self.container_layout.addWidget(self.status_label)

        # REMOVED Status Opacity Effect

        # Detail Label (Technical sub-steps)
        self.detail_label = QLabel("Caricamento configurazione")
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_label.setFixedHeight(20)
        self.detail_label.setStyleSheet("color: #6B7280; font-size: 14px; font-weight: 500; font-family: 'Inter';")
        self.container_layout.addWidget(self.detail_label)

        # Holographic Checklist
        self.checklist = HolographicChecklist()
        self.container_layout.addWidget(self.checklist)

        self.container_layout.addSpacing(5)

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
        self.resize(800, 550)

        # Window Entrance Animation (Animating Window Opacity instead of Container Effect)
        # This preserves the shadow on the container.
        self.setWindowOpacity(0)

        self.anim_opacity = QPropertyAnimation(self, b"windowOpacity")
        self.anim_opacity.setDuration(1000)
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
        if self.current_details and self.detail_index < len(self.current_details) - 1:
            self.detail_index += 1
            text = self.current_details[self.detail_index].rstrip('.')
            self.detail_label.setText(text)
        else:
            self.detail_timer.stop()

    def update_status(self, message, progress=None):
        clean_message = message.rstrip('.')

        if self.status_label.text() != clean_message:
            self._animate_text_change(clean_message)
        else:
             self.status_label.setText(clean_message)

        # Update Checklist
        if hasattr(self, 'checklist'):
            self.checklist.update_state(clean_message)

        new_details = []
        msg_lower = message.lower()
        if "integrità" in msg_lower:
            new_details = ["Verifica firma digitale", "Controllo hash componenti", "Analisi anti-debug", "Scansione integrità memoria"]
        elif "licenza" in msg_lower:
            new_details = ["Lettura chiave crittografica", "Decrittazione payload", "Validazione Hardware ID", "Controllo scadenza"]
        elif "orologio" in msg_lower:
            new_details = ["Contatto server NTP", "Verifica delta temporale", "Sincronizzazione", "Validazione timestamp"]
        elif "database" in msg_lower:
            new_details = ["Inizializzazione SQLite in-memory", "Caricamento schema crittografato", "Applicazione migrazioni", "Ottimizzazione indici", "Verifica consistenza"]
        elif "backend" in msg_lower:
            new_details = ["Avvio sottosistema API", "Binding porta locale", "Caricamento router", "Iniezione dipendenze"]
        elif "connessione" in msg_lower:
             new_details = ["Ping servizio locale", "Handshake di sicurezza", "Verifica disponibilità endpoint", "Controllo latenza"]
        elif "risorse" in msg_lower or "interfaccia" in msg_lower:
            new_details = ["Pre-rendering asset grafici", "Caricamento temi", "Inizializzazione motore di rendering", "Preparazione dashboard", "Avvio completato"]

        if new_details:
            self.current_details = new_details
            self.detail_index = 0
            self.detail_label.setText(new_details[0])
            count = len(new_details)
            interval = 2000 // count if count > 0 else 500
            interval = max(400, min(interval, 800))
            self.detail_timer.start(interval)
        else:
             self.detail_timer.stop()

        if progress is not None:
            self.progress_bar.setValue(progress)

        QApplication.processEvents()

    def _animate_text_change(self, new_text):
        # Simplified text change without Opacity Effect
        self.status_label.setText(new_text)

    def show_error(self, message):
        self.detail_timer.stop()
        self.status_label.setText("Errore di Avvio")
        self.status_label.setStyleSheet("color: #DC2626; font-size: 22px; font-weight: 700; font-family: 'Inter';")

        self.detail_label.setText(message)
        self.detail_label.setStyleSheet("color: #4B5563; font-size: 15px; padding: 10px; font-family: 'Inter';")
        self.detail_label.setWordWrap(True)
        self.detail_label.setFixedHeight(100)

        self.progress_bar.hide()
        self.exit_btn.show()

        loop = QEventLoop()
        self.exit_btn.clicked.connect(loop.quit)
        loop.exec()
        self.close()

    def finish(self, window):
        # Animate Window Opacity instead of effect
        self.anim_exit_opacity = QPropertyAnimation(self, b"windowOpacity")
        self.anim_exit_opacity.setDuration(500)
        self.anim_exit_opacity.setStartValue(1)
        self.anim_exit_opacity.setEndValue(0)
        self.anim_exit_opacity.setEasingCurve(QEasingCurve.Type.InBack)

        self.anim_exit_opacity.finished.connect(self.close)
        self.anim_exit_opacity.start()
