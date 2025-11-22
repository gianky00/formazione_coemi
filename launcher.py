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
    # Invece di cercare API nascoste, proviamo ad importare un modulo offuscato.
    # Se la licenza è invalida, PyArmor bloccherà l'importazione sollevando un'eccezione.
    try:
        # Proviamo ad importare un modulo leggero del backend
        # Nota: Questo funzionerà solo se 'app' è stato effettivamente offuscato.
        # Se siamo in dev mode (non offuscato), funzionerà comunque.
        import app.core.config
        return True, "OK"
    except Exception as e:
        # Se PyArmor blocca l'esecuzione, l'errore sarà qui.
        # Potrebbe essere un RuntimeError o un ImportError specifico.
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
        mbox = QMessageBox()
        mbox.setIcon(QMessageBox.Icon.Warning) # Warning è sufficiente ora
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
        w = MainWindow()
        w.ensurePolished()
        w.showMaximized()
        splash.finish(w)

        # CHECK CLI ARGS FOR ANALYSIS
        args = sys.argv[1:]
        if "--analyze" in args:
            try:
                idx = args.index("--analyze")
                if idx + 1 < len(args):
                    folder_path = args[idx + 1]
                    if os.path.isdir(folder_path):
                        w.analyze_folder(folder_path)
            except Exception as e:
                print(f"Error in CLI analysis: {e}")

        sys.exit(qt_app.exec())
    else:
        sys.exit(1)