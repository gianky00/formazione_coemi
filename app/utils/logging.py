import logging
import sys

def setup_logging():
    """
    Configures logging for the application.
    - Console: WARNING level for cleaner output.
    - File: DEBUG level, detailed format.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='intelleo_debug.log',
        filemode='w'
    )

    # Console handler - set to WARNING to reduce spam
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)

    # Add the console handler to the root logger
    logging.getLogger('').addHandler(console_handler)

    # Silence noisy libraries completely
    logging.getLogger("uvicorn").setLevel(logging.ERROR)
    logging.getLogger("uvicorn.access").setLevel(logging.ERROR)
    logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
    logging.getLogger("faker").setLevel(logging.ERROR)
    logging.getLogger("apscheduler").setLevel(logging.ERROR)
    logging.getLogger("apscheduler.scheduler").setLevel(logging.ERROR)
    logging.getLogger("apscheduler.executors").setLevel(logging.ERROR)
    
    # Reduce db_security and lock_manager verbosity
    logging.getLogger("app.core.db_security").setLevel(logging.WARNING)
    logging.getLogger("app.core.lock_manager").setLevel(logging.WARNING)
    
    # Desktop app services
    logging.getLogger("desktop_app.services").setLevel(logging.WARNING)
    logging.getLogger("desktop_app.services.hardware_id_service").setLevel(logging.WARNING)
    logging.getLogger("desktop_app.services.update_checker").setLevel(logging.WARNING)
    logging.getLogger("desktop_app.services.voice_service").setLevel(logging.WARNING)
