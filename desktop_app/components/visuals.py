from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QPen, QBrush, QFont
import random
import math

class HolographicScanner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(150)
        self.scan_line_y = 0
        self.scan_direction = 1
        self.particles = [] # Extracted keywords

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

    def animate(self):
        # Move Scan Line
        self.scan_line_y += 2
        if self.scan_line_y > 100:
            self.scan_line_y = 0
            self._emit_particles()

        # Move particles (Bezier curve to database?)
        # Simple linear for now
        target_x = self.width() - 60
        target_y = 60

        for p in self.particles:
            # Move towards target
            dx = target_x - p['x']
            dy = target_y - p['y']
            dist = math.sqrt(dx*dx + dy*dy)

            if dist > 5:
                p['x'] += (dx / dist) * 8
                p['y'] += (dy / dist) * 8
            else:
                p['life'] = 0 # Arrived

            # p['life'] -= 0.01

        self.particles = [p for p in self.particles if p['life'] > 0]
        self.update()

    def _emit_particles(self):
        if random.random() < 0.5:
            self.particles.append({
                'x': 55,
                'y': 20 + self.scan_line_y,
                'life': 1.0,
                'text': random.choice(["NOME", "DATA", "CF", "DOC"])
            })

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive(): return
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Draw Document Outline (Left)
        doc_x = 20
        doc_y = 20
        doc_w = 70
        doc_h = 100
        doc_rect = QRectF(doc_x, doc_y, doc_w, doc_h)

        painter.setPen(QPen(QColor("#3B82F6"), 2))
        painter.setBrush(QBrush(QColor(59, 130, 246, 30)))
        painter.drawRect(doc_rect)

        # Fake Text Lines
        painter.setPen(QPen(QColor("#3B82F6"), 1))
        for i in range(30, 110, 10):
            painter.drawLine(doc_x + 10, i, doc_x + 60, i)

        # 2. Scan Line
        scan_y = doc_y + self.scan_line_y
        painter.setPen(QPen(QColor("#EF4444"), 2)) # Red Laser
        painter.drawLine(QPointF(doc_x, scan_y), QPointF(doc_x + doc_w, scan_y))

        # Laser Glow
        grad = QLinearGradient(doc_x, scan_y, doc_x + doc_w, scan_y)
        grad.setColorAt(0, QColor(255, 0, 0, 0))
        grad.setColorAt(0.5, QColor(255, 0, 0, 200))
        grad.setColorAt(1, QColor(255, 0, 0, 0))
        painter.fillRect(QRectF(doc_x, scan_y - 2, doc_w, 4), grad)

        # 3. Database Target (Right)
        db_x = self.width() - 90
        db_y = 20

        painter.setPen(QPen(QColor("#10B981"), 2))
        painter.setBrush(QBrush(QColor(16, 185, 129, 30)))

        # Draw Database Cylinders
        path = QRectF(db_x, db_y, 60, 80)
        painter.drawRoundedRect(path, 5, 5)
        painter.drawLine(db_x, db_y + 20, db_x + 60, db_y + 20)
        painter.drawLine(db_x, db_y + 40, db_x + 60, db_y + 40)
        painter.drawLine(db_x, db_y + 60, db_x + 60, db_y + 60)

        # 4. Particles (Flying Data)
        font = QFont("Inter", 9, QFont.Weight.Bold)
        painter.setFont(font)

        for p in self.particles:
            # Use Dark Blue for visibility on light background
            painter.setPen(QColor("#1E3A8A"))
            painter.drawText(QPointF(p['x'], p['y']), p['text'])
