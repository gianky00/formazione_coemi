import sys
import os
import time
import socket
import threading
import uvicorn
import importlib
import argparse
import requests
import platform

# --- CRITICAL: IMPORT WEBENGINE & SET ATTRIBUTE BEFORE QAPPLICATION ---
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QCoreApplication, QTimer, QThread, pyqtSignal, QObject

QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox, QFileDialog
from PyQt6.QtGui import QPixmap

# --- CONFIGURAZIONE AMBIENTE ---
if getattr(sys, 'frozen', False):
    EXE_DIR = os.path.dirname(sys.executable)
    dll_dir = os.path.join(EXE_DIR, "dll")
    if os.name == 'nt' and os.path.exists(dll_dir):
        os.environ["PATH"] = dll_dir + os.pathsep + os.environ.get("PATH", "")
        try:
            if hasattr(os, 'add_dll_directory'):
                os.add_dll_directory(dll_dir)
        except Exception:
            pass

    lic_dir = os.path.join(EXE_DIR, "Licenza")
    if os.path.exists(lic_dir):
        sys.path.insert(0, lic_dir)

    db_path = os.path.join(EXE_DIR, "database_documenti.db")
    if os.name == 'nt': db_path = db_path.replace('\\', '\\\\')
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    
    if hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)
    else:
        os.chdir(EXE_DIR)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# --- UTILS ---
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
        "formatters": { "default": { "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s" } },
        "handlers": { "console": { "class": "logging.StreamHandler", "formatter": "default" } },
        "root": { "level": "INFO", "handlers": ["console"] },
    }
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="critical")

