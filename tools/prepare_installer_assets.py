import sys
import os
import random
import math
from PyQt6.QtGui import QImage, QPainter, QColor, QPixmap, QLinearGradient, QPen, QBrush, QRadialGradient, QPainterPath, QFont, QConicalGradient
from PyQt6.QtCore import Qt, QSize, QPointF, QRectF
from PyQt6.QtWidgets import QApplication

def draw_spectacular_background(painter, width, height, is_dark=True):
    """
    Draws a 'Breathtaking' Deep Space background with nebulae, stars, and a tech grid.
    """
    if is_dark:
        # 1. Deep Space Base
        grad = QLinearGradient(0, 0, width, height)
        grad.setColorAt(0.0, QColor("#050A14")) # Almost Black Blue
        grad.setColorAt(0.5, QColor("#0F172A")) # Slate 900
        grad.setColorAt(1.0, QColor("#172554")) # Blue 950
        painter.fillRect(0, 0, width, height, grad)

        # 2. Nebula / Glow Effects (Enhanced)
        # Intense Blue Core
        rad1 = QRadialGradient(width * 0.2, height * 0.8, width * 0.9)
        rad1.setColorAt(0.0, QColor(29, 78, 216, 50)) # Blue 700
        rad1.setColorAt(0.5, QColor(30, 64, 175, 20))
        rad1.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(rad1))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, width, height)

        # Cosmic Purple/Pink Highlight
        rad2 = QRadialGradient(width * 0.9, height * 0.2, width * 0.8)
        rad2.setColorAt(0.0, QColor(126, 34, 206, 40)) # Purple 700
        rad2.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(rad2))
        painter.drawRect(0, 0, width, height)

        # Cyan Tech Glow (Center)
        rad3 = QRadialGradient(width * 0.5, height * 0.5, width * 0.6)
        rad3.setColorAt(0.0, QColor(6, 182, 212, 15)) # Cyan 500
        rad3.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(rad3))
        painter.drawRect(0, 0, width, height)

        # 3. Stars & Particles
        random.seed(999)
        painter.setPen(Qt.PenStyle.NoPen)
        for _ in range(150):
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            s = random.uniform(0.5, 2.5)
            opacity = random.randint(100, 255)
            # Some stars are blueish, some white
            if random.random() > 0.8:
                painter.setBrush(QColor(147, 197, 253, opacity))
            else:
                painter.setBrush(QColor(255, 255, 255, opacity))
            painter.drawEllipse(QPointF(x, y), s, s)

    else:
        # White background for Small Image
        painter.fillRect(0, 0, width, height, Qt.GlobalColor.white)

    # 4. Tech Grid
    draw_tech_grid(painter, width, height, is_dark)

    if is_dark:
        # 5. Neural Network
        draw_neural_network(painter, width, height)

def draw_tech_grid(painter, width, height, is_dark):
    """Draws a subtle hexagonal grid."""
    size = 45
    dx = size * 1.5
    dy = size * math.sqrt(3)

    if is_dark:
        pen = QPen(QColor(255, 255, 255, 8))
    else:
        pen = QPen(QColor(0, 0, 0, 8))

    pen.setWidth(1)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    cols = int(width / dx) + 2
    rows = int(height / dy) + 2

    for i in range(cols):
        for j in range(rows):
            x = i * dx
            y = j * dy
            if i % 2 == 1:
                y += dy / 2

            path = QPainterPath()
            for k in range(6):
                angle_deg = 60 * k
                angle_rad = math.pi / 180 * angle_deg
                px = x + size * math.cos(angle_rad)
                py = y + size * math.sin(angle_rad)
                if k == 0:
                    path.moveTo(px, py)
                else:
                    path.lineTo(px, py)
            path.closeSubpath()
            painter.drawPath(path)

def draw_neural_network(painter, width, height):
    """Draws glowing nodes and connections."""
    random.seed(55)
    num_nodes = int((width * height) / 3500)
    nodes = []

    for _ in range(num_nodes):
        x = random.uniform(0, width)
        y = random.uniform(0, height)
        nodes.append(QPointF(x, y))

    # Connections
    pen = QPen(QColor(56, 189, 248, 40)) # Light Blue
    painter.setPen(pen)

    for i, p1 in enumerate(nodes):
        for j, p2 in enumerate(nodes):
            if i >= j: continue
            dist = math.sqrt((p1.x()-p2.x())**2 + (p1.y()-p2.y())**2)
            if dist < 90:
                opacity = int((1 - dist/90) * 90)
                pen.setColor(QColor(56, 189, 248, opacity))
                painter.setPen(pen)
                painter.drawLine(p1, p2)

    # Nodes
    painter.setPen(Qt.PenStyle.NoPen)
    for p in nodes:
        rad = QRadialGradient(p, 5)
        rad.setColorAt(0, QColor(255, 255, 255, 220))
        rad.setColorAt(1, QColor(14, 165, 233, 0)) # Sky 500
        painter.setBrush(QBrush(rad))
        painter.drawEllipse(p, 5, 5)

