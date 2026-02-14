import argparse
import logging
import logging.handlers
import os
import socket
import sys
import threading
import time
import traceback as tb

import uvicorn

from app.core.path_resolver import get_base_path, get_license_path

# REMOVED: sys.setrecursionlimit(5000) - Code smell removed.
# If RecursionError occurs, investigate infinite loops in sync_service or UI tree.

# Constants
DATABASE_FILENAME = "database_documenti.db"
LICENSE_FILE_KEY = "pyarmor.rkey"
LICENSE_FILE_CONFIG = "config.dat"


# --- PHASE 2: LOGGING CONFIGURATION ---
def setup_global_logging() -> None:
    try:
        from desktop_app.services.path_service import get_user_data_dir

        # 1. Determine Log Path
        log_dir = os.path.join(get_user_data_dir(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "intelleo.log")

        # 2. Configure Root Logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Capture everything at root level

        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 3. Rotating File Handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding="utf-8",
        )
        file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)

        # 4. Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.WARNING)
        root_logger.addHandler(console_handler)

        # 5. Silence ALL noisy libraries
        noisy_loggers = [
            "urllib3",
            "requests",
            "httpx",
            "asyncio",
            "multipart",
            "watchfiles",
            "uqi",
            "faker",
            "httpcore",
            "uvicorn",
            "uvicorn.access",
            "uvicorn.error",
            "apscheduler",
            "apscheduler.scheduler",
            "apscheduler.executors",
            "apscheduler.executors.default",
            "app.core.db_security",
            "app.core.lock_manager",
            "app.api.routers.system",
        ]
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.ERROR)

        logging.info("Global logging initialized.")

    except Exception:
        pass


setup_global_logging()

# --- CONFIGURAZIONE AMBIENTE (Nuitka-Compatible) ---


if getattr(sys, "frozen", False):
    BASE_DIR = get_base_path()

    # DLL Directory Setup
    dll_dir = BASE_DIR / "dll"
    if os.name == "nt" and dll_dir.exists():
        os.environ["PATH"] = str(dll_dir) + os.pathsep + os.environ.get("PATH", "")
        try:
            if hasattr(os, "add_dll_directory"):
                os.add_dll_directory(str(dll_dir))
        except Exception:
            pass

    # License Directory Setup
    lic_dir = get_license_path()
    if lic_dir.exists():
        sys.path.insert(0, str(lic_dir))

    # Database URL
    db_path = BASE_DIR / DATABASE_FILENAME
    db_path_str = str(db_path)
    if os.name == "nt":
        db_path_str = db_path_str.replace("\\", "\\\\")
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path_str}"

    os.chdir(str(BASE_DIR))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# --- UTILS ---
def find_free_port(start_port: int = 8000, max_port: int = 8010) -> int | None:
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("127.0.0.1", port)) != 0:
                    return port
        except Exception:
            continue
    return None


def start_server(port: int) -> None:
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

    uvicorn.run(
        app, host="127.0.0.1", port=port, log_config=log_config, log_level="error", reload=False
    )


def check_port(host: str, port: int) -> bool:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        result = s.connect_ex((host, port)) == 0
        s.close()
        return result
    except Exception:
        return False


def verify_license_files() -> bool:
    """Verifica la presenza dei file di licenza minimi necessari per l'avvio."""
    lic_dir = get_license_path()
    # config.dat è obbligatorio, pyarmor.rkey è consigliato ma obbligatorio per licenze attive
    required = [LICENSE_FILE_CONFIG, LICENSE_FILE_KEY]
    return all((lic_dir / f).exists() for f in required)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyze", help="Path")
    parser.add_argument("--import-csv", help="Path")
    parser.add_argument("--view", help="View")
    _args, _ = parser.parse_known_args()

    # 0. Verify License
    if not verify_license_files():
        sys.exit(1)

    # 1. Start Backend in separate thread
    server_port = find_free_port()
    if not server_port:
        sys.exit(1)

    os.environ["API_URL"] = f"http://localhost:{server_port}/api/v1"

    server_thread = threading.Thread(target=start_server, args=(server_port,), daemon=True)
    server_thread.start()

    # 2. Wait for server (Blocking wait, simple)
    t0 = time.time()
    ready = False
    while time.time() - t0 < 60:
        if check_port("127.0.0.1", server_port):
            ready = True
            break
        time.sleep(0.1)

    if not ready:
        sys.exit(1)

    # 3. Start Tkinter Frontend
    try:
        from desktop_app.main import ApplicationController

        app = ApplicationController()
        app.start()
    except Exception:
        tb.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
