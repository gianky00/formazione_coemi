import socket
import struct
import time
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

NTP_SERVER = "pool.ntp.org"
TIME1970 = 2208988800  # Reference time

def get_network_time():
    """
    Fetches the current time from an NTP server.
    Returns a datetime object or None if it fails.
    """
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.settimeout(2)  # 2-second timeout
        data = b'\x1b' + 47 * b'\0'
        client.sendto(data, (NTP_SERVER, 123))
        data, address = client.recvfrom(1024)
        if data:
            t = struct.unpack('!12I', data)[10]
            t -= TIME1970
            return datetime.fromtimestamp(t)
    except (socket.timeout, socket.gaierror) as e:
        logger.warning(f"NTP time check failed: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during NTP check: {e}")
        return None
    return None

def check_system_clock():
    """
    Compares the system clock to network time.
    Returns True if the clock is reasonably accurate, False otherwise.
    """
    network_time = get_network_time()
    if not network_time:
        # If we can't get network time, we can't validate.
        # For security, we could fail here, but for usability, we might allow it.
        # Let's be strict: if we can't check, it's a failure.
        return False, "Impossibile verificare l'ora del sistema. Controllare la connessione a Internet."

    system_time = datetime.now()
    time_difference = abs((network_time - system_time).total_seconds())

    # Allow a tolerance of 5 minutes (300 seconds)
    if time_difference > 300:
        return False, f"L'orologio del sistema non è sincronizzato (differenza di {int(time_difference / 60)} minuti).\n" \
                      "Sincronizzare l'ora del sistema per continuare."

    return True, "OK"
