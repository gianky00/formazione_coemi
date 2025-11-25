import sys
import os
import time
import socket
import threading
import uvicorn
import importlib
import argparse
import requests

# --- CRITICAL: IMPORT WEBENGINE & SET ATTRIBUTE BEFORE QAPPLICATION ---
# This fixes "QtWebEngineWidgets must be imported or Qt.AA_ShareOpenGLContexts..."
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QCoreApplication

# Set the attribute specifically required for WebEngine on Windows/Frozen builds
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt6.QtGui import QPixmap

# --- 1. CONFIGURAZIONE AMBIENTE ---
if getattr(sys, 'frozen', False):
    EXE_DIR = os.path.dirname(sys.executable)

    # DLL Handling: Add 'dll' subdirectory to search path
    dll_dir = os.path.join(EXE_DIR, "dll")
    if os.name == 'nt' and os.path.exists(dll_dir):
        os.environ["PATH"] = dll_dir + os.pathsep + os.environ.get("PATH", "")
        try:
            if hasattr(os, 'add_dll_directory'):
                os.add_dll_directory(dll_dir)
        except Exception:
            pass

    # License Handling: Add 'Licenza' subdirectory to sys.path so PyArmor finds pyarmor.rkey
    lic_dir = os.path.join(EXE_DIR, "Licenza")
    if os.path.exists(lic_dir):
        sys.path.insert(0, lic_dir)

    # Cartella dell'EXE (per il DB fallback)
    db_path = os.path.join(EXE_DIR, "database_documenti.db")
    if os.name == 'nt': db_path = db_path.replace('\\', '\\\\')
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    
    # Cartella temporanea (per gli asset grafici)
    if hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)
    else:
        os.chdir(EXE_DIR)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# --- 2. VERIFICA LICENZA (Fisica + Logica Implicita) ---
def verify_license():
    """
    Verifica la presenza del file di runtime pyarmor.rkey.
    Cerca prima nella nuova cartella dati utente, poi nella vecchia per retrocompatibilità.
    """
    from desktop_app.services.path_service import get_license_dir, get_app_install_dir

    # 1. Percorso preferito (dati utente)
    user_license_path = os.path.join(get_license_dir(), "pyarmor.rkey")

    # 2. Percorsi di fallback (cartella di installazione)
    install_dir = get_app_install_dir()
    fallback_license_path_licenza = os.path.join(install_dir, "Licenza", "pyarmor.rkey")
    fallback_license_path_root = os.path.join(install_dir, "pyarmor.rkey")

    # Determina quale percorso usare
    if os.path.exists(user_license_path):
        lic_path = user_license_path
        sys.path.insert(0, os.path.dirname(user_license_path))
    elif os.path.exists(fallback_license_path_licenza):
        lic_path = fallback_license_path_licenza
        sys.path.insert(0, os.path.dirname(fallback_license_path_licenza))
    elif os.path.exists(fallback_license_path_root):
        lic_path = fallback_license_path_root
        sys.path.insert(0, os.path.dirname(fallback_license_path_root))
    else:
        return False, f"File di licenza (pyarmor.rkey) non trovato."

    # B. Check Logico Implicito: se il file è valido, l'import protetto funziona
    try:
        import app.core.config
        return True, "OK"
    except Exception as e:
        return False, f"Licenza non valida o scaduta.\nErrore sistema: {str(e)}"

# --- 3. UTILS ---
def find_free_port(start_port=8000, max_port=8010):
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('127.0.0.1', port)) != 0:
                    return port
        except:
            continue
    return None

def start_server(port):
    from app.main import app
    # Disable duplicate logs
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
    }
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="critical")

def check_port(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        return s.connect_ex((host, port)) == 0
    except: return False

# --- 4. MAIN ---
def main():
    print("[DEBUG] Starting launcher.main() ...")

    # Parse CLI Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyze", help="Path to folder or file to analyze")
    parser.add_argument("--import-csv", help="Path to CSV file to import")
    parser.add_argument("--view", help="View to open")
    args, unknown = parser.parse_known_args()

    # Find free port for this instance
    server_port = find_free_port()
    if not server_port:
        QMessageBox.critical(None, "Errore Avvio", "Nessuna porta libera trovata (8000-8010).")
        sys.exit(1)

    print(f"[DEBUG] Selected server port: {server_port}")
    os.environ["API_URL"] = f"http://localhost:{server_port}/api/v1"

    # Check if QApplication already exists (unlikely but safe)
    if not QApplication.instance():
        print("[DEBUG] Creating QApplication...")
        qt_app = QApplication(sys.argv)
    else:
        print("[DEBUG] QApplication already exists.")
        qt_app = QApplication.instance()

    # Import ApplicationController from the CORRECT module
    try:
        print("[DEBUG] Importing ApplicationController and setup_styles...")
        from desktop_app.main import ApplicationController, setup_styles
        print("[DEBUG] Running setup_styles...")
        setup_styles(qt_app)
    except ImportError as e:
        # Detailed debug for import errors
        import traceback
        traceback.print_exc()
        QMessageBox.critical(None, "Errore Moduli", f"Impossibile caricare i moduli principali:\n{e}")
        sys.exit(1)
    except Exception as e:
        QMessageBox.critical(None, "Errore Avvio", f"Errore generico: {e}")
        sys.exit(1)

    # CONTROLLO LICENZA
    license_ok, license_error = verify_license()

    # AVVIO SERVER
    print(f"[DEBUG] Starting server thread on port {server_port}...")
    threading.Thread(target=start_server, args=(server_port,), daemon=True).start()

    # SPLASH
    print("[DEBUG] Showing Splash Screen...")
    splash = QSplashScreen()
    if os.path.exists("desktop_app/assets/logo.png"):
        splash.setPixmap(QPixmap("desktop_app/assets/logo.png").scaled(600, 300, Qt.AspectRatioMode.KeepAspectRatio))
    splash.showMessage("Caricamento sistema...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, Qt.GlobalColor.black)
    splash.show()

    t0 = time.time()
    ready = False
    print(f"[DEBUG] Waiting for server port {server_port}...")
    while time.time() - t0 < 20:
        qt_app.processEvents()
        if check_port("127.0.0.1", server_port):
            ready = True
            print("[DEBUG] Server is ready!")
            break
        time.sleep(0.2)

    if ready:
        # Instantiate Controller
        print("[DEBUG] Instantiating ApplicationController...")
        controller = ApplicationController(license_ok=license_ok, license_error=license_error)

        # APPLY CLI ARGS (First Run)
        if args.analyze:
             controller.analyze_path(args.analyze)
        elif args.import_csv:
             controller.import_dipendenti_csv(args.import_csv)
        elif args.view and controller.dashboard:
             controller.dashboard.switch_to(args.view)

        print("[DEBUG] Calling controller.start()...")
        controller.start() # Shows window

        # Finish splash using the actual window from controller
        print("[DEBUG] Finishing Splash...")
        if hasattr(controller, 'master_window'):
            controller.master_window.ensurePolished()
            splash.finish(controller.master_window)
        else:
            splash.close()

        print("[DEBUG] Starting Qt Event Loop (exec)...")
        sys.exit(qt_app.exec())
    else:
        print("[ERROR] Server timeout!")
        sys.exit(1)

if __name__ == "__main__":
    main()
