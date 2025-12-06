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
import sqlite3
import traceback as tb

# --- SENTRY INTEGRATION ---
import sentry_sdk

def init_sentry():
    """Initializes Sentry SDK for error tracking."""
    # Environment detection
    environment = "production" if getattr(sys, 'frozen', False) else "development"

    # DSN Resolution (Env Var -> Hardcoded Fallback)
    SENTRY_DSN = os.environ.get("SENTRY_DSN", "https://f252d598aaf7e70fe94d533474b76639@o4510490492600320.ingest.de.sentry.io/4510490526744656")

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=environment,
        traces_sample_rate=1.0,
        send_default_pii=True
    )

def sentry_exception_hook(exctype, value, traceback):
    """
    Global exception handler that captures errors to Sentry
    AND ensures database security cleanup.
    """
    # 1. Capture to Sentry
    sentry_sdk.capture_exception(value)

    # 2. Print Traceback (for local logging/debugging)
    print(f"[CRITICAL] Unhandled exception: {exctype}, {value}")
    tb.print_tb(traceback)

    # 3. Database Cleanup (CRITICAL)
    try:
        from app.core.db_security import db_security
        print("[CRITICAL] Attempting emergency DB cleanup...")
        db_security.cleanup()
    except Exception as e:
        print(f"[CRITICAL] Emergency cleanup failed: {e}")
        sentry_sdk.capture_exception(e) # Capture cleanup failure too

    # 4. Exit
    sys.exit(1)

# Initialize Sentry immediately
init_sentry()
# Override global exception hook
sys.excepthook = sentry_exception_hook

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

# --- PHASE 0: LICENSE GATEKEEPER ---
def verify_license_files():
    """Checks for the physical presence of license files."""
    from desktop_app.services.path_service import get_license_dir, get_app_install_dir

    # 1. Check User Data Directory (Preferred)
    user_lic_dir = get_license_dir()
    if os.path.exists(os.path.join(user_lic_dir, "pyarmor.rkey")) and \
       os.path.exists(os.path.join(user_lic_dir, "config.dat")):
        sys.path.insert(0, user_lic_dir)
        return True

    # 2. Check Install Directory (Legacy)
    install_dir = get_app_install_dir()
    legacy_lic_dir = os.path.join(install_dir, "Licenza")
    if os.path.exists(os.path.join(legacy_lic_dir, "pyarmor.rkey")) and \
       os.path.exists(os.path.join(legacy_lic_dir, "config.dat")):
        sys.path.insert(0, legacy_lic_dir)
        return True

    # 3. Check Root (Legacy)
    if os.path.exists(os.path.join(install_dir, "pyarmor.rkey")) and \
       os.path.exists(os.path.join(install_dir, "config.dat")):
        sys.path.insert(0, install_dir)
        return True

    return False

def check_license_gatekeeper(splash):
    """
    Step 0: Strict License Check.
    If license is missing or invalid, attempt headless update.
    If update fails, BLOCK startup.
    """
    splash.update_status("Controllo Licenza...", 5)
    QApplication.processEvents()

    # 1. Physical Check
    files_ok = verify_license_files()

    # 2. Validity Check (Simulated by import)
    valid_license = False
    if files_ok:
        try:
            # Try importing a protected module
            import app.core.config
            valid_license = True
        except Exception:
            valid_license = False

    if valid_license:
        return # Proceed

    # --- LICENSE INVALID/MISSING: RECOVERY MODE ---
    splash.update_status("Licenza mancante. Tentativo aggiornamento...", 5)
    QApplication.processEvents()

    try:
        from app.core.config import settings
        from desktop_app.services.license_updater_service import LicenseUpdaterService
        from desktop_app.services.hardware_id_service import get_machine_id

        # Prepare Config for Headless Update
        update_config = {
            "repo_owner": settings.LICENSE_REPO_OWNER,
            "repo_name": settings.LICENSE_REPO_NAME,
            "github_token": settings.LICENSE_GITHUB_TOKEN
        }

        updater = LicenseUpdaterService(config=update_config)
        hw_id = get_machine_id()

        success, msg = updater.update_license(hw_id)

        if success:
            splash.update_status("Licenza aggiornata! Riavvio...", 100)
            QApplication.processEvents()
            time.sleep(1)
            # Restart Application
            python = sys.executable
            os.execl(python, python, *sys.argv)
        else:
            QMessageBox.critical(None, "Errore Licenza",
                f"Impossibile avviare l'applicazione.\n\nStato Licenza: {msg}\n\nContattare il supporto.")
            sys.exit(1)

    except Exception as e:
        QMessageBox.critical(None, "Errore Critico", f"Fallito recupero licenza:\n{e}")
        sys.exit(1)

