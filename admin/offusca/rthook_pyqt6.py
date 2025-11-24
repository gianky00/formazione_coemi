# rthook_pyqt6.py
# Runtime hook per PyInstaller + PyArmor + PyQt6 WebEngine
# Forza il caricamento delle DLL prima dell'esecuzione del codice offuscato.

import sys
import os

def _force_load_qt_modules():
    try:
        # Import espliciti per forzare PyInstaller a caricare i binari
        import PyQt6.QtWebEngineWidgets
        import PyQt6.QtWebEngineCore
        import PyQt6.QtWebChannel
        import PyQt6.QtNetwork
        import PyQt6.QtPrintSupport
    except ImportError as e:
        # Ignora errori in fase di hook, verranno gestiti dal main se bloccanti
        pass

_force_load_qt_modules()