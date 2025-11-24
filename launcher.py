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
    # A. Check Fisico: il file deve esistere
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        # Production: Check in Licenza folder
        lic_path = os.path.join(base_dir, "Licenza", "pyarmor.rkey")
    else:
        # Dev: Check in root
        base_dir = os.path.dirname(os.path.abspath(__file__))
        lic_path = os.path.join(base_dir, "pyarmor.rkey")
    
    if not os.path.exists(lic_path):
        return False, f"File di licenza mancante.\nCercato in: {lic_path}"

    # B. Check Logico Implicito:
    try:
        import app.core.config
        return True, "OK"
    except Exception as e:
        return False, f"Licenza non valida o scaduta.\nErrore sistema: {str(e)}"

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

def check_existing_instance(args):
    """
    Checks if an instance is already running on port 8000.
    If so, sends the command via IPC and returns True (so we can exit).
    """
    try:
        # 1. Check if port is open (fast check)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()

        if result != 0:
            return False # Port closed, not running

        # 2. Handshake / Health Check (Ensure it's Intelleo)
        response = requests.get("http://127.0.0.1:8000/api/v1/health", timeout=1)
        if response.status_code != 200:
            return False # Not our app or broken

        # 3. Construct Payload
        action = "view" # Default action (bring to front)
        payload = {}

        if args.analyze:
            action = "analyze"
            payload["path"] = args.analyze
        elif args.import_csv:
            action = "import_csv"
            payload["path"] = args.import_csv
        elif args.view:
            action = "view"
            payload["view_name"] = args.view

        # 4. Send Command
        print(f"[LAUNCHER] Sending IPC command: {action} {payload}")
        requests.post("http://127.0.0.1:8000/api/v1/system/open-action",
                      json={"action": action, "payload": payload}, timeout=2)
        return True

    except Exception as e:
        print(f"[LAUNCHER] Existing instance check failed (starting new): {e}")
        return False

# --- 4. MAIN ---
def main():
    print("[DEBUG] Starting launcher.main() ...")

    # Parse CLI Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyze", help="Path to folder or file to analyze")
    parser.add_argument("--import-csv", help="Path to CSV file to import")
    parser.add_argument("--view", help="View to open")
    args, unknown = parser.parse_known_args()

    # CHECK EXISTING INSTANCE
    if check_existing_instance(args):
        print("[LAUNCHER] Command sent to existing instance. Exiting.")
        sys.exit(0)

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
    ok, err = verify_license()
    if not ok:
        mbox = QMessageBox()
        mbox.setIcon(QMessageBox.Icon.Warning)
        mbox.setWindowTitle("Licenza")
        mbox.setText("Verifica licenza fallita.")
        mbox.setDetailedText(err)
        mbox.exec()
        sys.exit(1)

    # AVVIO SERVER
    print("[DEBUG] Starting server thread...")
    threading.Thread(target=start_server, daemon=True).start()

    # SPLASH
    print("[DEBUG] Showing Splash Screen...")
    splash = QSplashScreen()
    if os.path.exists("desktop_app/assets/logo.png"):
        splash.setPixmap(QPixmap("desktop_app/assets/logo.png").scaled(600, 300, Qt.AspectRatioMode.KeepAspectRatio))
    splash.showMessage("Caricamento sistema...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, Qt.GlobalColor.black)
    splash.show()

    t0 = time.time()
    ready = False
    print("[DEBUG] Waiting for server port 8000...")
    while time.time() - t0 < 20:
        qt_app.processEvents()
        if check_port("127.0.0.1", 8000):
            ready = True
            print("[DEBUG] Server is ready!")
            break
        time.sleep(0.2)

    if ready:
        # Instantiate Controller
        print("[DEBUG] Instantiating ApplicationController...")
        controller = ApplicationController()

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
