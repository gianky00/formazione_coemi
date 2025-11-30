from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QProgressBar, QFrame,
                             QGraphicsDropShadowEffect, QPushButton, QApplication, QHBoxLayout,
                             QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QSize, QEventLoop, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QColor, QPixmap
from desktop_app.utils import get_asset_path
from desktop_app.components.animated_widgets import AnimatedButton

class FadeLabel(QLabel):
    """
    A QLabel that animates text changes with a fade effect.
    """
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def setText(self, text):
        # If text is the same, do nothing
        if text == self.text():
            return

        # Stop any running animation
        self.anim.stop()

        # Reset opacity to 0
        self.opacity_effect.setOpacity(0)

        # Update text
        super().setText(text)

        # Animate to 1
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()

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
                border-radius: 16px;
                border: 1px solid #E5E7EB;
            }
            QLabel {
                border: none;
                outline: none;
            }
        """)

        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.container.setGraphicsEffect(shadow)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(50, 50, 50, 40)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.container_layout.setSpacing(20)

        # Logo
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = get_asset_path("desktop_app/assets/logo.png")
        if logo_path:
            pixmap = QPixmap(logo_path)
            # Slightly larger logo
            scaled = pixmap.scaled(QSize(500, 250), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled)
        else:
            self.logo_label.setText("INTELLEO")
            self.logo_label.setStyleSheet("font-size: 52px; font-weight: bold; color: #1E3A8A; border: none;")

        self.container_layout.addWidget(self.logo_label)
        self.container_layout.addSpacing(15)

        # Status Label (FadeLabel)
        self.status_label = FadeLabel("Avvio sistema...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #4B5563; font-size: 16px; font-weight: 500; border: none;")
        self.container_layout.addWidget(self.status_label)

        # Progress Bar (Full Width)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #F3F4F6;
                border-radius: 3px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #2563EB; /* Bright Blue */
                border-radius: 3px;
            }
        """)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        # Add to layout without fixed width constraint (it will stretch to margins)
        self.container_layout.addWidget(self.progress_bar)

        self.container_layout.addStretch()

        # Footer (Copyright & Version)
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 10, 0, 0)

        self.copyright_label = QLabel("© 2025 Intelleo Security")
        self.copyright_label.setStyleSheet("color: #9CA3AF; font-size: 13px; border: none;")
        footer_layout.addWidget(self.copyright_label, alignment=Qt.AlignmentFlag.AlignLeft)

        footer_layout.addStretch()

        self.version_label = QLabel("v1.0.0")
        self.version_label.setStyleSheet("color: #9CA3AF; font-size: 13px; font-weight: 500; border: none;")
        footer_layout.addWidget(self.version_label, alignment=Qt.AlignmentFlag.AlignRight)

        self.container_layout.addLayout(footer_layout)

        # Error Button (Hidden by default, replaces progress if error)
        self.exit_btn = AnimatedButton("Chiudi")
        self.exit_btn.setFixedSize(140, 45)
        self.exit_btn.set_colors("#DC2626", "#B91C1C", "#991B1B", text="#FFFFFF")
        self.exit_btn.hide()
        self.exit_btn.clicked.connect(self.close)
        self.container_layout.addWidget(self.exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addWidget(self.container)
        self.resize(700, 500) # Slightly larger

        # Entrance Animation Setup
        self.opacity_effect = QGraphicsOpacityEffect(self.container)
        self.container.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

        self.anim_opacity = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_opacity.setDuration(800)
        self.anim_opacity.setStartValue(0)
        self.anim_opacity.setEndValue(1)
        self.anim_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

    def showEvent(self, event):
        super().showEvent(event)
        self.anim_opacity.start()

    def update_status(self, message, progress=None):
        self.status_label.setText(message)
        if progress is not None:
            self.progress_bar.setValue(progress)
        QApplication.processEvents()

    def show_error(self, message):
        """
        Displays an error message and waits for the user to close the splash.
        """
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #DC2626; font-size: 16px; font-weight: 700; padding: 10px; border: none;")
        self.status_label.setWordWrap(True)

        self.progress_bar.hide()
        self.exit_btn.show()

        # Block until closed
        loop = QEventLoop()
        self.exit_btn.clicked.connect(loop.quit)
        loop.exec()
        self.close()

    def finish(self, window):
        """
        Mimics QSplashScreen.finish(window).
        Closes the splash screen when the main window is ready.
        """
        self.close()
