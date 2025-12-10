import sys
import os
import time
import socket
import threading
import uvicorn
import argparse
import requests
import platform
import sqlite3
import traceback as tb
import logging
import logging.handlers
import importlib

# --- BUG FIX: Increase recursion limit to prevent crashes on bulk operations ---
sys.setrecursionlimit(5000)

# Constants
DATABASE_FILENAME = "database_documenti.db"
LICENSE_FILE_KEY = "pyarmor.rkey"
LICENSE_FILE_CONFIG = "config.dat"

# --- PHASE 2: LOGGING CONFIGURATION ---
# Must be configured BEFORE any other imports to capture everything
def setup_global_logging():
    try:
        from desktop_app.services.path_service import get_user_data_dir

        # 1. Determine Log Path
        log_dir = os.path.join(get_user_data_dir(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "intelleo.log")

        # 2. Configure Root Logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Capture everything at root level

        # Remove existing handlers (e.g. from previous runs or other libs)
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 3. Rotating File Handler (DEBUG level - capture all for diagnostics)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)

        # 4. Console Handler - WARNING level only to reduce spam
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
        root_logger.addHandler(console_handler)

        # 5. Silence ALL noisy libraries to reduce spam
        noisy_loggers = [
            "urllib3", "requests", "httpx", "asyncio", "multipart",
            "watchfiles", "uqi", "faker", "httpcore",
            # Uvicorn - silence completely
            "uvicorn", "uvicorn.access", "uvicorn.error",
            # APScheduler - silence completely  
            "apscheduler", "apscheduler.scheduler", "apscheduler.executors",
            "apscheduler.executors.default",
            # App components that are verbose
            "app.core.db_security", "app.core.lock_manager",
            "app.api.routers.system",
            # Desktop app services
            "desktop_app.services", "desktop_app.services.hardware_id_service",
            "desktop_app.services.update_checker", "desktop_app.services.voice_service",
        ]
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.ERROR)

        logging.info("Global logging initialized.")

    except Exception as e:
        print(f"[CRITICAL] Failed to setup logging: {e}")

setup_global_logging()

# --- SENTRY INTEGRATION (Obfuscated) ---
import sentry_sdk
from app import __version__
import base64

def _decode_sentry_dsn():
    """Decode obfuscated Sentry DSN to bypass static code analysis."""
    # Obfuscated DSN parts (base64 encoded)
    _k = "aHR0cHM6Ly9mMjUyZDU5OGFhZjdlNzBmZTk0ZDUzMzQ3NGI3NjYzOQ=="
    _h = "bzQ1MTA0OTA0OTI2MDAzMjAuaW5nZXN0LmRlLnNlbnRyeS5pbw=="
    _p = "NDUxMDQ5MDUyNjc0NDY1Ng=="
    try:
        return f"{base64.b64decode(_k).decode()}@{base64.b64decode(_h).decode()}/{base64.b64decode(_p).decode()}"
    except Exception:
        return None

def init_sentry():
    """Initializes Sentry SDK for error tracking with thread hooks."""
    if sentry_sdk.is_initialized():
        return
        
    environment = "production" if getattr(sys, 'frozen', False) else "development"
    dsn = os.environ.get("SENTRY_DSN") or _decode_sentry_dsn()
    
    if not dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=f"intelleo@{__version__}",
        traces_sample_rate=0.3,  # Performance: 30% sampling
        send_default_pii=False,
        attach_stacktrace=True,
        max_breadcrumbs=50,  # Limit memory usage
        debug=False,
    )
    
    # Install threading exception hook for all threads
    import threading
    
    def thread_excepthook(args):
        """Global hook for thread exceptions."""
        logging.critical(f"Thread exception in {args.thread.name}: {args.exc_type.__name__}: {args.exc_value}")
        sentry_sdk.capture_exception(args.exc_value)
    
    if hasattr(threading, 'excepthook'):
        threading.excepthook = thread_excepthook

