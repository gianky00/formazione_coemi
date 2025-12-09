import logging
import sys
import os

def setup_logging():
    """
    Configures logging for the application.
    - Console: INFO level, simple format.
    - File: DEBUG level, detailed format.
    """
    try:
        from desktop_app.services.path_service import get_user_data_dir

        # 1. Determine Log Path
        log_dir = os.path.join(get_user_data_dir(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "intelleo.log")

        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.INFO)

        # FORCE RESET: Clear any existing handlers
        if root_logger.handlers:
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

        # 2. File Handler (Rotating)
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024, # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)

        # 3. Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

        # 4. Silence noisy libraries
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("faker").setLevel(logging.WARNING)
        logging.getLogger("watchfiles").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)
        logging.getLogger("multipart").setLevel(logging.WARNING)
        logging.getLogger("uqi").setLevel(logging.WARNING)

        logging.info("Global logging initialized via app.utils.logging")

    except Exception as e:
        print(f"[CRITICAL] Failed to setup logging in app.utils.logging: {e}")
