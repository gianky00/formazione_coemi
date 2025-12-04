from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect, QApplication
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve, pyqtSignal

class ToastNotification(QWidget):
    closed = pyqtSignal()

    def __init__(self, title, message, type="info", parent=None):
        super().__init__(parent)
        # Use Tool | Frameless | WindowStaysOnTopHint so it floats over everything
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Styles
        colors = {
            "success": "#10B981", # Green
            "error": "#EF4444",   # Red
            "warning": "#F59E0B", # Yellow
            "info": "#3B82F6"     # Blue
        }
        accent_color = colors.get(type, colors["info"])
        bg_color = "#FFFFFF"
        text_color = "#1F2937"
        msg_color = "#6B7280"

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
            QLabel#title {{
                font-weight: bold;
                font-size: 14px;
                color: {text_color};
            }}
            QLabel#message {{
                font-size: 12px;
                color: {msg_color};
            }}
            QWidget#accent {{
                background-color: {accent_color};
                border-top-left-radius: 8px;
                border-bottom-left-radius: 8px;
                border: none;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Accent strip
        accent = QWidget()
        accent.setObjectName("accent")
        accent.setFixedWidth(6)
        layout.addWidget(accent)

        # Content
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 20, 10)
        content_layout.setSpacing(2)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("title")
        content_layout.addWidget(lbl_title)

        if message:
            lbl_msg = QLabel(message)
            lbl_msg.setObjectName("message")
            content_layout.addWidget(lbl_msg)

        layout.addLayout(content_layout)

        # Opacity Effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # Timer
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fade_out)

        self.adjustSize()

    def show_toast(self, duration=3000):
        self.show()
        # Animation Fade In
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

        self.timer.start(duration)

    def fade_out(self):
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.finished.connect(self.close)
        self.anim.finished.connect(self.closed.emit)
        self.anim.start()

class ToastManager:
    _instance = None

    @staticmethod
    def instance():
        if not ToastManager._instance:
            ToastManager._instance = ToastManager()
        return ToastManager._instance

    def __init__(self):
        self.active_toasts = []

    def show_toast(self, parent, type, title, message, duration=3000):
        toast = ToastNotification(title, message, type, parent)

        if parent:
            # Position: Bottom Right of parent window
            # If parent is not visible or minimized, mapToGlobal might act weird,
            # but usually called when active.

            # Map (0,0) of parent to global
            parent_top_left = parent.mapToGlobal(QPoint(0,0))

            # Calculate Bottom Right
            x = parent_top_left.x() + parent.width() - toast.width() - 20
            y = parent_top_left.y() + parent.height() - toast.height() - 20

            # Stack existing toasts?
            # If there are active toasts, move up.
            offset_y = 0
            for t in self.active_toasts:
                if t.isVisible():
                    offset_y += t.height() + 10

            y -= offset_y

            toast.move(x, y)

        toast.show_toast(duration)
        self.active_toasts.append(toast)

        # Cleanup when closed
        def cleanup():
            if toast in self.active_toasts:
                self.active_toasts.remove(toast)
        toast.closed.connect(cleanup)

    @staticmethod
    def success(title, message, parent=None):
        if not parent: parent = QApplication.activeWindow()
        ToastManager.instance().show_toast(parent, "success", title, message)

    @staticmethod
    def error(title, message, parent=None):
        if not parent: parent = QApplication.activeWindow()
        ToastManager.instance().show_toast(parent, "error", title, message)

    @staticmethod
    def warning(title, message, parent=None):
        if not parent: parent = QApplication.activeWindow()
        ToastManager.instance().show_toast(parent, "warning", title, message)

    @staticmethod
    def info(title, message, parent=None):
        if not parent: parent = QApplication.activeWindow()
        ToastManager.instance().show_toast(parent, "info", title, message)
