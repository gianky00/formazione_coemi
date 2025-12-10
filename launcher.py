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
LICENSE_FILE_CONFIG = "config.dat"

# --- PHASE 2: LOGGING CONFIGURATION ---
def setup_global_logging():
    try:
        from desktop_app.services.path_service import get_user_data_dir

        log_dir = os.path.join(get_user_data_dir(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "intelleo.log")

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding='utf-8'
        )
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.WARNING)
        root_logger.addHandler(console_handler)

        noisy_loggers = [
            "urllib3", "requests", "httpx", "asyncio", "multipart",
            "watchfiles", "uqi", "faker", "httpcore",
            "uvicorn", "uvicorn.access", "uvicorn.error",
            "apscheduler", "apscheduler.scheduler", "apscheduler.executors",
            "apscheduler.executors.default",
            "app.core.db_security", "app.core.lock_manager",
            "app.api.routers.system",
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
    _k = "aHR0cHM6Ly9mMjUyZDU5OGFhZjdlNzBmZTk0ZDUzMzQ3NGI3NjYzOQ=="
    _h = "bzQ1MTA0OTA0OTI2MDAzMjAuaW5nZXN0LmRlLnNlbnRyeS5pbw=="
    _p = "NDUxMDQ5MDUyNjc0NDY1Ng=="
    try:
        return f"{base64.b64decode(_k).decode()}@{base64.b64decode(_h).decode()}/{base64.b64decode(_p).decode()}"
    except Exception:
        return None

def init_sentry():
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
        traces_sample_rate=0.3,
        send_default_pii=False,
        attach_stacktrace=True,
        max_breadcrumbs=50,
        debug=False,
    )
    
    import threading
    
    def thread_excepthook(args):
        logging.critical(f"Thread exception in {args.thread.name}: {args.exc_type.__name__}: {args.exc_value}")
        sentry_sdk.capture_exception(args.exc_value)
    
    if hasattr(threading, 'excepthook'):
        threading.excepthook = thread_excepthook

def sentry_exception_hook(exctype, value, traceback):
    logging.critical("Unhandled exception", exc_info=(exctype, value, traceback))
    sentry_sdk.capture_exception(value)
    print(f"[CRITICAL] Unhandled exception: {exctype}, {value}")
    tb.print_tb(traceback)

    try:
        from app.core.db_security import db_security
        print("[CRITICAL] Attempting emergency DB cleanup...")
        db_security.cleanup()
    except Exception as e:
        print(f"[CRITICAL] Emergency cleanup failed: {e}")
        sentry_sdk.capture_exception(e)

    if issubclass(exctype, SystemExit):
        sys.exit(value.code if hasattr(value, 'code') else 1)

    sys.exit(1)

init_sentry()
sys.excepthook = sentry_exception_hook

# --- CRITICAL: IMPORT WEBENGINE & SET ATTRIBUTE BEFORE QAPPLICATION ---
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QCoreApplication, QTimer, QThread, pyqtSignal

QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

from PyQt6.QtWidgets import QApplication, QMessageBox, QFileDialog

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

    db_path = os.path.join(EXE_DIR, DATABASE_FILENAME)
    if os.name == 'nt': db_path = db_path.replace('\\', '\\\\')
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    
    # Nuitka compatibility
    # sys._MEIPASS is not used in Nuitka standalone, we use EXE_DIR
    os.chdir(EXE_DIR)

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
    
    uvicorn.run(app, host="127.0.0.1", port=port, log_config=log_config, log_level="error", reload=False)

