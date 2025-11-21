import sys
import os
from PyQt6.QtGui import QImage, QPainter, QColor, QPixmap
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QApplication

def create_assets():
    # QApplication is required to use QPixmap
    app = QApplication(sys.argv)

    # Paths
    # Script is in tools/, so root is ..
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    assets_dir = os.path.join(base_dir, "desktop_app", "assets")
    logo_path = os.path.join(assets_dir, "logo.png")

    if not os.path.exists(logo_path):
        print(f"Error: Logo not found at {logo_path}")
        # Create dummy logo for testing if missing
        # return

    print(f"Generating assets from {logo_path}...")

    # 1. Wizard Image (Side Banner)
    # Inno Setup recommended size for WizardImageFile is 164x314.
    # We create a larger one for better quality on high DPI: 328x628
    wiz_size = QSize(328, 628)
    wiz_img = QImage(wiz_size, QImage.Format.Format_RGB32)
    wiz_img.fill(QColor("#FFFFFF")) # White for professional look

    painter = QPainter(wiz_img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw Logo
    if os.path.exists(logo_path):
        logo = QPixmap(logo_path)
        if not logo.isNull():
            # Scale logo to fit width with margins
            target_width = 260
            scaled_logo = logo.scaledToWidth(target_width, Qt.TransformationMode.SmoothTransformation)

            x = (wiz_size.width() - scaled_logo.width()) // 2
            y = (wiz_size.height() - scaled_logo.height()) // 2
            painter.drawPixmap(x, y, scaled_logo)
    else:
         painter.setPen(QColor("black"))
         painter.drawText(wiz_img.rect(), Qt.AlignmentFlag.AlignCenter, "LOGO MISSING")

    painter.end()
    wiz_path = os.path.join(assets_dir, "installer_wizard.bmp")
    wiz_img.save(wiz_path, "BMP")
    print(f"Created {wiz_path}")

    # 2. Small Image (Header)
    # Inno Setup recommended size for WizardSmallImageFile is 55x55.
    # We use 110x110
    small_size = QSize(110, 110)
    small_img = QImage(small_size, QImage.Format.Format_RGB32)
    small_img.fill(QColor("#FFFFFF")) # White background

    painter = QPainter(small_img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    if os.path.exists(logo_path):
        logo = QPixmap(logo_path)
        if not logo.isNull():
            scaled_logo = logo.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            x = (small_size.width() - scaled_logo.width()) // 2
            y = (small_size.height() - scaled_logo.height()) // 2
            painter.drawPixmap(x, y, scaled_logo)

    painter.end()
    small_path = os.path.join(assets_dir, "installer_small.bmp")
    small_img.save(small_path, "BMP")
    print(f"Created {small_path}")

if __name__ == "__main__":
    create_assets()
