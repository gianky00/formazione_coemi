from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea,
                             QPushButton, QHBoxLayout, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QBrush

from .toast import ToastManager
from ..utils import load_colored_icon

class NotificationItem(QFrame):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setObjectName("notification_item")

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

        ts = data.get("timestamp")
        time_str = ts.strftime("%H:%M") if ts else ""
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
        self.container_layout.addWidget(self.empty_label)
        self.empty_label.hide()

        # Connect to manager
        ToastManager.instance().history_updated.connect(self.refresh)

        self.refresh()

    def refresh(self):
        # Clear existing
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        history = ToastManager.instance().history

        if not history:
            self.container_layout.addWidget(self.empty_label)
            self.empty_label.show()
            return

        self.empty_label.hide()
        for data in history:
            item = NotificationItem(data)
            self.container_layout.addWidget(item)

    def clear_all(self):
        ToastManager.instance().history.clear()
        ToastManager.instance().history_updated.emit()

    def paintEvent(self, event):
        # Draw shadow
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Use stylesheet for simplicity, but if needed custom paint here
        super().paintEvent(event)