def check_port(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        result = s.connect_ex((host, port)) == 0
        s.close()
        return result
    except Exception: return False

# --- PHASE 0: LICENSE GATEKEEPER (PYTHON NATIVE) ---

def verify_license_logic():
    """
    Validates the license explicitly in Python using decryption.
    """
    from desktop_app.services.license_manager import LicenseManager
    from desktop_app.services.hardware_id_service import get_machine_id
    from desktop_app.constants import LABEL_HARDWARE_ID

    # 1. Read & Decrypt
    license_data = LicenseManager.get_license_data()
    if not license_data:
        logging.warning("License file missing or corrupt.")
        return False

    # 2. Verify Content (Hardware ID)
    stored_hw_id = license_data.get(LABEL_HARDWARE_ID)
    current_hw_id = get_machine_id()

    if not stored_hw_id or stored_hw_id != current_hw_id:
        logging.warning(f"Hardware ID mismatch. Stored: {stored_hw_id}, Current: {current_hw_id}")
        return False

    # 3. Expiry Check (Optional - we might allow expired to open but show warning,
    # but for strict gatekeeper, we could block.
    # Current logic: Gatekeeper ensures valid signature/machine binding.
    # Expiry is handled by UI warnings in LoginView.)

    logging.info("License verified successfully.")
    return True

def check_license_gatekeeper(splash):
    """
    Step 0: Strict License Check.
    If license is missing or invalid (HWID mismatch), launch Recovery Mode.
    """
    splash.update_status("Controllo Licenza...", 5)
    QApplication.processEvents()

    if verify_license_logic():
        return # Proceed

    # --- LICENSE INVALID/MISSING: RECOVERY MODE ---
    splash.hide() # Hide splash to show blocking dialog

    # Launch Recovery Dialog
    from desktop_app.views.recovery_dialog import RecoveryDialog

    dialog = RecoveryDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        # Restart Application on success
        python = sys.executable
        os.execl(python, python, *sys.argv)
    else:
        # User cancelled or failed
        sys.exit(1)

# --- PHASE 2: DATABASE INTEGRITY & RECOVERY ---

def initialize_new_database(path_obj):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.db.models import Base
    from app.db.seeding import seed_database
    from app.core.config import settings

    conn = sqlite3.connect(str(path_obj))
    conn.execute("PRAGMA journal_mode=DELETE;")
    conn.execute("PRAGMA synchronous=FULL;")
    conn.commit()
    conn.close()

    db_url = f"sqlite:///{path_obj}"
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    settings.save_mutable_settings({"DATABASE_PATH": str(path_obj)})

def _check_db_integrity(target):
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
    try:
        while True:
            if check_and_recover_database(controller):
                break

    except ImportError as e:
        QMessageBox.critical(None, "Errore Critico", f"Impossibile caricare configurazione: {e}")
        sys.exit(1)

def restart_app():
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
            self.progress_update.emit("Inizializzazione...", 20)
            try:
                from desktop_app.services.integrity_service import verify_critical_components
                is_intact, int_msg = verify_critical_components()
                if not is_intact:
                    raise RuntimeError(f"Integrità compromessa: {int_msg}")
            except ImportError:
                pass

            self.progress_update.emit("Avvio servizi...", 40)
            threading.Thread(target=start_server, args=(self.server_port,), daemon=True).start()

            self.progress_update.emit("Connessione...", 60)
            t0 = time.time()
            ready = False
            timeout = 60
            
            while time.time() - t0 < timeout:
                if check_port("127.0.0.1", self.server_port):
                    ready = True
                    break
                elapsed = time.time() - t0
                prog = 60 + int((elapsed / timeout) * 30)
                self.progress_update.emit("Connessione...", min(90, prog))
                time.sleep(0.05)

            if not ready:
                raise TimeoutError("Timeout connessione al server.")

            self.progress_update.emit("Verifica...", 95)
            try:
                health_url = f"http://localhost:{self.server_port}/api/v1/health"
                response = requests.get(health_url, timeout=3)
                if response.status_code != 200:
                    raise ConnectionError(f"Server Error: {response.status_code}")
            except requests.exceptions.RequestException as e:
                raise ConnectionError(f"Health Check Failed: {e}")

            self.progress_update.emit("Pronto!", 100)
            self.startup_complete.emit(True, "OK")

        except Exception as e:
            self.error_occurred.emit(str(e))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyze", help="Path")
    parser.add_argument("--import-csv", help="Path")
    parser.add_argument("--view", help="View")
    args, _ = parser.parse_known_args()

    server_port = find_free_port()
    if not server_port:
        QMessageBox.critical(None, "Errore", "Nessuna porta libera.")
        sys.exit(1)

    os.environ["API_URL"] = f"http://localhost:{server_port}/api/v1"

    qt_app = QApplication.instance() or QApplication(sys.argv)

    try:
        from desktop_app.views.splash_screen import CustomSplashScreen
        splash = CustomSplashScreen()
        splash.show()
    except Exception as e:
        QMessageBox.critical(None, "Errore", f"Splash Error: {e}")
        sys.exit(1)

    # --- STRICT LICENSE CHECK (RECOVERY MODE) ---
    check_license_gatekeeper(splash)

    # Proceed if valid
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

            post_launch_integrity_check(controller)

        except Exception as e:
            splash.show_error(f"Errore caricamento interfaccia: {e}")
            logging.critical("UI Load Error", exc_info=True)
            sys.exit(1)

    worker.progress_update.connect(on_progress)
    worker.error_occurred.connect(on_error)
    worker.startup_complete.connect(on_complete)

    worker.start()

    sys.exit(qt_app.exec())

if __name__ == "__main__":
    main()
