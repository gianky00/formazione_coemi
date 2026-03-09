import math
import os
import random
import sys

from PySide6.QtCore import QPointF, QRect, QRectF, QSize, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import QApplication


def draw_spectacular_background(painter, width, height, is_dark=True):
    """
    Draws a 'Breathtaking' Deep Space background with nebulae, stars, and a tech grid.
    """
    if is_dark:
        # 1. Deep Space Base
        grad = QLinearGradient(0, 0, width, height)
        grad.setColorAt(0.0, QColor("#050A14"))
        grad.setColorAt(0.5, QColor("#0F172A"))
        grad.setColorAt(1.0, QColor("#172554"))
        painter.fillRect(0, 0, width, height, grad)

        # 2. Nebula / Glow Effects
        rad1 = QRadialGradient(width * 0.2, height * 0.8, width * 0.9)
        rad1.setColorAt(0.0, QColor(29, 78, 216, 50))
        rad1.setColorAt(0.5, QColor(30, 64, 175, 20))
        rad1.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(rad1))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, width, height)

        rad2 = QRadialGradient(width * 0.9, height * 0.2, width * 0.8)
        rad2.setColorAt(0.0, QColor(126, 34, 206, 40))
        rad2.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(rad2))
        painter.drawRect(0, 0, width, height)

        rad3 = QRadialGradient(width * 0.5, height * 0.5, width * 0.6)
        rad3.setColorAt(0.0, QColor(6, 182, 212, 15))
        rad3.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(rad3))
        painter.drawRect(0, 0, width, height)

        # 3. Stars
        random.seed(999)
        painter.setPen(Qt.NoPen)
        for _ in range(150):
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            s = random.uniform(0.5, 2.5)
            opacity = random.randint(100, 255)
            painter.setBrush(
                QColor(147, 197, 253, opacity)
                if random.random() > 0.8
                else QColor(255, 255, 255, opacity)
            )
            painter.drawEllipse(QPointF(x, y), s, s)
    else:
        painter.fillRect(0, 0, width, height, Qt.white)

    draw_tech_grid(painter, width, height, is_dark)
    if is_dark:
        draw_neural_network(painter, width, height)


def draw_tech_grid(painter, width, height, is_dark):
    size = 45
    dx, dy = size * 1.5, size * math.sqrt(3)
    pen = QPen(QColor(255, 255, 255, 8)) if is_dark else QPen(QColor(0, 0, 0, 8))
    pen.setWidth(1)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)
    cols, rows = int(width / dx) + 2, int(height / dy) + 2
    for i in range(cols):
        for j in range(rows):
            x, y = i * dx, j * dy
            if i % 2 == 1:
                y += dy / 2
            _draw_hexagon(painter, x, y, size)


def _draw_hexagon(painter, x, y, size):
    path = QPainterPath()
    for k in range(6):
        angle_rad = math.pi / 180 * (60 * k)
        px, py = x + size * math.cos(angle_rad), y + size * math.sin(angle_rad)
        if k == 0:
            path.moveTo(px, py)
        else:
            path.lineTo(px, py)
    path.closeSubpath()
    painter.drawPath(path)


