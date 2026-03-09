import os
import sys
import datetime
import traceback


def crash_handler(etype, value, tb_obj):
    """Gestore globale per i crash dell'applicazione."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_msg = "".join(traceback.format_exception(etype, value, tb_obj))

    crash_info = f"""
============================================================
CRASH REPORT - {timestamp}
============================================================
Versione Python: {sys.version}
Sistema: {sys.platform}
PYTHONPATH: {os.environ.get("PYTHONPATH", "N/D")}

ERRORE:
{error_msg}
============================================================
"""
    try:
        with open("CRASH_REPORT.txt", "a", encoding="utf-8") as f:
            f.write(crash_info)
    except Exception:
        pass
    sys.exit(1)


# REGISTRAZIONE IMMEDIATA
sys.excepthook = crash_handler

import logging
import logging.handlers
import socket
import threading
import time
import uvicorn

from app.core.path_resolver import get_base_path

# Setup logging
log_file = os.path.join(get_base_path(), "app.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.handlers.RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3),
        logging.StreamHandler(sys.stdout) if sys.stdout else logging.NullHandler(),
    ],
)
logger = logging.getLogger("launcher")


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def start_server():
    try:
        from app.main import app

        config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
        server = uvicorn.Server(config)
        server.run()
    except Exception:
        # Questo cattura errori nel thread del server
        etype, value, tb_obj = sys.exc_info()
        crash_handler(etype, value, tb_obj)


def main() -> None:
    logger.info("Avvio sistema Intelleo...")

    # 1. Start FastAPI Backend in background thread
    if not is_port_in_use(8000):
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()

        # Wait for server to be ready
        retries = 0
        while not is_port_in_use(8000) and retries < 10:
            time.sleep(1)
            retries += 1
    else:
        logger.info("Server già in esecuzione sulla porta 8000")

    # 2. Check for updates or other tasks could go here

    # 3. Start PySide6 Frontend
    try:
        from PySide6.QtWidgets import QApplication
        from desktop_app.main import ApplicationController

        qt_app = QApplication(sys.argv)
        qt_app.setStyle("Fusion")

        controller = ApplicationController()
        controller.start()

        sys.exit(qt_app.exec())
    except Exception:
        etype, value, tb_obj = sys.exc_info()
        crash_handler(etype, value, tb_obj)


if __name__ == "__main__":
    main()