def create_slide(filepath, text, subtext, width=800, height=600, logo_pixmap=None):
    image = QImage(width, height, QImage.Format.Format_ARGB32)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    draw_spectacular_background(painter, width, height, is_dark=True)

    # Logo Watermark
    if logo_pixmap:
        scaled_logo = logo_pixmap.scaledToWidth(140, Qt.TransformationMode.SmoothTransformation)
        painter.setOpacity(0.9)
        painter.drawPixmap(width - 160, 40, scaled_logo)
        painter.setOpacity(1.0)

    # Text Styling
    font_main = QFont("Segoe UI", 52, QFont.Weight.Bold)
    font_sub = QFont("Segoe UI", 26, QFont.Weight.Light)

    # Shadow for text
    painter.setPen(QColor(0, 0, 0, 150))
    painter.setFont(font_main)
    rect_main = painter.fontMetrics().boundingRect(text)
    x_main = (width - rect_main.width()) // 2
    y_main = (height // 2) - 40
    painter.drawText(x_main + 4, y_main + 4, text)

    # Main Text (White with subtle cyan glow)
    painter.setPen(QColor(255, 255, 255))
    painter.drawText(x_main, y_main, text)

    # Subtext
    painter.setFont(font_sub)
    painter.setPen(QColor(125, 211, 252)) # Light sky blue
    rect_sub = painter.fontMetrics().boundingRect(subtext)
    x_sub = (width - rect_sub.width()) // 2
    y_sub = y_main + rect_main.height() + 20
    painter.drawText(x_sub, y_sub, subtext)

    painter.end()
    image.save(filepath, "BMP")
    print(f"Created {filepath}")

def create_assets():
    app = QApplication(sys.argv)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    assets_dir = os.path.join(base_dir, "desktop_app", "assets")
    logo_path = os.path.join(assets_dir, "logo.png")

    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    logo = None
    if os.path.exists(logo_path):
        logo = QPixmap(logo_path)

    # 1. Wizard Image (Large Side)
    wiz_size = QSize(328, 628)
    wiz_img = QImage(wiz_size, QImage.Format.Format_ARGB32)
    painter = QPainter(wiz_img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    draw_spectacular_background(painter, wiz_size.width(), wiz_size.height(), is_dark=True)

    # Logo with SOLID WHITE background for contrast
    if logo:
        target_w = 220
        scaled = logo.scaledToWidth(target_w, Qt.TransformationMode.SmoothTransformation)
        x = (wiz_size.width() - scaled.width()) // 2
        y = (wiz_size.height() - scaled.height()) // 2

        # Solid White Box with Rounded Corners
        painter.setBrush(QColor(255, 255, 255, 255))
        painter.setPen(Qt.PenStyle.NoPen)
        # Add shadow
        painter.setBrush(QColor(0, 0, 0, 80))
        painter.drawRoundedRect(x - 20 + 4, y - 20 + 6, scaled.width() + 40, scaled.height() + 40, 20, 20)
        # White Box
        painter.setBrush(QColor(255, 255, 255, 255))
        painter.drawRoundedRect(x - 20, y - 20, scaled.width() + 40, scaled.height() + 40, 20, 20)

        painter.drawPixmap(x, y, scaled)

    painter.end()
    wiz_img.save(os.path.join(assets_dir, "installer_wizard.bmp"), "BMP")

    # 2. Small Image (Header) - LARGER SIZE
    # Increased size for visibility
    small_size = QSize(150, 57)
    small_img = QImage(small_size, QImage.Format.Format_ARGB32)
    painter = QPainter(small_img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    # Fill White
    painter.fillRect(small_img.rect(), Qt.GlobalColor.white)

    # Draw Tech Grid (Very Subtle)
    draw_tech_grid(painter, small_size.width(), small_size.height(), is_dark=False)

    if logo:
        # Maximize logo within the new size
        # Keep aspect ratio, margin 5px
        scaled = logo.scaled(small_size.width() - 10, small_size.height() - 10, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        x = (small_size.width() - scaled.width()) // 2
        y = (small_size.height() - scaled.height()) // 2

        painter.drawPixmap(x, y, scaled)

    painter.end()
    small_img.save(os.path.join(assets_dir, "installer_small.bmp"), "BMP")

    # 3. Slides (Italian & Expanded)
    slides_data = [
        ("slide_1.bmp", "INTELLIGENZA ARTIFICIALE", "Analisi Documentale con Gemini Pro"),
        ("slide_2.bmp", "SCADENZARIO PREDITTIVO", "Anticipa le Scadenze Critiche"),
        ("slide_3.bmp", "VALIDAZIONE DATI", "Controllo Conformità Automatizzato"),
        ("slide_4.bmp", "CLOUD SICURO", "Crittografia AES-256 e Backup"),
        ("slide_5.bmp", "NOTIFICHE SMART", "Report Periodici e Alert Email"),
        ("slide_6.bmp", "AUTOMAZIONE TOTALE", "Efficienza Operativa Massimizzata")
    ]

    for filename, title, subtitle in slides_data:
        create_slide(os.path.join(assets_dir, filename), title, subtitle, logo_pixmap=logo)

if __name__ == "__main__":
    create_assets()