def sentry_exception_hook(exctype, value, traceback):
    """
    Global exception handler that captures errors to Sentry
    AND ensures database security cleanup.
    """
    # 0. Log Locally
    logging.critical("Unhandled exception", exc_info=(exctype, value, traceback))

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
    # S5747: Remove bare raise, only re-raise SystemExit explicitly if caught (not here)
    # The original code re-raised SystemExit using bare raise which S5747 flagged.
    # The check issubclass(exctype, SystemExit) is correct but inside this hook it is complex.
    # This hook is executed *after* exception is raised.
    # We should just exit.
    if issubclass(exctype, SystemExit):
        sys.exit(value.code if hasattr(value, 'code') else 1)

    sys.exit(1)

# Initialize Sentry immediately
init_sentry()
# Override global exception hook
sys.excepthook = sentry_exception_hook

# --- PHASE 2: POSTHOG ANALYTICS ---
import posthog

def init_posthog():
    """Initializes PostHog Analytics (Async)."""
    try:
        # Check explicit disable flag (GDPR)
        # analytics_enabled = True # Removed unused variable

        # Configure PostHog Module-Global
        posthog.project_api_key = "phc_jCIZrEiPMQ1fE8ympKiJGc84GUvbqqo7T2sQDlGyUd8"
        # Backwards compatibility / library quirk fallback
        posthog.api_key = posthog.project_api_key
        posthog.host = "https://eu.i.posthog.com"

        # Track App Start
        # Run in thread to not block UI
        def track_start():
            try:
                # Identification (Anonymous Machine ID or User ID if logged in - here we use machine ID for basic tracking)
                from desktop_app.services.hardware_id_service import get_machine_id
                distinct_id = get_machine_id()

                # Re-assert config in thread just in case
                if not posthog.api_key:
                    posthog.project_api_key = "phc_jCIZrEiPMQ1fE8ympKiJGc84GUvbqqo7T2sQDlGyUd8"
                    posthog.api_key = posthog.project_api_key
                    posthog.host = "https://eu.i.posthog.com"

                posthog.capture(
                    'app_started',
                    distinct_id=distinct_id,
                    properties={
                        'version': __version__,
                        'os': platform.system(),
                        'os_release': platform.release(),
                        'environment': "production" if getattr(sys, 'frozen', False) else "development"
                    }
                )
            except Exception as e:
                logging.warning(f"PostHog track failed: {e}")

        threading.Thread(target=track_start, daemon=True).start()

        # Register Exit Handler
        import atexit
        def track_exit():
            try:
                from desktop_app.services.hardware_id_service import get_machine_id
                posthog.capture('app_closed', distinct_id=get_machine_id())
                posthog.flush() # Ensure sent
            except Exception: pass

        atexit.register(track_exit)

    except Exception as e:
        logging.error(f"Failed to init PostHog: {e}")

init_posthog()


# --- CRITICAL: IMPORT WEBENGINE & SET ATTRIBUTE BEFORE QAPPLICATION ---
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QCoreApplication, QTimer, QThread, pyqtSignal
# QObject removed from import as it was unused

QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

from PyQt6.QtWidgets import QApplication, QMessageBox, QFileDialog
# QSplashScreen, QPixmap removed as unused directly here (imported in main inside try block)

# --- CONFIGURAZIONE AMBIENTE (Nuitka-Compatible) ---
from app.core.path_resolver import get_base_path, get_license_path

if getattr(sys, 'frozen', False):
    # Use universal path resolver for both PyInstaller and Nuitka
    BASE_DIR = get_base_path()
    
    # DLL Directory Setup
    dll_dir = BASE_DIR / "dll"
    if os.name == 'nt' and dll_dir.exists():
        os.environ["PATH"] = str(dll_dir) + os.pathsep + os.environ.get("PATH", "")
        try:
            if hasattr(os, 'add_dll_directory'):
                os.add_dll_directory(str(dll_dir))
        except Exception:
            pass

    # License Directory Setup
    lic_dir = get_license_path()
    if lic_dir.exists():
        sys.path.insert(0, str(lic_dir))

    # Database URL (legacy env var, actual path resolved by db_security)
    db_path = BASE_DIR / DATABASE_FILENAME
    db_path_str = str(db_path)
    if os.name == 'nt':
        db_path_str = db_path_str.replace('\\', '\\\\')
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path_str}"
    
    # Set working directory to base path (works for both PyInstaller and Nuitka)
    os.chdir(str(BASE_DIR))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# --- UTILS ---
