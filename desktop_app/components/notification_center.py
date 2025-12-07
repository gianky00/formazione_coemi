from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea,
                             QPushButton, QHBoxLayout, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QBrush
from datetime import datetime

from .toast import ToastManager
from ..utils import load_colored_icon

class NotificationItem(QFrame):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setObjectName("notification_item")
        self.data = data # Store for smart refresh comparison

        # Styles
        colors = {
            "success": "#10B981", # Green
            "error": "#EF4444",   # Red
            "warning": "#F59E0B", # Yellow
            "info": "#3B82F6"     # Blue
        }
        accent_color = colors.get(data.get("type", "info"), colors["info"])

        self.setStyleSheet(f"""
            QFrame#notification_item {{
                background-color: #FFFFFF;
                border-bottom: 1px solid #F3F4F6;
                border-radius: 4px;
            }}
            QFrame#notification_item:hover {{
                background-color: #F9FAFB;
            }}
            QLabel#title {{
                font-weight: bold;
                font-size: 13px;
                color: #1F2937;
            }}
            QLabel#message {{
                font-size: 12px;
                color: #6B7280;
            }}
            QLabel#time {{
                font-size: 10px;
                color: #9CA3AF;
            }}
            QWidget#accent {{
                background-color: {accent_color};
                border-radius: 2px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Accent dot or strip
        accent = QWidget()
        accent.setObjectName("accent")
        accent.setFixedSize(4, 30)
        layout.addWidget(accent)

        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)

        # Header (Title + Time)
        header_layout = QHBoxLayout()
        title_lbl = QLabel(data.get("title", ""))
        title_lbl.setObjectName("title")
        header_layout.addWidget(title_lbl)

        header_layout.addStretch()

        ts_str = data.get("timestamp")
        time_str = ""
        if ts_str:
            try:
                if isinstance(ts_str, str):
                    dt = datetime.fromisoformat(ts_str)
                    # Convert to local time for display
                    time_str = dt.astimezone().strftime("%H:%M")
                elif isinstance(ts_str, datetime):
                    time_str = ts_str.strftime("%H:%M")
            except Exception: # S5754: Handle exception
                pass # Use empty string for time if parsing fails

        time_lbl = QLabel(time_str)
        time_lbl.setObjectName("time")
        header_layout.addWidget(time_lbl)

        content_layout.addLayout(header_layout)

        msg_lbl = QLabel(data.get("message", ""))
        msg_lbl.setObjectName("message")
        msg_lbl.setWordWrap(True)
        content_layout.addWidget(msg_lbl)

        layout.addLayout(content_layout)

class NotificationCenter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(320)
        self.setFixedHeight(400)

        # Drop shadow and border
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(50)
        header.setStyleSheet("border-bottom: 1px solid #E5E7EB; background-color: #F9FAFB; border-top-left-radius: 8px; border-top-right-radius: 8px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)

        title = QLabel("Notifiche")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #111827; border: none; background: transparent;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        clear_btn = QPushButton("Cancella tutto")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet("""
            QPushButton {
                color: #6B7280;
                font-size: 12px;
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                color: #EF4444;
                text-decoration: underline;
            }
        """)
        clear_btn.clicked.connect(self.clear_all)
        header_layout.addWidget(clear_btn)

        layout.addWidget(header)

        # List Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area)

        # Empty State
        self.empty_label = QLabel("Nessuna notifica")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #9CA3AF; margin-top: 20px; border: none; background: transparent;")

        # Connect to manager
        ToastManager.instance().history_updated.connect(self.refresh)

        self.refresh()

    def clear_layout(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def refresh(self):
        # Bug 9: Smart Scroll / Refresh
        history = ToastManager.instance().history

        if not history:
            self.clear_layout()
            self.container_layout.addWidget(self.empty_label)
            self.empty_label.show()
            return

        # Ensure empty label is removed
        if self.empty_label.parent() == self.container:
             self.empty_label.setParent(None)
             self.container_layout.removeWidget(self.empty_label)
             self.empty_label.hide()

        # Update items
        for i, data in enumerate(history):
            # Get existing widget at this index
            # Note: layout itemAt includes spacers if any, but we only add widgets.
            item = self.container_layout.itemAt(i)
            widget = item.widget() if item else None

            # Check if match
            if isinstance(widget, NotificationItem) and widget.data == data:
                continue

            # If mismatch or missing, insert new
            # If there was a widget here but it didn't match, we insert BEFORE it?
            # Or we assume history insertion order is consistent.
            # History is [Newest, ..., Oldest].
            # If we inserted a new item at 0, everything shifts down.

            new_item = NotificationItem(data)
            self.container_layout.insertWidget(i, new_item)

        # Remove excess
        while self.container_layout.count() > len(history):
            item = self.container_layout.takeAt(len(history))
            if item.widget():
                item.widget().deleteLater()

    def clear_all(self):
        ToastManager.instance().history.clear()
        ToastManager.instance().save_history() # Ensure clear is persisted
        ToastManager.instance().history_updated.emit()

    def paintEvent(self, event):
        # Draw shadow
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Use stylesheet for simplicity, but if needed custom paint here
        super().paintEvent(event)
