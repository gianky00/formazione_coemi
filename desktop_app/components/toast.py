from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve, QSize
from PyQt6.QtGui import QColor, QPainter, QIcon
from desktop_app.utils import load_colored_icon

class ToastNotification(QWidget):
    """
    A non-blocking toast notification that slides in, stays for a few seconds, and slides out.
    """
    def __init__(self, parent, title, message, icon_name="file-text.svg", duration=5000):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.duration = duration
        self.parent_widget = parent

        # Style and Layout
        self.setFixedSize(320, 90)
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
            QLabel#title {
                color: #1F2937;
                font-weight: 700;
                font-size: 14px;
            }
            QLabel#message {
                color: #6B7280;
                font-size: 13px;
                line-height: 1.4;
            }
        """)

        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel()
        icon = load_colored_icon(icon_name, "#1D4ED8") # Blue-700
        if not icon.isNull():
            icon_label.setPixmap(icon.pixmap(24, 24))
        icon_label.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignTop)

        # Text Container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        text_layout.setContentsMargins(0, 0, 0, 0)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("title")
        title_lbl.setStyleSheet("border: none; background: transparent;") # Reset for safety
        text_layout.addWidget(title_lbl)

        msg_lbl = QLabel(message)
        msg_lbl.setObjectName("message")
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("border: none; background: transparent;")
        text_layout.addWidget(msg_lbl)

        layout.addLayout(text_layout)

        # Timer for auto-close
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close_toast)
        self.timer.setSingleShot(True)

    def show_toast(self):
        """Shows the toast with animation."""
        self.show()

        # Position: Bottom Right with margin
        if self.parent_widget:
            parent_rect = self.parent_widget.geometry()
            # Calculate global position if parent is not a window?
            # If parent is the main window, we want it relative to that window or screen?
            # Usually "notification" is relative to the application window.
            # Using mapToGlobal might be safer if parent is a widget.
            # But let's assume parent is Main Window.

            # Position relative to parent's bottom right
            x = parent_rect.width() - self.width() - 20
            final_y = parent_rect.height() - self.height() - 20
            start_y = parent_rect.height() # Start below

            # Since self is a child of parent (passed in __init__), move() uses parent coordinates.
            # If we used Window flag, we might need global coords.
            # But we passed `parent` to `super().__init__`, so it's a child widget (or window child).
            # Wait, `Qt.WindowType.Tool` usually makes it a top-level window.
            # If it's top-level, we need global coordinates.

            gp = self.parent_widget.mapToGlobal(QPoint(0, 0))
            x += gp.x()
            final_y += gp.y()
            start_y += gp.y()
        else:
            # Fallback to screen geometry? Let's assume parent is always passed.
            return

        self.move(x, start_y)

        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(400)
        self.anim.setStartValue(QPoint(x, start_y))
        self.anim.setEndValue(QPoint(x, final_y))
        self.anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self.anim.start()

        self.timer.start(self.duration)

    def close_toast(self):
        # Fade out or Slide down
        current_pos = self.pos()
        target_pos = QPoint(current_pos.x(), current_pos.y() + 20)

        self.anim_out = QPropertyAnimation(self, b"pos")
        self.anim_out.setDuration(300)
        self.anim_out.setStartValue(current_pos)
        self.anim_out.setEndValue(target_pos)
        self.anim_out.setEasingCurve(QEasingCurve.Type.InQuad)

        # Also fade opacity
        # Note: Opacity on top-level widgets requires setWindowOpacity
        self.anim_fade = QPropertyAnimation(self, b"windowOpacity")
        self.anim_fade.setDuration(300)
        self.anim_fade.setStartValue(1.0)
        self.anim_fade.setEndValue(0.0)

        self.anim_out.finished.connect(self.close)

        self.anim_out.start()
        self.anim_fade.start()