# --- PHASE 2: DATABASE INTEGRITY & RECOVERY ---

def initialize_new_database(path_obj):
    """
    Creates a new SQLite database with DELETE mode (compatible with in-memory loading), Schema, and Admin User.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.db.models import Base
    from app.db.seeding import seed_database
    from app.core.config import settings

    # 1. Initialize SQLite file with DELETE Mode (Not WAL, to avoid multi-file issues during single-file load)
    conn = sqlite3.connect(str(path_obj))
    conn.execute("PRAGMA journal_mode=DELETE;")
    conn.execute("PRAGMA synchronous=FULL;")
    conn.commit()
    conn.close()

    # 2. Apply Schema (SQLAlchemy)
    db_url = f"sqlite:///{path_obj}"
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)

    # 3. Seed Admin
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    # 4. Update Settings
    settings.save_mutable_settings({"DATABASE_PATH": str(path_obj)})


def post_launch_integrity_check(controller):
    """
    Step 3 (Delayed): Integrity Check and Recovery Dialog.
    Executes AFTER the UI (Login) is visible.
    """
    try:
        from app.core.config import settings, get_user_data_dir
        from app.core.db_security import db_security
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

        # 1. Check Existence
        exists = target.exists()

        # 2. Check Integrity (if exists)
        is_valid = False
        if exists:
            # Check silently if possible, or show minimal feedback
            # In post-launch, we probably just check validity.
            # db_security.verify_integrity reads the file.
            is_valid = db_security.verify_integrity(target)

        if exists and is_valid:
            # Everything is fine.
            break

        # 3. Prompt User (Recovery Dialog OVER Login View)
        # Use controller.login_view as parent if available
        parent = controller.login_view if hasattr(controller, 'login_view') and controller.login_view else None

        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Critical if exists else QMessageBox.Icon.Warning)

        if not exists:
            msg.setWindowTitle("Database Mancante")
            msg.setText("Il database non è stato trovato.")
            msg.setInformativeText(f"Percorso: {target}\n\nÈ necessario creare un nuovo database o selezionarne uno esistente.")
        else:
            msg.setWindowTitle("Database Corrotto")
            msg.setText("Il file del database è danneggiato.")
            msg.setInformativeText("Integrità compromessa. Ripristinare un backup o creare un nuovo database.")

        browse_btn = msg.addButton("Sfoglia / Ripristina...", QMessageBox.ButtonRole.ActionRole)
        create_btn = msg.addButton("Crea Nuovo Database", QMessageBox.ButtonRole.ActionRole)
        exit_btn = msg.addButton("Esci", QMessageBox.ButtonRole.RejectRole)

        msg.setWindowFlags(msg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        msg.exec()

        clicked = msg.clickedButton()

        if clicked == browse_btn:
            file_path, _ = QFileDialog.getOpenFileName(parent, "Seleziona Database", str(get_user_data_dir()), "Database Files (*.db *.bak)")
            if file_path:
                file_path = os.path.normpath(file_path)
                path_obj = Path(file_path)

                if path_obj.suffix.lower() == ".bak":
                    # RESTORE LOGIC
                    reply = QMessageBox.question(parent, "Ripristino Backup", f"Ripristinare dal backup:\n{path_obj.name}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        try:
                            db_security.db_path = target
                            db_security.data_dir = target.parent
                            db_security.restore_from_backup(path_obj)
                            # RESTART REQUIRED to reload DB in backend
                            restart_app()
                        except Exception as e:
                            QMessageBox.critical(parent, "Errore", f"Ripristino fallito: {e}")
                else:
                    # Update Settings
                    settings.save_mutable_settings({"DATABASE_PATH": file_path})
                    # RESTART REQUIRED
                    restart_app()

        elif clicked == create_btn:
            try:
                # Ask user for DIRECTORY
                dir_path = QFileDialog.getExistingDirectory(parent, "Seleziona Cartella per Nuovo Database", str(get_user_data_dir()))
                if not dir_path:
                    continue # Cancelled

                # Enforce standard filename
                target = Path(dir_path) / "database_documenti.db"

                # Initialize with DELETE mode
                initialize_new_database(target)

                # RESTART REQUIRED
                restart_app()
            except Exception as e:
                QMessageBox.critical(parent, "Errore Creazione", f"Impossibile creare il database:\n{e}")

        else:
            sys.exit(1)

def restart_app():
    """Restarts the current application."""
    python = sys.executable
    os.execl(python, python, *sys.argv)

class StartupWorker(QThread):
    progress_update = pyqtSignal(str, int)
    error_occurred = pyqtSignal(str)
    startup_complete = pyqtSignal(bool, str)

    def __init__(self, server_port):
        super().__init__()
        self.server_port = server_port

    def run(self):
        try:
            # 1. Environment Checks
            self.progress_update.emit("Verifica ambiente...", 30)
            try:
                from desktop_app.services.security_service import is_virtual_environment, is_debugger_active, is_analysis_tool_running
                from desktop_app.services.integrity_service import verify_critical_components

                is_intact, int_msg = verify_critical_components()
                if not is_intact: raise Exception(f"Integrità compromessa: {int_msg}")
            except ImportError: pass

            # 2. Clock
            self.progress_update.emit("Sincronizzazione orologio...", 40)
            try:
                from desktop_app.services.time_service import check_system_clock
                clock_ok, clock_error = check_system_clock()
                if not clock_ok: raise Exception(clock_error)
            except ImportError: pass

            # 3. Server Start
            self.progress_update.emit("Avvio Server Database...", 50)
            threading.Thread(target=start_server, args=(self.server_port,), daemon=True).start()

            # 4. Wait for Server
            self.progress_update.emit("Connessione al Backend...", 60)
            t0 = time.time()
            ready = False
            while time.time() - t0 < 20:
                if check_port("127.0.0.1", self.server_port):
                    ready = True
                    break
                elapsed = time.time() - t0
                prog = 60 + int((elapsed / 20) * 30)
                self.progress_update.emit("Connessione al Backend...", min(90, prog))
                time.sleep(0.1)

            if not ready:
                raise Exception("Timeout connessione al server locale.")

            # 5. Health Check
            self.progress_update.emit("Verifica Connessione...", 92)
            try:
                health_url = f"http://localhost:{self.server_port}/api/v1/health"
                response = requests.get(health_url, timeout=5)
                if response.status_code != 200:
                    raise Exception(f"Server Error: {response.json().get('detail')}")
            except Exception as e:
                raise Exception(f"Health Check Failed: {e}")

            # 6. Ready
            self.progress_update.emit("Caricamento interfaccia...", 98)
            # License is guaranteed valid by Gatekeeper
            self.startup_complete.emit(True, "OK")

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

    # Show Splash
    try:
        from desktop_app.views.splash_screen import CustomSplashScreen
        splash = CustomSplashScreen()
        splash.show()
    except Exception as e:
        QMessageBox.critical(None, "Errore", f"Splash Error: {e}")
        sys.exit(1)

    # --- EXECUTE STRICT STARTUP SEQUENCE ---

    # Step 0: License Gatekeeper
    check_license_gatekeeper(splash)

    # Step 1 (Removed Pre-Launch Check): Proceed to App Launch

    # Step 2: Start Backend & App
    worker = StartupWorker(server_port)

    def on_progress(msg, val):
        splash.update_status(msg, val)

    def on_error(msg):
        splash.show_error(msg)

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

            # --- STEP 3: POST-LAUNCH DB INTEGRITY CHECK ---
            # Now that UI (Login) is potentially visible, check DB.
            # If missing/corrupt, the dialog will show OVER the Login View.
            # And user can resolve it.
            post_launch_integrity_check(controller)

        except Exception as e:
            splash.show_error(f"Errore caricamento interfaccia: {e}")
            sys.exit(1)

    worker.progress_update.connect(on_progress)
    worker.error_occurred.connect(on_error)
    worker.startup_complete.connect(on_complete)

    worker.start()

    sys.exit(qt_app.exec())

if __name__ == "__main__":
    main()
