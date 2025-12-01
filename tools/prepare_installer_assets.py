import sys
import os
import random
import math
from PyQt6.QtGui import QImage, QPainter, QColor, QPixmap, QLinearGradient, QPen, QBrush, QRadialGradient, QPainterPath, QFont
from PyQt6.QtCore import Qt, QSize, QPointF, QRectF
from PyQt6.QtWidgets import QApplication

def draw_neural_background(painter, width, height):
    """
    Draws the 'Deep Space' gradient and a procedural neural network pattern.
    Matches the aesthetic of the LoginView.
    """
    # 1. Deep Space Background Gradient
    # Vertical gradient from Deep Blue to Slate Dark
    grad = QLinearGradient(0, 0, 0, height)
    grad.setColorAt(0, QColor("#1E3A8A")) # Primary Dark Blue
    grad.setColorAt(1, QColor("#0F172A")) # Slate 900
    painter.fillRect(0, 0, width, height, grad)

    # 2. Tech Grid Overlay (Futuristic effect)
    draw_tech_grid(painter, width, height)

    # 3. Procedural Neural Network
    # Use a fixed seed for consistent results across builds
    random.seed(42)

    num_nodes = int((width * height) / 2500) # Density based on area
    nodes = []

    # Generate Nodes
    for _ in range(num_nodes):
        x = random.uniform(0, width)
        y = random.uniform(0, height)
        size = random.uniform(2, 5)
        nodes.append({"pos": QPointF(x, y), "size": size})

    # Draw Connections
    pen = QPen(QColor(255, 255, 255, 30)) # Low opacity white
    pen.setWidthF(0.8)
    painter.setPen(pen)

    connect_dist = 100 # Max distance to connect
    if width < 150: connect_dist = 40 # Adjust for small icons

    for i, node_a in enumerate(nodes):
        for j, node_b in enumerate(nodes):
            if i >= j: continue # Avoid double checking

            # Simple distance check
            dx = node_a["pos"].x() - node_b["pos"].x()
            dy = node_a["pos"].y() - node_b["pos"].y()
            dist = math.sqrt(dx*dx + dy*dy)

            if dist < connect_dist:
                # Calculate opacity based on distance (closer = more opaque)
                opacity = int((1 - dist / connect_dist) * 60)
                pen.setColor(QColor(147, 197, 253, opacity)) # Light Blue tint
                painter.setPen(pen)
                painter.drawLine(node_a["pos"], node_b["pos"])

    # Draw Nodes (Glowing dots)
    painter.setPen(Qt.PenStyle.NoPen)
    for node in nodes:
        # Radial gradient for glow effect
        r = node["size"]
        rad_grad = QRadialGradient(node["pos"], r)
        rad_grad.setColorAt(0, QColor(255, 255, 255, 200)) # Core
        rad_grad.setColorAt(1, QColor(30, 58, 138, 0))   # Fade out

        painter.setBrush(QBrush(rad_grad))
        painter.drawEllipse(node["pos"], r, r)

def draw_tech_grid(painter, width, height):
    """Draws a subtle hexagonal grid for a futuristic look."""
    size = 40
    dx = size * 1.5
    dy = size * math.sqrt(3)

    pen = QPen(QColor(0, 255, 255, 5)) # Very faint Cyan
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

            # Draw Hexagon
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

def draw_white_container(painter, x, y, w, h):
    """Draws a solid white rounded rectangle with shadow behind the logo."""
    padding_x = 30
    padding_y = 20

    rect_x = x - padding_x
    rect_y = y - padding_y
    rect_w = w + padding_x * 2
    rect_h = h + padding_y * 2

    radius = 16

    # Shadow
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(0, 0, 0, 60))
    painter.drawRoundedRect(QRectF(rect_x + 4, rect_y + 6, rect_w, rect_h), radius, radius)

    # White Box
    painter.setBrush(QColor(255, 255, 255, 255)) # Solid White
    painter.drawRoundedRect(QRectF(rect_x, rect_y, rect_w, rect_h), radius, radius)

