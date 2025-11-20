import sys
import os
import time
import socket
import threading
import uvicorn
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
        from pyarmor_runtime import get_license_info
        info = get_license_info()
        if not info.get('expired'): 
            return False, "Licenza di sviluppo non consentita."
        return True, "OK"
    except:
        return False, "Errore Runtime (File manomessi)."

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

    # CONTROLLO LICENZA (Senza più EULA Dialog)
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