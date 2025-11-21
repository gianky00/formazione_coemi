import os
import sys
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QByteArray

def get_asset_path(relative_path):
    """
    Resolve path to assets, handling both dev environment and frozen app.
    """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.getcwd()

    return os.path.join(base_path, relative_path)

def load_colored_icon(icon_name, color_hex):
    """
    Loads an SVG icon from the lucide folder and recolors it.
    Replaces 'currentColor' with the provided hex color.
    """
    path = get_asset_path(f"desktop_app/icons/lucide/{icon_name}")

    if not os.path.exists(path):
        return QIcon()

    try:
        with open(path, 'r', encoding='utf-8') as f:
            svg_content = f.read()

        # Replace currentColor
        colored_svg = svg_content.replace("currentColor", color_hex)

        # Create QIcon from bytes
        data = QByteArray(colored_svg.encode('utf-8'))
        pixmap = QPixmap()
        pixmap.loadFromData(data, "SVG")
        return QIcon(pixmap)

    except Exception as e:
        print(f"Error loading icon {icon_name}: {e}")
        return QIcon(path) # Fallback