def create_slide(filepath, text, subtext, width=800, height=600, logo_pixmap=None):
    """Generates a slide image with Deep Space background and text."""
    image = QImage(width, height, QImage.Format.Format_ARGB32)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Background
    draw_neural_background(painter, width, height)

    # Logo (Top Right or Centered Watermark?)
    # Let's put a watermark logo in the corner
    if logo_pixmap:
        scaled_logo = logo_pixmap.scaledToWidth(100, Qt.TransformationMode.SmoothTransformation)
        painter.drawPixmap(width - 130, 30, scaled_logo)

    # Text
    # Center text
    font_main = QFont("Segoe UI", 48, QFont.Weight.Bold)
    font_sub = QFont("Segoe UI", 24, QFont.Weight.Light)

    painter.setPen(QColor(255, 255, 255))
    painter.setFont(font_main)

    # Draw Main Text Centered
    rect_main = painter.fontMetrics().boundingRect(text)
    x_main = (width - rect_main.width()) // 2
    y_main = (height // 2) - 40
    painter.drawText(x_main, y_main, text)

    # Draw Sub Text
    painter.setFont(font_sub)
    painter.setPen(QColor(147, 197, 253)) # Light blue
    rect_sub = painter.fontMetrics().boundingRect(subtext)
    x_sub = (width - rect_sub.width()) // 2
    y_sub = y_main + rect_main.height() + 20
    painter.drawText(x_sub, y_sub, subtext)

    painter.end()
    image.save(filepath, "BMP")
    print(f"Created Slide: {filepath}")


def create_assets():
    # QApplication is required to use QPixmap/QPainter
    app = QApplication(sys.argv)

    # Paths
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    assets_dir = os.path.join(base_dir, "desktop_app", "assets")
    logo_path = os.path.join(assets_dir, "logo.png")

    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    print(f"Generating Premium Assets from {logo_path}...")

    # Load Logo
    logo = None
    if os.path.exists(logo_path):
        logo = QPixmap(logo_path)

    # --- 1. Wizard Image (Side Banner) ---
    wiz_size = QSize(328, 628)
    wiz_img = QImage(wiz_size, QImage.Format.Format_ARGB32)

    painter = QPainter(wiz_img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw Background & Network
    draw_neural_background(painter, wiz_size.width(), wiz_size.height())

    # Draw Logo Centered
    if logo and not logo.isNull():
        target_width = 240
        scaled_logo = logo.scaledToWidth(target_width, Qt.TransformationMode.SmoothTransformation)

        x = (wiz_size.width() - scaled_logo.width()) // 2
        y = (wiz_size.height() - scaled_logo.height()) // 2

        draw_white_container(painter, x, y, scaled_logo.width(), scaled_logo.height())
        painter.drawPixmap(x, y, scaled_logo)
    else:
         painter.setPen(QColor("white"))
         painter.setFont(painter.font())
         painter.drawText(wiz_img.rect(), Qt.AlignmentFlag.AlignCenter, "INTELLEO")

    painter.end()

    wiz_path = os.path.join(assets_dir, "installer_wizard.bmp")
    wiz_img.save(wiz_path, "BMP")
    print(f"Created {wiz_path}")


    # --- 2. Small Image (Header) ---
    small_size = QSize(110, 110)
    small_img = QImage(small_size, QImage.Format.Format_ARGB32)

    painter = QPainter(small_img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw Background & Network
    draw_neural_background(painter, small_size.width(), small_size.height())

    # Draw Logo
    if logo and not logo.isNull():
        scaled_logo = logo.scaled(70, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        x = (small_size.width() - scaled_logo.width()) // 2
        y = (small_size.height() - scaled_logo.height()) // 2

        padding = 10
        rect_size = max(scaled_logo.width(), scaled_logo.height()) + padding * 2
        cx = x + scaled_logo.width() / 2
        cy = y + scaled_logo.height() / 2

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 60))
        painter.drawEllipse(QPointF(cx+2, cy+3), rect_size/2, rect_size/2)

        painter.setBrush(QColor(255, 255, 255, 255))
        painter.drawEllipse(QPointF(cx, cy), rect_size/2, rect_size/2)

        painter.drawPixmap(x, y, scaled_logo)

    painter.end()
    small_path = os.path.join(assets_dir, "installer_small.bmp")
    small_img.save(small_path, "BMP")
    print(f"Created {small_path}")

    # --- 3. Slideshow Images ---
    # We create 3 slides with the Deep Space theme
    # Slide 1: PREDICT
    create_slide(
        os.path.join(assets_dir, "slide_1.bmp"),
        "PREDICT",
        "AI-Powered Risk Analysis",
        width=800, height=600, logo_pixmap=logo
    )
    # Slide 2: VALIDATE
    create_slide(
        os.path.join(assets_dir, "slide_2.bmp"),
        "VALIDATE",
        "Automated Compliance Checks",
        width=800, height=600, logo_pixmap=logo
    )
    # Slide 3: AUTOMATE
    create_slide(
        os.path.join(assets_dir, "slide_3.bmp"),
        "AUTOMATE",
        "Seamless Workflow Integration",
        width=800, height=600, logo_pixmap=logo
    )

if __name__ == "__main__":
    create_assets()
