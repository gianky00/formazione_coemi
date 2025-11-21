import sys
import os
import time
import socket
import threading
import uvicorn
import importlib
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

        # Tentativo 1: Import diretto standard
        try:
            from pyarmor_runtime import get_license_info
            get_license_info_func = get_license_info
        except ImportError:
            pass

        # Tentativo 2: Risoluzione Runtime Randomizzato
        if not get_license_info_func:
            search_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
            runtime_pkg_name = None

            for item in os.listdir(search_path):
                if item.startswith("pyarmor_runtime_") and os.path.isdir(os.path.join(search_path, item)):
                    runtime_pkg_name = item
                    break

            if runtime_pkg_name:
                try:
                    # 1. Importa il pacchetto randomizzato
                    pkg = importlib.import_module(runtime_pkg_name)

                    # 2. Cerca il sottomodulo 'pyarmor_runtime' interno
                    if hasattr(pkg, "pyarmor_runtime"):
                        real_runtime = getattr(pkg, "pyarmor_runtime")

                        # 3. TRUCCO ESSENZIALE: Aliasing in sys.modules
                        # Facciamo credere a Python che questo sia il 'pyarmor_runtime' ufficiale
                        sys.modules["pyarmor_runtime"] = real_runtime

                        # 4. Ora riproviamo l'import standard
                        # Questo spesso triggera l'inizializzazione corretta del modulo
                        try:
                            from pyarmor_runtime import get_license_info
                            get_license_info_func = get_license_info
                        except ImportError:
                            # Se fallisce ancora, controlliamo se è disponibile direttamente sull'oggetto
                            if hasattr(real_runtime, "get_license_info"):
                                get_license_info_func = real_runtime.get_license_info

                    # 5. Fallback estremo: controllo __pyarmor__ (Internal API)
                    if not get_license_info_func and hasattr(pkg, "__pyarmor__"):
                         internal_api = getattr(pkg, "__pyarmor__")
                         if hasattr(internal_api, "get_license_info"):
                             get_license_info_func = internal_api.get_license_info

                except Exception as e:
                     return False, f"Err init runtime {runtime_pkg_name}: {e}"

        if not get_license_info_func:
             # Se fallisce tutto, diamo un errore chiaro
             return False, "Funzione get_license_info non trovata nemmeno dopo aliasing."

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
        QMessageBox.warning(None, "Licenza", f"Errore: {err}")
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