def check_port(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        result = s.connect_ex((host, port)) == 0
        s.close()
        return result
    except: return False

def check_database_recovery(splash):
    """
    Checks if the configured database file exists.
    If not, enters a blocking Recovery Loop to prompt the user.
    """
    try:
        # Import dynamically to ensure environment is ready
        from app.core.config import settings, get_user_data_dir
        from pathlib import Path
    except ImportError as e:
        QMessageBox.critical(None, "Errore Critico", f"Impossibile caricare configurazione: {e}")
        sys.exit(1)

    while True:
        db_path_str = settings.DATABASE_PATH
        if db_path_str:
             db_path = Path(db_path_str)
             if db_path.is_dir():
                 target = db_path / "database_documenti.db"
             else:
                 target = db_path
        else:
             target = get_user_data_dir() / "database_documenti.db"

        if target.exists():
            break

        # Notify User
        splash.update_status(f"Database mancante: {target.name}")

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Database Non Trovato")
        msg.setText("Il file del database non è stato trovato.")
        msg.setInformativeText(f"Percorso atteso:\n{target}\n\nSeleziona 'Sfoglia' per localizzare il file .db esistente.")
        browse_btn = msg.addButton("Sfoglia...", QMessageBox.ButtonRole.ActionRole)
        exit_btn = msg.addButton("Esci", QMessageBox.ButtonRole.RejectRole)

        # Ensure dialog is top-most
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        msg.exec()

        if msg.clickedButton() == browse_btn:
            file_path, _ = QFileDialog.getOpenFileName(None, "Seleziona Database", str(get_user_data_dir()), "SQLite Database (*.db)")

            if file_path:
                # Update Settings
                try:
                    settings.save_mutable_settings({"DATABASE_PATH": file_path})
                    splash.update_status("Database aggiornato. Riavvio controllo...")
                except Exception as e:
                     QMessageBox.critical(None, "Errore", f"Impossibile salvare impostazioni: {e}")
        else:
            sys.exit(1)


def verify_license():
    from desktop_app.services.path_service import get_license_dir, get_app_install_dir
    user_license_path = os.path.join(get_license_dir(), "pyarmor.rkey")
    install_dir = get_app_install_dir()
    fallback_license_path_licenza = os.path.join(install_dir, "Licenza", "pyarmor.rkey")
    fallback_license_path_root = os.path.join(install_dir, "pyarmor.rkey")

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
        return False, "File di licenza (pyarmor.rkey) non trovato."

    try:
        import app.core.config
        return True, "OK"
    except Exception as e:
        return False, f"Licenza non valida o scaduta.\nErrore sistema: {str(e)}"

class StartupWorker(QThread):
    progress_update = pyqtSignal(str, int)
    error_occurred = pyqtSignal(str)
    startup_complete = pyqtSignal(bool, str) # license_ok, license_error

    def __init__(self, server_port):
        super().__init__()
        self.server_port = server_port

    def run(self):
        try:
            # 1. Integrity
            self.progress_update.emit("Verifica integrità...", 10)
            try:
                from desktop_app.services.security_service import is_virtual_environment, is_debugger_active, is_analysis_tool_running
                from desktop_app.services.integrity_service import verify_critical_components

                is_intact, int_msg = verify_critical_components()
                if not is_intact: raise Exception(f"Integrità compromessa: {int_msg}")

                is_dbg, dbg_msg = is_debugger_active()
                if is_dbg: raise Exception(dbg_msg)

                is_tool, tool_msg = is_analysis_tool_running()
                if is_tool: raise Exception(tool_msg)

                is_vm, vm_msg = is_virtual_environment()
                if is_vm: raise Exception(vm_msg)
            except ImportError:
                pass # Dev mode

            # 2. License
            self.progress_update.emit("Controllo Licenza...", 30)
            license_ok, license_error = verify_license()

            # 3. Clock
            self.progress_update.emit("Sincronizzazione orologio...", 40)
            try:
                from desktop_app.services.time_service import check_system_clock
                clock_ok, clock_error = check_system_clock()
                if not clock_ok: raise Exception(clock_error)
            except ImportError: pass

            # 4. Server Start
            self.progress_update.emit("Avvio Server Database...", 50)
            threading.Thread(target=start_server, args=(self.server_port,), daemon=True).start()

            # 5. Wait for Server
            self.progress_update.emit("Connessione al Backend...", 60)
            t0 = time.time()
            ready = False
            while time.time() - t0 < 20:
                if check_port("127.0.0.1", self.server_port):
                    ready = True
                    break
                # Animate progress while waiting
                elapsed = time.time() - t0
                prog = 60 + int((elapsed / 20) * 30)
                self.progress_update.emit("Connessione al Backend...", min(90, prog))
                time.sleep(0.1) # Safe in thread

            if not ready:
                raise Exception("Timeout connessione al server locale.")

            # 6. Health Check
            self.progress_update.emit("Verifica Connessione...", 92)
            try:
                health_url = f"http://localhost:{self.server_port}/api/v1/health"
                response = requests.get(health_url, timeout=5)
                if response.status_code != 200:
                    detail = response.json().get("detail", "Errore sconosciuto")
                    raise Exception(f"Server Error: {detail}")
            except Exception as e:
                raise Exception(f"Health Check Failed: {e}")

            # 7. Ready
            self.progress_update.emit("Caricamento risorse...", 98)
            self.startup_complete.emit(license_ok, license_error)

        except Exception as e:
            self.error_occurred.emit(str(e))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyze", help="Path")
    parser.add_argument("--import-csv", help="Path")
    parser.add_argument("--view", help="View")
    args, unknown = parser.parse_known_args()

    server_port = find_free_port()
    if not server_port:
        QMessageBox.critical(None, "Errore", "Nessuna porta libera.")
        sys.exit(1)

    os.environ["API_URL"] = f"http://localhost:{server_port}/api/v1"

    if not QApplication.instance():
        qt_app = QApplication(sys.argv)
    else:
        qt_app = QApplication.instance()

    # Show Splash Immediately
    try:
        from desktop_app.views.splash_screen import CustomSplashScreen
        splash = CustomSplashScreen()
        splash.show()
        splash.update_status("Avvio sistema...", 0)
    except Exception as e:
        QMessageBox.critical(None, "Errore", f"Splash Error: {e}")
        sys.exit(1)

    # RECOVERY LOOP: Check Database Existence
    try:
        splash.update_status("Controllo Database...", 5)
        # Ensure splash updates before blocking loop
        QApplication.processEvents()
        check_database_recovery(splash)
    except Exception as e:
        QMessageBox.critical(None, "Errore Recovery", f"Errore durante il controllo del database: {e}")
        sys.exit(1)

    # Worker Setup
    worker = StartupWorker(server_port)

    def on_progress(msg, val):
        splash.update_status(msg, val)

    def on_error(msg):
        splash.show_error(msg)
        # Don't exit immediately, allow user to read and close splash manually
        # Splash show_error manages its own event loop if needed or we wait
        # Since we are in main thread, qt_app.exec() hasn't started yet.
        # But splash.show_error calls loop.exec().
        # After loop quits, splash closes. We should exit.
        # sys.exit(1) happens after splash closes.

    def on_complete(license_ok, license_error):
        try:
            splash.update_status("Avvio Interfaccia...", 100)
            from desktop_app.main import ApplicationController, setup_styles
            setup_styles(qt_app)

            controller = ApplicationController(license_ok=license_ok, license_error=license_error)

            if args.analyze: controller.analyze_path(args.analyze)
            elif args.import_csv: controller.import_dipendenti_csv(args.import_csv)
            elif args.view and controller.dashboard: controller.dashboard.switch_to(args.view)

            controller.start()

            if hasattr(controller, 'master_window'):
                controller.master_window.ensurePolished()
                splash.finish(controller.master_window)
            else:
                splash.close()

        except Exception as e:
            splash.show_error(f"Errore caricamento interfaccia: {e}")
            sys.exit(1)

    worker.progress_update.connect(on_progress)
    worker.error_occurred.connect(on_error)
    worker.startup_complete.connect(on_complete)

    worker.start()

    # Start Event Loop
    sys.exit(qt_app.exec())

if __name__ == "__main__":
    main()
