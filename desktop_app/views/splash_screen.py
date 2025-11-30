from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QProgressBar, QFrame,
                             QGraphicsDropShadowEffect, QPushButton, QApplication)
from PyQt6.QtCore import Qt, QSize, QEventLoop, QTimer
from PyQt6.QtGui import QColor, QPixmap
from desktop_app.utils import get_asset_path
from desktop_app.components.animated_widgets import AnimatedButton

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
        """)

        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.container.setGraphicsEffect(shadow)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(40, 40, 40, 40)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.container_layout.setSpacing(20)

        # Logo
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = get_asset_path("desktop_app/assets/logo.png")
        if logo_path:
            pixmap = QPixmap(logo_path)
            scaled = pixmap.scaled(QSize(400, 200), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled)
        else:
            self.logo_label.setText("INTELLEO")
            self.logo_label.setStyleSheet("font-size: 40px; font-weight: bold; color: #1E3A8A;")

        self.container_layout.addWidget(self.logo_label)

        # Status Label
        self.status_label = QLabel("Avvio sistema...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #4B5563; font-size: 14px; font-weight: 500;")
        self.container_layout.addWidget(self.status_label)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(300)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #E5E7EB;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #1D4ED8;
                border-radius: 3px;
            }
        """)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.container_layout.addWidget(self.progress_bar)

        # Error Button (Hidden by default)
        self.exit_btn = AnimatedButton("Chiudi")
        self.exit_btn.setFixedSize(120, 40)
        self.exit_btn.set_colors("#DC2626", "#B91C1C", "#991B1B", text="#FFFFFF")
        self.exit_btn.hide()
        self.exit_btn.clicked.connect(self.close)
        self.container_layout.addWidget(self.exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addWidget(self.container)
        self.resize(600, 400) # Initial size

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
        self.status_label.setStyleSheet("color: #DC2626; font-size: 15px; font-weight: 700; padding: 10px;")
        self.status_label.setWordWrap(True)

        self.progress_bar.hide()
        self.exit_btn.show()

        # Block until closed
        loop = QEventLoop()
        self.exit_btn.clicked.connect(loop.quit)
        # Also connect close event? No, simple button click is enough.
        loop.exec()
        self.close()