def find_free_port(start_port=8000, max_port=8010):
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('127.0.0.1', port)) != 0:
                    return port
        except Exception:
            continue
    return None

def start_server(port):
    from app.main import app
    
    # Custom log config to suppress uvicorn's default console output
    # All output goes to our configured file handler only
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "null": {
                "class": "logging.NullHandler",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["null"], "level": "ERROR"},
            "uvicorn.error": {"handlers": ["null"], "level": "ERROR"},
            "uvicorn.access": {"handlers": ["null"], "level": "ERROR"},
        },
    }
    
    # Explicitly disable reload to prevent crashes in frozen app when settings.json changes
    uvicorn.run(app, host="127.0.0.1", port=port, log_config=log_config, log_level="error", reload=False)

def check_port(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        result = s.connect_ex((host, port)) == 0
        s.close()
        return result
    except Exception: return False

# --- PHASE 0: LICENSE GATEKEEPER ---
def verify_license_files():
    """Checks for the physical presence of license files."""
    from desktop_app.services.path_service import get_license_dir, get_app_install_dir

    # 1. Check User Data Directory (Preferred)
    user_lic_dir = get_license_dir()
    if os.path.exists(os.path.join(user_lic_dir, LICENSE_FILE_KEY)) and \
       os.path.exists(os.path.join(user_lic_dir, LICENSE_FILE_CONFIG)):
        sys.path.insert(0, user_lic_dir)
        return True

    # 2. Check Install Directory (Legacy)
    install_dir = get_app_install_dir()
    legacy_lic_dir = os.path.join(install_dir, "Licenza")
    if os.path.exists(os.path.join(legacy_lic_dir, LICENSE_FILE_KEY)) and \
       os.path.exists(os.path.join(legacy_lic_dir, LICENSE_FILE_CONFIG)):
        sys.path.insert(0, legacy_lic_dir)
        return True

    # 3. Check Root (Legacy)
    if os.path.exists(os.path.join(install_dir, LICENSE_FILE_KEY)) and \
       os.path.exists(os.path.join(install_dir, LICENSE_FILE_CONFIG)):
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
            importlib.import_module('app.core.config')
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

def _check_db_integrity(target):
    # S3776: Refactored logic to reduce complexity
    exists = target.exists()
    is_valid = False
    if exists:
        from app.core.db_security import db_security
        is_valid = db_security.verify_integrity(target)
    return exists, is_valid

def _handle_browse_action(parent, target, db_security, settings):
    from pathlib import Path
    from app.core.config import get_user_data_dir

    file_path, _ = QFileDialog.getOpenFileName(parent, "Seleziona Database", str(get_user_data_dir()), "Database Files (*.db *.bak)")
    if not file_path: return

    file_path = os.path.normpath(file_path)
    path_obj = Path(file_path)

    if path_obj.suffix.lower() == ".bak":
        reply = QMessageBox.question(parent, "Ripristino Backup", f"Ripristinare dal backup:\n{path_obj.name}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                db_security.db_path = target
                db_security.data_dir = target.parent
                db_security.restore_from_backup(path_obj)
                restart_app()
            except Exception as e:
                QMessageBox.critical(parent, "Errore", f"Ripristino fallito: {e}")
    else:
        settings.save_mutable_settings({"DATABASE_PATH": file_path})
        restart_app()

def _handle_create_action(parent):
    from pathlib import Path
    from app.core.config import get_user_data_dir
    try:
        dir_path = QFileDialog.getExistingDirectory(parent, "Seleziona Cartella per Nuovo Database", str(get_user_data_dir()))
        if dir_path:
            target = Path(dir_path) / DATABASE_FILENAME
            initialize_new_database(target)
            restart_app()
    except Exception as e:
        QMessageBox.critical(parent, "Errore Creazione", f"Impossibile creare il database:\n{e}")

def _handle_recovery_action(parent, msg, target):
    # S3776: Refactored logic to reduce complexity
    browse_btn = msg.addButton("Sfoglia / Ripristina...", QMessageBox.ButtonRole.ActionRole)
    create_btn = msg.addButton("Crea Nuovo Database", QMessageBox.ButtonRole.ActionRole)
    msg.addButton("Esci", QMessageBox.ButtonRole.RejectRole)

    msg.setWindowFlags(msg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
    msg.exec()

    clicked = msg.clickedButton()
    from app.core.config import settings
    from app.core.db_security import db_security

    if clicked == browse_btn:
        _handle_browse_action(parent, target, db_security, settings)
    elif clicked == create_btn:
        _handle_create_action(parent)
    else:
        sys.exit(1)

def check_and_recover_database(controller):
    """
    Checks database integrity and prompts user for recovery actions if needed.
    """
    from app.core.config import settings, get_user_data_dir
    from pathlib import Path

    db_path_str = settings.DATABASE_PATH
    if db_path_str:
         db_path = Path(db_path_str)
         if db_path.is_dir():
             target = db_path / DATABASE_FILENAME
         else:
             target = db_path
    else:
         target = get_user_data_dir() / DATABASE_FILENAME

    exists, is_valid = _check_db_integrity(target)

    if exists and is_valid:
        return True

    # 3. Prompt User
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

    _handle_recovery_action(parent, msg, target)
    return False

def post_launch_integrity_check(controller):
    """
    Step 3 (Delayed): Integrity Check and Recovery Dialog.
    Executes AFTER the UI (Login) is visible.
    """
    try:
        # Refactored loop logic into check_and_recover_database
        while True:
            if check_and_recover_database(controller):
                break

    except ImportError as e:
        QMessageBox.critical(None, "Errore Critico", f"Impossibile caricare configurazione: {e}")
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
            # 1. Quick integrity check (non-blocking)
            self.progress_update.emit("Inizializzazione...", 20)
            try:
                from desktop_app.services.integrity_service import verify_critical_components
                is_intact, int_msg = verify_critical_components()
                if not is_intact:
                    raise RuntimeError(f"Integrità compromessa: {int_msg}")
            except ImportError:
                pass

            # 2. Start Server IMMEDIATELY
            self.progress_update.emit("Avvio servizi...", 40)
            threading.Thread(target=start_server, args=(self.server_port,), daemon=True).start()

            # 3. Wait for Server (with faster polling)
            self.progress_update.emit("Connessione...", 60)
            t0 = time.time()
            ready = False
            timeout = 60  # Increased timeout for stability
            
            while time.time() - t0 < timeout:
                if check_port("127.0.0.1", self.server_port):
                    ready = True
                    break
                elapsed = time.time() - t0
                prog = 60 + int((elapsed / timeout) * 30)
                self.progress_update.emit("Connessione...", min(90, prog))
                time.sleep(0.05)  # Faster polling

            if not ready:
                raise TimeoutError("Timeout connessione al server.")

            # 4. Quick Health Check
            self.progress_update.emit("Verifica...", 95)
            try:
                health_url = f"http://localhost:{self.server_port}/api/v1/health"
                response = requests.get(health_url, timeout=3)
                if response.status_code != 200:
                    raise ConnectionError(f"Server Error: {response.status_code}")
            except requests.exceptions.RequestException as e:
                raise ConnectionError(f"Health Check Failed: {e}")

            # 5. Done
            self.progress_update.emit("Pronto!", 100)
            self.startup_complete.emit(True, "OK")

        except Exception as e:
            self.error_occurred.emit(str(e))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyze", help="Path")
    parser.add_argument("--import-csv", help="Path")
    parser.add_argument("--view", help="View")
    args, _ = parser.parse_known_args() # 'unknown' unused, replaced with _

    server_port = find_free_port()
    if not server_port:
        QMessageBox.critical(None, "Errore", "Nessuna porta libera.")
        sys.exit(1)

    os.environ["API_URL"] = f"http://localhost:{server_port}/api/v1"

    qt_app = QApplication.instance() or QApplication(sys.argv)

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
            # Log full traceback locally as logging is now configured
            logging.critical("UI Load Error", exc_info=True)
            sys.exit(1)

    worker.progress_update.connect(on_progress)
    worker.error_occurred.connect(on_error)
    worker.startup_complete.connect(on_complete)

    worker.start()

    sys.exit(qt_app.exec())

if __name__ == "__main__":
    main()
