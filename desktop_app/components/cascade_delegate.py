from PyQt6.QtWidgets import QStyledItemDelegate
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QColor, QPainter

class CascadeDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_time = QTime.currentTime()
        self.delay_per_row = 30 # ms
        self.fade_duration = 300 # ms
        self.is_animating = False

    def start_animation(self):
        self.start_time = QTime.currentTime()
        self.is_animating = True

    def prepare_painter(self, painter, index):
        """Applies opacity to painter based on animation state. Returns True if visible."""
        if self.is_animating:
            elapsed = self.start_time.msecsTo(QTime.currentTime())
            row_start = index.row() * self.delay_per_row

            if elapsed < row_start:
                return False # Not visible yet

            progress = (elapsed - row_start) / self.fade_duration
            opacity = min(1.0, max(0.0, progress))

            painter.setOpacity(opacity)
        return True

    def paint(self, painter, option, index):
        painter.save()
        if self.prepare_painter(painter, index):
             super().paint(painter, option, index)
        painter.restore()
