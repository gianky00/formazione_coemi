import threading
from collections import deque
from datetime import datetime

from PySide6.QtCore import QObject, QPoint, Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class Notification:
    def __init__(
        self,
        title,
        message,
        notification_type="info",
        action=None,
        action_label=None,
        category=None,
        priority=0,
    ):
        self.id = id(self)
        self.title = title
        self.message = message
        self.notification_type = notification_type
        self.action = action
        self.action_label = action_label
        self.category = category
        self.priority = priority
        self.timestamp = datetime.now()
        self.read = False
        self.dismissed = False


class NotificationCenter(QObject):
    changed = Signal()
    MAX_NOTIFICATIONS = 100

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.notifications = deque(maxlen=self.MAX_NOTIFICATIONS)
        self._lock = threading.Lock()

    def add(
        self,
        title,
        message,
        notification_type="info",
        action=None,
        action_label=None,
        category=None,
        priority=0,
        show_toast=True,
    ):
        notif = Notification(
            title, message, notification_type, action, action_label, category, priority
        )
        with self._lock:
            self.notifications.appendleft(notif)

        if show_toast and hasattr(self.controller, "toast_manager"):
            self.controller.toast_manager.show(title, message, notification_type, on_click=action)

        self.changed.emit()
        return notif

    def get_all(self, include_dismissed=False):
        with self._lock:
            return (
                list(self.notifications)
                if include_dismissed
                else [n for n in self.notifications if not n.dismissed]
            )

    def get_unread_count(self):
        with self._lock:
            return len([n for n in self.notifications if not n.read and not n.dismissed])

    def mark_all_read(self):
        with self._lock:
            for n in self.notifications:
                n.read = True
        self.changed.emit()

    def clear_all(self):
        with self._lock:
            self.notifications.clear()
        self.changed.emit()

    def mark_read(self, nid):
        with self._lock:
            for n in self.notifications:
                if n.id == nid:
                    n.read = True
                    break
        self.changed.emit()

    def dismiss(self, nid):
        with self._lock:
            for n in self.notifications:
                if n.id == nid:
                    n.dismissed = True
                    break
        self.changed.emit()


class NotificationBell(QWidget):
    def __init__(self, notification_center, on_click=None):
        super().__init__()
        self.notification_center = notification_center
        self.on_click_callback = on_click
        self.setup_ui()
        self.notification_center.changed.connect(self.update_badge)
        self.update_badge()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.btn_bell = QPushButton("🔔")
        self.btn_bell.setFixedSize(40, 40)
        self.btn_bell.setCursor(Qt.PointingHandCursor)
        self.btn_bell.setStyleSheet(
            "background: transparent; color: white; font-size: 20px; border: none;"
        )
        self.btn_bell.clicked.connect(self._on_click)
        layout.addWidget(self.btn_bell)

        self.badge = QLabel("0", self.btn_bell)
        self.badge.setFixedSize(18, 18)
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setStyleSheet(
            "background-color: #EF4444; color: white; border-radius: 9px; font-size: 10px; font-weight: bold;"
        )
        self.badge.move(22, 2)
        self.badge.hide()

    def _on_click(self):
        if self.on_click_callback:
            self.on_click_callback()

    def update_badge(self):
        count = self.notification_center.get_unread_count()
        if count > 0:
            self.badge.setText(str(count) if count < 100 else "99+")
            self.badge.show()
        else:
            self.badge.hide()


class NotificationPanel(QFrame):
    def __init__(self, parent_bell, notification_center, controller):
        super().__init__(None)  # Popup
        self.notification_center = notification_center
        self.controller = controller

        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFixedSize(400, 450)
        self.setStyleSheet(
            "background-color: white; border: 1px solid #D1D5DB; border-radius: 8px;"
        )

        self.setup_ui()
        self.load_notifications()

        # Position
        pos = parent_bell.mapToGlobal(QPoint(0, parent_bell.height()))
        self.move(pos.x() - 360, pos.y() + 5)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        header = QFrame()
        header.setFixedHeight(45)
        header.setStyleSheet(
            "background-color: #F3F4F6; border-top-left-radius: 8px; border-top-right-radius: 8px;"
        )
        h_layout = QHBoxLayout(header)
        h_layout.addWidget(QLabel("Notifiche"))
        h_layout.addStretch()

        btn_all = QPushButton("Segna tutto letto")
        btn_all.setFlat(True)
        btn_all.setStyleSheet("color: #3B82F6;")
        btn_all.clicked.connect(self._mark_all_read)
        h_layout.addWidget(btn_all)
        layout.addWidget(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")
        self.container = QWidget()
        self.c_layout = QVBoxLayout(self.container)
        self.c_layout.addStretch()
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

    def load_notifications(self):
        # Clear
        for i in reversed(range(self.c_layout.count() - 1)):
            self.c_layout.itemAt(i).widget().setParent(None)

        notifs = self.notification_center.get_all()[:20]
        if not notifs:
            self.c_layout.insertWidget(0, QLabel("Nessuna notifica"))
            return

        for n in notifs:
            item = QFrame()
            item.setStyleSheet(
                f"background-color: {'white' if n.read else '#EFF6FF'}; border-bottom: 1px solid #E5E7EB; padding: 5px;"
            )
            i_layout = QVBoxLayout(item)
            title = QLabel(f"{'• ' if not n.read else ''}{n.title}")
            title.setStyleSheet("font-weight: bold;")
            i_layout.addWidget(title)
            i_layout.addWidget(QLabel(n.message[:100]))

            item.mousePressEvent = lambda e, notif=n: self._on_click(notif)
            self.c_layout.insertWidget(self.c_layout.count() - 1, item)

    def _on_click(self, n):
        self.notification_center.mark_read(n.id)
        if n.action:
            n.action()
        self.close()

    def _mark_all_read(self):
        self.notification_center.mark_all_read()
        self.load_notifications()


class NotificationsWindow(QDialog):
    def __init__(self, parent, notification_center, controller):
        super().__init__(parent)
        self.setWindowTitle("Centro Notifiche")
        self.resize(800, 600)
        # Simplified for migration - usually used for full view
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Centro Notifiche Full View (In fase di migrazione)"))
        btn = QPushButton("Chiudi")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
