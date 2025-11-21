import sys
import os
import time
import socket
import threading
import uvicorn
import importlib
import pkgutil
from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# --- 1. CONFIGURAZIONE AMBIENTE ---
if getattr(sys, 'frozen', False):
    # Cartella dell'EXE (per il DB)
    EXE_DIR = os.path.dirname(sys.executable)
    db_path = os.path.join(EXE_DIR, "scadenzario.db")
    if os.name == 'nt': db_path = db_path.replace('\\', '\\\\')
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    
    # Cartella temporanea (per gli asset grafici)
    os.chdir(sys._MEIPASS)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# --- 2. VERIFICA LICENZA (Fisica + Logica) ---
def verify_license():
    # A. Check Fisico: il file deve esistere accanto all'EXE
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if not os.path.exists(os.path.join(base_dir, "pyarmor.rkey")):
        return False, "File 'pyarmor.rkey' mancante."

    # B. Check Logico: PyArmor deve validarla
    try:
        get_license_info_func = None
        debug_info = [] # Raccoglitore di info per debug

        # Tentativo 1: Import diretto
        try:
            from pyarmor_runtime import get_license_info
            get_license_info_func = get_license_info
        except ImportError:
            pass

        # Tentativo 2: Ricerca dinamica
        if not get_license_info_func:
            search_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
            runtime_pkg_name = None

            # Cerca la cartella
            for item in os.listdir(search_path):
                if item.startswith("pyarmor_runtime_") and os.path.isdir(os.path.join(search_path, item)):
                    runtime_pkg_name = item
                    break

            if runtime_pkg_name:
                try:
                    debug_info.append(f"Found pkg: {runtime_pkg_name}")
                    mod = importlib.import_module(runtime_pkg_name)
                    debug_info.append(f"Dir(mod): {dir(mod)}")

                    # Check top level
                    if hasattr(mod, "get_license_info"):
                         get_license_info_func = mod.get_license_info

                    # Check submodule 'pyarmor_runtime'
                    if not get_license_info_func:
                        try:
                            sub_name = f"{runtime_pkg_name}.pyarmor_runtime"
                            submod = importlib.import_module(sub_name)
                            debug_info.append(f"Submod {sub_name} loaded. Dir: {dir(submod)}")
                            if hasattr(submod, "get_license_info"):
                                get_license_info_func = submod.get_license_info
                        except ImportError as e:
                            debug_info.append(f"Import {sub_name} failed: {e}")

                    # Check attribute 'pyarmor_runtime'
                    if not get_license_info_func and hasattr(mod, "pyarmor_runtime"):
                         sub_obj = getattr(mod, "pyarmor_runtime")
                         debug_info.append(f"Attr pyarmor_runtime found. Type: {type(sub_obj)} Dir: {dir(sub_obj)}")
                         if hasattr(sub_obj, "get_license_info"):
                             get_license_info_func = sub_obj.get_license_info

                except Exception as e:
                     return False, f"Err import {runtime_pkg_name}: {e}"
            else:
                debug_info.append("No runtime folder found in " + search_path)

        if not get_license_info_func:
             # FORMATTA IL MESSAGGIO DI DEBUG PER L'UTENTE
             debug_str = "\n".join(debug_info)
             return False, f"DEBUG MODE: Funzione mancante.\n{debug_str}"

        info = get_license_info_func()
        if not info.get('expired'): 
            return False, "Licenza di sviluppo non consentita."
        return True, "OK"
    except Exception as e:
        return False, f"Errore Runtime Generico: {str(e)}"

# --- 3. UTILS ---
def start_server():
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="critical")

def check_port(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        return s.connect_ex((host, port)) == 0
    except: return False

# --- 4. AVVIO ---
if __name__ == "__main__":
    qt_app = QApplication(sys.argv)

    # Import Stile
    try:
        from desktop_app.main import MainWindow, setup_styles
        setup_styles(qt_app)
    except Exception as e:
        QMessageBox.critical(None, "Errore Avvio", f"Errore moduli: {e}")
        sys.exit(1)

    # CONTROLLO LICENZA
    ok, err = verify_license()
    if not ok:
        # Usa critical per avere una finestra più grande se necessario, o warning
        mbox = QMessageBox()
        mbox.setIcon(QMessageBox.Icon.Critical)
        mbox.setWindowTitle("Errore Licenza")
        mbox.setText("Errore verifica licenza.")
        mbox.setDetailedText(err) # Mette il debug nel dettaglio espandibile
        mbox.exec()
        sys.exit(1)

    # AVVIO SERVER
    threading.Thread(target=start_server, daemon=True).start()

    # SPLASH
    splash = QSplashScreen()
    if os.path.exists("desktop_app/assets/logo.png"):
        splash.setPixmap(QPixmap("desktop_app/assets/logo.png").scaled(600, 300, Qt.AspectRatioMode.KeepAspectRatio))
    splash.showMessage("Caricamento sistema...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, Qt.GlobalColor.black)
    splash.show()

    t0 = time.time()
    ready = False
    while time.time() - t0 < 20:
        qt_app.processEvents()
        if check_port("127.0.0.1", 8000):
            ready = True
            break
        time.sleep(0.2)

    if ready:
        w = MainWindow()
        w.ensurePolished()
        w.showMaximized()
        splash.finish(w)
        sys.exit(qt_app.exec())
    else:
        sys.exit(1)