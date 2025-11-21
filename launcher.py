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
        # Tentativo 1: Import diretto (per versioni vecchie o statiche)
        try:
            from pyarmor_runtime import get_license_info
        except ImportError:
            # Tentativo 2: Ricerca dinamica del runtime randomizzato (pyarmor_runtime_xxxxxx)
            runtime_pkg = None

            # Cerca nei moduli già caricati o nel path
            # Nota: In build frozen, spesso il runtime è già in sys.modules o importabile
            for name in sys.builtin_module_names:
                if name.startswith('pyarmor_runtime'):
                    runtime_pkg = name
                    break

            if not runtime_pkg:
                # Se non è builtin, prova a trovarlo importandolo se possibile o scandendo
                # Ma in frozen environments (PyInstaller), di solito è un pacchetto nascosto
                # Proviamo a scansionare i file nella directory corrente (per non-frozen) o
                # affidiamoci al fatto che PyInstaller lo impacchetta.

                # Strategia migliore per PyInstaller one-dir con PyArmor 8+:
                # Il runtime è una cartella dentro la dist.
                # Cerchiamo di importarlo "alla cieca" se conosciamo il prefisso? No.
                # Cerchiamo tra i moduli disponibili se possiamo.

                # In PyInstaller, sys.modules potrebbe non averlo ancora se non importato.
                # Ma il nome è fisso al momento del build.
                # Prova a scansionare sys.modules dopo un tentativo di import fallito?
                pass

            # Se siamo qui, proviamo un approccio diverso:
            # PyArmor inietta il runtime. Se usiamo `gen`, il runtime ha un nome specifico.
            # Dobbiamo trovarlo.

            found = False
            # Metodo scansione directory (funziona se non è single-file o se scompattato)
            search_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)

            for item in os.listdir(search_path):
                if item.startswith("pyarmor_runtime_") and os.path.isdir(os.path.join(search_path, item)):
                    try:
                        mod = importlib.import_module(f"{item}")
                        get_license_info = mod.get_license_info
                        found = True
                        break
                    except Exception as e:
                        return False, f"Trovato runtime {item} ma errore import: {e}"

            if not found:
                 return False, "Modulo pyarmor_runtime non trovato."

        info = get_license_info()
        if not info.get('expired'): 
            return False, "Licenza di sviluppo non consentita."
        return True, "OK"
    except Exception as e:
        return False, f"Errore Runtime: {str(e)}"

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