from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect, QApplication
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve, pyqtSignal, QObject, QRect, QThread, pyqtSlot
from PyQt6.QtGui import QCursor
from datetime import datetime
import json
import os
from desktop_app.services.path_service import get_user_data_dir

class ToastNotification(QWidget):
    closed = pyqtSignal()

    def __init__(self, title, message, type="info", parent=None):
        super().__init__(parent)
        # Use Tool | Frameless | WindowStaysOnTopHint so it floats over everything
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        # Bug 2: Ensure deletion on close to prevent memory leaks
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

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
            # Bug 4: Fix Text Truncation
            lbl_msg.setWordWrap(True)
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

class ToastManager(QObject):
    _instance = None
    history_updated = pyqtSignal()
    # Bug 1: Thread Safety Signal
    # Note: We cannot pass QWidget (parent) across threads safely if it was created in another thread,
    # but usually parent is MainWindow (Main Thread). If parent is None, it's fine.
    # We use 'object' for parent to be generic.
    request_show_toast = pyqtSignal(object, str, str, str, int)

    @staticmethod
    def instance():
        if not ToastManager._instance:
            ToastManager._instance = ToastManager()
        return ToastManager._instance

    def __init__(self):
        super().__init__()
        self.active_toasts = []
        self.history = []
        # Connect signal to slot for thread safety
        self.request_show_toast.connect(self._show_toast_slot)
        self.load_history()

    def add_to_history(self, type, title, message):
        # Bug 10: Timezone Awareness
        entry = {
            "type": type,
            "title": title,
            "message": message,
            "timestamp": datetime.now().astimezone().isoformat()
        }
        self.history.insert(0, entry) # Newest first
        # Limit history size
        if len(self.history) > 50:
            self.history.pop()

        self.save_history()
        self.history_updated.emit()

    def save_history(self):
        # Bug 8: Persistence
        try:
            path = os.path.join(get_user_data_dir(), "notifications.json")
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving notification history: {e}")

    def load_history(self):
        # Bug 8: Persistence
        try:
            path = os.path.join(get_user_data_dir(), "notifications.json")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Ensure loaded data is a valid list
                    if isinstance(loaded, list):
                        self.history = loaded
                    else:
                        self.history = []
        except json.JSONDecodeError as e:
            # Corrupted file - reset it
            print(f"[Toast] Corrupted notification history, resetting: {e}")
            self.history = []
            # Try to delete corrupted file
            try:
                path = os.path.join(get_user_data_dir(), "notifications.json")
                os.remove(path)
            except Exception:
                pass
        except Exception as e:
            print(f"[Toast] Error loading notification history: {e}")
            self.history = []

    def show_toast(self, parent, type, title, message, duration=3000):
        # Bug 1: Thread Safety Check
        if QThread.currentThread() != QApplication.instance().thread():
            self.request_show_toast.emit(parent, type, title, message, duration)
            return

        self._show_toast_slot(parent, type, title, message, duration)

    def _get_target_geometry(self, parent):
        """Helper to determine the target geometry for toast positioning."""
        if parent and parent.isVisible() and not (parent.windowState() & Qt.WindowState.WindowMinimized):
             # Parent is visible and valid
             target_geometry = parent.geometry()
             # If parent is not top-level, map to global
             if not parent.isWindow():
                 top_left = parent.mapToGlobal(QPoint(0, 0))
                 target_geometry = QRect(top_left, parent.size())
             return target_geometry

        # Bug 7: Multi-monitor fallback
        screen = QApplication.screenAt(QCursor.pos())
        if not screen:
            screen = QApplication.primaryScreen()

        if screen:
            return screen.availableGeometry()

        return None

    @pyqtSlot(object, str, str, str, int)
    def _show_toast_slot(self, parent, type, title, message, duration):
        # S3776: Refactored to reduce complexity
        self.add_to_history(type, title, message)

        toast = ToastNotification(title, message, type, parent)
        target_geometry = self._get_target_geometry(parent)

        if target_geometry:
            # Calculate Bottom Right of the target area
            x = target_geometry.x() + target_geometry.width() - toast.width() - 20
            base_y = target_geometry.y() + target_geometry.height() - 20

            # Calculate offset based on active toasts
            offset_y = 0
            for t in self.active_toasts:
                if t.isVisible():
                    offset_y += t.height() + 10

            y = base_y - toast.height() - offset_y

            if y < target_geometry.y():
                 y = target_geometry.y() + 20

            toast.move(x, y)
            toast.setProperty("target_geometry", target_geometry)

        toast.show_toast(duration)
        self.active_toasts.append(toast)

        # Cleanup when closed
        toast.closed.connect(lambda: self.cleanup_toast(toast))

    def cleanup_toast(self, toast):
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)
            # Bug 6: Stacking Animation
            self.rearrange_toasts()

    def rearrange_toasts(self):
        cumulative_offset = 0
        for toast in self.active_toasts:
            target_geometry = toast.property("target_geometry")
            if not target_geometry: continue

            base_y = target_geometry.y() + target_geometry.height() - 20
            new_y = base_y - toast.height() - cumulative_offset

            # Animate move
            if toast.y() != new_y:
                anim = QPropertyAnimation(toast, b"pos")
                anim.setDuration(200)
                anim.setStartValue(toast.pos())
                anim.setEndValue(QPoint(toast.x(), new_y))
                anim.setEasingCurve(QEasingCurve.Type.OutQuad)
                anim.start()
                # Keep reference to avoid GC? QPropertyAnimation parent is toast.
                toast._pos_anim = anim

            cumulative_offset += toast.height() + 10

    @staticmethod
    def success(title, message, parent=None):
        ToastManager.instance().show_toast(parent, "success", title, message)

    @staticmethod
    def error(title, message, parent=None):
        ToastManager.instance().show_toast(parent, "error", title, message)

    @staticmethod
    def warning(title, message, parent=None):
        ToastManager.instance().show_toast(parent, "warning", title, message)

    @staticmethod
    def info(title, message, parent=None):
        ToastManager.instance().show_toast(parent, "info", title, message)
