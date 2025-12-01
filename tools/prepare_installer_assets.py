import sys
import os
import random
import math
from PyQt6.QtGui import QImage, QPainter, QColor, QPixmap, QLinearGradient, QPen, QBrush, QRadialGradient
from PyQt6.QtCore import Qt, QSize, QPointF
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

    # 2. Procedural Neural Network
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

def draw_glow_behind(painter, center_point, radius):
    """Draws a soft white glow behind the logo to improve visibility."""
    glow = QRadialGradient(center_point, radius)
    glow.setColorAt(0, QColor(255, 255, 255, 80))  # White center, semi-transparent
    glow.setColorAt(0.7, QColor(255, 255, 255, 20)) # Fade
    glow.setColorAt(1, QColor(255, 255, 255, 0))   # Transparent edge

    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(glow))
    painter.drawEllipse(center_point, radius, radius)
    painter.restore()

def create_assets():
    # QApplication is required to use QPixmap/QPainter
    app = QApplication(sys.argv)

    # Paths
    # Script is in tools/, so root is ..
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    assets_dir = os.path.join(base_dir, "desktop_app", "assets")
    logo_path = os.path.join(assets_dir, "logo.png")

    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    print(f"Generating Premium Assets from {logo_path}...")

    # --- 1. Wizard Image (Side Banner) ---
    # Size: 328x628 (High DPI)
    wiz_size = QSize(328, 628)
    wiz_img = QImage(wiz_size, QImage.Format.Format_ARGB32)

    painter = QPainter(wiz_img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw Background & Network
    draw_neural_background(painter, wiz_size.width(), wiz_size.height())

    # Draw Logo Centered
    if os.path.exists(logo_path):
        logo = QPixmap(logo_path)
        if not logo.isNull():
            # Scale logo to fit width with margins - Increased for better visibility
            target_width = 260
            scaled_logo = logo.scaledToWidth(target_width, Qt.TransformationMode.SmoothTransformation)

            x = (wiz_size.width() - scaled_logo.width()) // 2
            y = (wiz_size.height() - scaled_logo.height()) // 2

            # Draw Glow
            center = QPointF(x + scaled_logo.width()/2, y + scaled_logo.height()/2)
            radius = max(scaled_logo.width(), scaled_logo.height()) * 0.7
            draw_glow_behind(painter, center, radius)

            # Draw Logo
            painter.drawPixmap(x, y, scaled_logo)
    else:
         painter.setPen(QColor("white"))
         painter.setFont(painter.font()) # Default font
         painter.drawText(wiz_img.rect(), Qt.AlignmentFlag.AlignCenter, "INTELLEO")

    painter.end()

    wiz_path = os.path.join(assets_dir, "installer_wizard.bmp")
    wiz_img.save(wiz_path, "BMP")
    print(f"Created {wiz_path}")


    # --- 2. Small Image (Header) ---
    # Size: 110x110 (High DPI)
    small_size = QSize(110, 110)
    small_img = QImage(small_size, QImage.Format.Format_ARGB32)

    painter = QPainter(small_img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw Background & Network
    draw_neural_background(painter, small_size.width(), small_size.height())

    # Draw Logo
    if os.path.exists(logo_path):
        logo = QPixmap(logo_path)
        if not logo.isNull():
            scaled_logo = logo.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            x = (small_size.width() - scaled_logo.width()) // 2
            y = (small_size.height() - scaled_logo.height()) // 2

            # Draw Glow
            center = QPointF(x + scaled_logo.width()/2, y + scaled_logo.height()/2)
            radius = max(scaled_logo.width(), scaled_logo.height()) * 0.7
            draw_glow_behind(painter, center, radius)

            painter.drawPixmap(x, y, scaled_logo)

    painter.end()
    small_path = os.path.join(assets_dir, "installer_small.bmp")
    small_img.save(small_path, "BMP")
    print(f"Created {small_path}")

if __name__ == "__main__":
    create_assets()
