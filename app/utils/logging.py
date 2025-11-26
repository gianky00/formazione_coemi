import logging
import sys

def setup_logging():
    """
    Configures logging for the application.
    - Console: INFO level, simple format.
    - File: DEBUG level, detailed format.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='intelleo_debug.log',
        filemode='w'
    )

    # Console handler with a higher log level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)

    # Add the console handler to the root logger
    logging.getLogger('').addHandler(console_handler)

    # Silence noisy libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("faker").setLevel(logging.WARNING)
