# rthook_pyqt6.py
# Runtime hook per PyInstaller + PyArmor + PyQt6 WebEngine
# Questo file forza il caricamento dei moduli prima che venga eseguito il codice offuscato.

import sys
import os

def _force_load_qt_modules():
    """
    Forza l'importazione dei moduli QtWebEngine.
    Questo è necessario perché PyArmor nasconde gli import a PyInstaller,
    e senza questo pre-caricamento l'exe non trova la DLL/modulo.
    """
    try:
        # Tenta di importare i moduli critici
        import PyQt6.QtWebEngineWidgets
        import PyQt6.QtWebEngineCore
        import PyQt6.QtWebChannel
        import PyQt6.QtNetwork
        import PyQt6.QtPrintSupport
        
        # Opzionale: Log per debug (se lanciato con console)
        # print("DEBUG: PyQt6 WebEngine modules pre-loaded successfully.")
    except ImportError as e:
        # Se fallisce qui, l'exe crasherà comunque, ma almeno abbiamo provato
        print(f"DEBUG: Failed to pre-load PyQt6 modules: {e}")

# Esegue il pre-caricamento immediatamente
_force_load_qt_modules()