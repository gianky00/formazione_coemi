import os
import sys

# Fix for PyQt6 DLL search path on Windows (Python 3.8+)
# This ensures that nested Qt binaries (like Qt6WebEngineCore.dll) can find their dependencies
# (like Qt6Core.dll) which might be in a parent or sibling directory within the frozen bundle.

if sys.platform == 'win32':
    try:
        # _MEIPASS is the temp directory where PyInstaller extracts files
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Common paths where PyQt6 binaries might reside in a PyInstaller bundle
    qt6_paths = [
        os.path.join(base_path, 'PyQt6'),
        os.path.join(base_path, 'PyQt6', 'Qt6', 'bin'),
        os.path.join(base_path, 'PyQt6', 'Qt', 'bin'),
    ]

    for path in qt6_paths:
        if os.path.exists(path):
            try:
                os.add_dll_directory(path)
            except Exception:
                pass
