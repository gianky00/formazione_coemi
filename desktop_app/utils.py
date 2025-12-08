import os
import sys
import uuid
import re
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QByteArray, QObject, pyqtSignal
from desktop_app.services.license_manager import LicenseManager

class GlobalLoading(QObject):
    _instance = None
    loading_changed = pyqtSignal(bool)

    @staticmethod
    def instance():
        if not GlobalLoading._instance:
            GlobalLoading._instance = GlobalLoading()
        return GlobalLoading._instance

    @staticmethod
    def start():
        GlobalLoading.instance().loading_changed.emit(True)

    @staticmethod
    def stop():
        GlobalLoading.instance().loading_changed.emit(False)

def get_device_id():
    """
    Retrieves the device fingerprint.
    Tries to read 'Hardware ID' from the encrypted license file.
    Falls back to MAC address (uuid.getnode()) if file not found.
    """
    try:
        data = LicenseManager.get_license_data()
        if data and "Hardware ID" in data:
            return data["Hardware ID"]
    except Exception:
        pass

    # Fallback
    return str(uuid.getnode())

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
        # Bug 5 Fix: Return empty QIcon if path is bad, avoiding crashes with invalid paths
        if os.path.exists(path):
             return QIcon(path)
        return QIcon()

def clean_text_for_display(text: str) -> str:
    """
    Removes phonetic stress accents for visual display while preserving
    standard Italian grammatical accents at the end of words.

    Logic:
    - Always removes acute phonetic markers (á, í, ú).
    - Removes internal stress accents (ò, è, à, ì, ù) only if they are inside a word.
    - Preserves Markdown formatting (e.g., _città_) by excluding '_' from the "inside word" check.
    """
    # 1. Always replace acute accents on a, i, u (Phonetic stress markers)
    # S6397: Replaced character class [x] with x
    # S5361: Replaced re.sub with str.replace for simple replacements
    text = text.replace('á', 'a')
    text = text.replace('í', 'i')
    text = text.replace('ú', 'u')

    # Regex lookahead (?=[^\W_]) ensures the character is followed by a word character
    # that is NOT an underscore. This prevents stripping accents before a Markdown underscore.

    # 2. Replace accented o/e ONLY if they are inside a word
    text = re.sub(r'[òó](?=[^\W_])', 'o', text)
    text = re.sub(r'[èé](?=[^\W_])', 'e', text)

    # 3. Also clean other accents inside words if used for stress (e.g. càsa)
    # S6397: Replaced character class
    text = re.sub(r'à(?=[^\W_])', 'a', text)
    text = re.sub(r'ì(?=[^\W_])', 'i', text)
    text = re.sub(r'ù(?=[^\W_])', 'u', text)

    return text