def draw_neural_network(painter, width, height):
    random.seed(55)
    nodes = [
        QPointF(random.uniform(0, width), random.uniform(0, height))
        for _ in range(int((width * height) / 3500))
    ]
    pen = QPen(QColor(56, 189, 248, 40))
    painter.setPen(pen)
    for i, p1 in enumerate(nodes):
        for j, p2 in enumerate(nodes):
            if i >= j:
                continue
            dist = math.sqrt((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2)
            if dist < 90:
                pen.setColor(QColor(56, 189, 248, int((1 - dist / 90) * 90)))
                painter.setPen(pen)
                painter.drawLine(p1, p2)
    painter.setPen(Qt.NoPen)
    for p in nodes:
        rad = QRadialGradient(p, 5)
        rad.setColorAt(0, QColor(255, 255, 255, 220))
        rad.setColorAt(1, QColor(14, 165, 233, 0))
        painter.setBrush(QBrush(rad))
        painter.drawEllipse(p, 5, 5)


def create_slide(filepath, text, subtext, width=800, height=600, logo_pixmap=None):
    image = QImage(width, height, QImage.Format_ARGB32)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)
    draw_spectacular_background(painter, width, height, is_dark=True)
    if logo_pixmap:
        scaled = logo_pixmap.scaledToWidth(140, Qt.SmoothTransformation)
        margin = 40
        x, y = width - margin - scaled.width(), margin
        box = QRectF(x - 15, y - 15, scaled.width() + 30, scaled.height() + 30)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 80))
        painter.drawRoundedRect(box.translated(4, 4), 15, 15)
        painter.setBrush(Qt.white)
        painter.drawRoundedRect(box, 15, 15)
        painter.drawPixmap(x, y, scaled)

    center_y = height // 2
    painter.setFont(QFont("Segoe UI", 48, QFont.Bold))
    rect_main = QRect(40, center_y - 120, width - 80, 240)
    painter.setPen(QColor(0, 0, 0, 150))
    painter.drawText(rect_main.translated(4, 4), Qt.AlignCenter | Qt.TextWordWrap, text)
    painter.setPen(Qt.white)
    painter.drawText(rect_main, Qt.AlignCenter | Qt.TextWordWrap, text)

    painter.setFont(QFont("Segoe UI", 24, QFont.Light))
    painter.setPen(QColor(125, 211, 252))
    rect_sub = QRect(40, center_y + 80, width - 80, 100)
    painter.drawText(rect_sub, Qt.AlignCenter | Qt.TextWordWrap, subtext)
    painter.end()
    image.save(filepath, "BMP")


def create_assets():
    _ = QApplication(sys.argv)
    assets_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "desktop_app", "assets")
    )
    os.makedirs(assets_dir, exist_ok=True)
    logo_path = os.path.join(assets_dir, "logo.png")
    logo = QPixmap(logo_path) if os.path.exists(logo_path) else None

    wiz_size = QSize(328, 628)
    wiz_img = QImage(wiz_size, QImage.Format_ARGB32)
    p = QPainter(wiz_img)
    p.setRenderHint(QPainter.Antialiasing)
    draw_spectacular_background(p, wiz_size.width(), wiz_size.height(), is_dark=True)
    if logo:
        scaled = logo.scaledToWidth(220, Qt.SmoothTransformation)
        x, y = (wiz_size.width() - scaled.width()) // 2, (wiz_size.height() - scaled.height()) // 2
        p.setBrush(QColor(0, 0, 0, 80))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(x - 20 + 4, y - 20 + 6, scaled.width() + 40, scaled.height() + 40, 20, 20)
        p.setBrush(Qt.white)
        p.drawRoundedRect(x - 20, y - 20, scaled.width() + 40, scaled.height() + 40, 20, 20)
        p.drawPixmap(x, y, scaled)
    p.end()
    wiz_img.save(os.path.join(assets_dir, "installer_wizard.bmp"), "BMP")

    small_size = QSize(150, 57)
    small_img = QImage(small_size, QImage.Format_ARGB32)
    p = QPainter(small_img)
    p.fillRect(small_img.rect(), Qt.white)
    draw_tech_grid(p, small_size.width(), small_size.height(), is_dark=False)
    if logo:
        scaled = logo.scaled(
            small_size.width() - 10,
            small_size.height() - 10,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        p.drawPixmap(
            (small_size.width() - scaled.width()) // 2,
            (small_size.height() - scaled.height()) // 2,
            scaled,
        )
    p.end()
    small_img.save(os.path.join(assets_dir, "installer_small.bmp"), "BMP")

    slides = [
        ("slide_1.bmp", "INTELLIGENZA ARTIFICIALE", "Supporto all'Estrazione Dati"),
        ("slide_2.bmp", "SCADENZARIO", "Monitoraggio Scadenze"),
        ("slide_3.bmp", "VALIDAZIONE DATI", "Controllo Conformità"),
    ]
    for f, t, s in slides:
        create_slide(os.path.join(assets_dir, f), t, s, logo_pixmap=logo)


if __name__ == "__main__":
    create_assets()
