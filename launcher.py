import sys
import os
import time
import socket
import threading
import uvicorn
import importlib

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
    # Cartella dell'EXE (per il DB)
    EXE_DIR = os.path.dirname(sys.executable)
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
    # A. Check Fisico: il file deve esistere accanto all'EXE
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Percorso atteso della licenza
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

# --- 4. MAIN ---
def main():
    # Check if QApplication already exists (unlikely but safe)
    if not QApplication.instance():
        qt_app = QApplication(sys.argv)
    else:
        qt_app = QApplication.instance()

    # Import ApplicationController from the CORRECT module
    # FIX: Was importing 'MainWindow' which does not exist
    try:
        from desktop_app.main import ApplicationController, setup_styles
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
        # Instantiate Controller
        controller = ApplicationController()

        # CHECK CLI ARGS FOR ANALYSIS
        args = sys.argv[1:]
        if "--analyze" in args:
            try:
                idx = args.index("--analyze")
                if idx + 1 < len(args):
                    folder_path = args[idx + 1]
                    if os.path.isdir(folder_path):
                        controller.analyze_folder(folder_path)
            except Exception as e:
                print(f"Error in CLI analysis: {e}")

        controller.start() # Shows window

        # Finish splash using the actual window from controller
        if hasattr(controller, 'master_window'):
            controller.master_window.ensurePolished()
            splash.finish(controller.master_window)
        else:
            splash.close()

        sys.exit(qt_app.exec())
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
