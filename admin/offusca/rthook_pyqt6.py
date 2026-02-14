# rthook_pyqt6.py
# Runtime hook per PyInstaller + PyArmor + PyQt6 WebEngine
# Forza il caricamento delle DLL prima dell'esecuzione del codice offuscato.


def _force_load_qt_modules():
    try:
        # Import espliciti per forzare PyInstaller a caricare i binari
        import PyQt6.QtNetwork
        import PyQt6.QtPrintSupport
        import PyQt6.QtWebChannel  # noqa: F401
    except ImportError:
        # Ignora errori in fase di hook, verranno gestiti dal main se bloccanti
        # S1481: Unused variable removed
        pass


_force_load_qt_modules()
