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
        grad.setColorAt(0.0, QColor("#0B0F19")) # Deepest Blue/Black
        grad.setColorAt(0.4, QColor("#111827")) # Slate 900
        grad.setColorAt(1.0, QColor("#1E1B4B")) # Indigo 950
        painter.fillRect(0, 0, width, height, grad)

        # 2. Nebula / Glow Effects (Spectacular!)
        # Large Blue Glow (Bottom Left)
        rad1 = QRadialGradient(0, height, width * 0.8)
        rad1.setColorAt(0.0, QColor(59, 130, 246, 40)) # Blue 500 low opacity
        rad1.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(rad1))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, width, height)

        # Large Purple Glow (Top Right)
        rad2 = QRadialGradient(width, 0, width * 0.7)
        rad2.setColorAt(0.0, QColor(147, 51, 234, 30)) # Purple 600 low opacity
        rad2.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(rad2))
        painter.drawRect(0, 0, width, height)

        # 3. Stars
        random.seed(123)
        painter.setPen(Qt.PenStyle.NoPen)
        for _ in range(100):
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            s = random.uniform(0.5, 2.0)
            opacity = random.randint(50, 200)
            painter.setBrush(QColor(255, 255, 255, opacity))
            painter.drawEllipse(QPointF(x, y), s, s)

    else:
        # White background for Small Image
        painter.fillRect(0, 0, width, height, Qt.GlobalColor.white)

    # 4. Tech Grid (Subtle)
    draw_tech_grid(painter, width, height, is_dark)

    if is_dark:
        # 5. Neural Network (Enhanced)
        draw_neural_network(painter, width, height)

def draw_tech_grid(painter, width, height, is_dark):
    """Draws a subtle hexagonal grid."""
    size = 50
    dx = size * 1.5
    dy = size * math.sqrt(3)

    if is_dark:
        pen = QPen(QColor(255, 255, 255, 5)) # Very faint white
    else:
        pen = QPen(QColor(0, 0, 0, 5)) # Very faint black

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

            # Hexagon
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
    random.seed(42) # Consistent
    num_nodes = int((width * height) / 3000)
    nodes = []

    for _ in range(num_nodes):
        x = random.uniform(0, width)
        y = random.uniform(0, height)
        nodes.append(QPointF(x, y))

    # Connections
    pen = QPen(QColor(147, 197, 253, 30)) # Blue light
    painter.setPen(pen)

    for i, p1 in enumerate(nodes):
        for j, p2 in enumerate(nodes):
            if i >= j: continue
            dist = math.sqrt((p1.x()-p2.x())**2 + (p1.y()-p2.y())**2)
            if dist < 80:
                opacity = int((1 - dist/80) * 80)
                pen.setColor(QColor(147, 197, 253, opacity))
                painter.setPen(pen)
                painter.drawLine(p1, p2)

    # Nodes
    painter.setPen(Qt.PenStyle.NoPen)
    for p in nodes:
        rad = QRadialGradient(p, 4)
        rad.setColorAt(0, QColor(255, 255, 255, 200))
        rad.setColorAt(1, QColor(59, 130, 246, 0))
        painter.setBrush(QBrush(rad))
        painter.drawEllipse(p, 4, 4)

def create_slide(filepath, text, subtext, width=800, height=600, logo_pixmap=None):
    image = QImage(width, height, QImage.Format.Format_ARGB32)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    draw_spectacular_background(painter, width, height, is_dark=True)

    # Logo Watermark
    if logo_pixmap:
        scaled_logo = logo_pixmap.scaledToWidth(120, Qt.TransformationMode.SmoothTransformation)
        painter.setOpacity(0.8)
        painter.drawPixmap(width - 150, 40, scaled_logo)
        painter.setOpacity(1.0)

    # Text Styling
    font_main = QFont("Segoe UI", 56, QFont.Weight.Bold)
    font_sub = QFont("Segoe UI", 28, QFont.Weight.Light)

    # Shadow for text
    painter.setPen(QColor(0, 0, 0, 100))
    painter.setFont(font_main)
    rect_main = painter.fontMetrics().boundingRect(text)
    x_main = (width - rect_main.width()) // 2
    y_main = (height // 2) - 40
    painter.drawText(x_main + 4, y_main + 4, text)

    painter.setPen(QColor(255, 255, 255))
    painter.drawText(x_main, y_main, text)

    # Subtext
    painter.setFont(font_sub)
    painter.setPen(QColor(147, 197, 253))
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

    # Draw Logo in a sleek glass container
    if logo:
        target_w = 200
        scaled = logo.scaledToWidth(target_w, Qt.TransformationMode.SmoothTransformation)
        x = (wiz_size.width() - scaled.width()) // 2
        y = (wiz_size.height() - scaled.height()) // 2

        # Glass backing
        painter.setBrush(QColor(255, 255, 255, 20))
        painter.setPen(QColor(255, 255, 255, 50))
        painter.drawRoundedRect(x - 20, y - 20, scaled.width() + 40, scaled.height() + 40, 15, 15)

        painter.drawPixmap(x, y, scaled)

    painter.end()
    wiz_img.save(os.path.join(assets_dir, "installer_wizard.bmp"), "BMP")

    # 2. Small Image (Top Right) - WHITE BACKGROUND FIX
    # Inno Setup SmallImage is typically 55x55 (standard) but can be larger.
    # The header is white. So we use white background.
    small_size = QSize(55, 55)
    small_img = QImage(small_size, QImage.Format.Format_ARGB32)
    painter = QPainter(small_img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Fill White
    painter.fillRect(small_img.rect(), Qt.GlobalColor.white)

    # Draw Tech Grid (Subtle)
    draw_tech_grid(painter, small_size.width(), small_size.height(), is_dark=False)

    if logo:
        # Draw Logo scaled nicely
        scaled = logo.scaled(45, 45, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        x = (small_size.width() - scaled.width()) // 2
        y = (small_size.height() - scaled.height()) // 2

        # Add a soft shadow to pop from white
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 30))
        painter.drawEllipse(x + 2, y + 4, scaled.width(), scaled.height())

        painter.drawPixmap(x, y, scaled)

    painter.end()
    small_img.save(os.path.join(assets_dir, "installer_small.bmp"), "BMP")

    # 3. Slides
    create_slide(os.path.join(assets_dir, "slide_1.bmp"), "PREDICT", "Advanced Risk Analysis", logo_pixmap=logo)
    create_slide(os.path.join(assets_dir, "slide_2.bmp"), "VALIDATE", "Automated Compliance", logo_pixmap=logo)
    create_slide(os.path.join(assets_dir, "slide_3.bmp"), "AUTOMATE", "Seamless Workflow", logo_pixmap=logo)

if __name__ == "__main__":
    create_assets()
