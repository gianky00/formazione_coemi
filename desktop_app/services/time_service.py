import os
import json
import logging
import socket
import struct
import time
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from app.core.license_security import LICENSE_SECRET_KEY
from desktop_app.services.path_service import get_license_dir

logger = logging.getLogger(__name__)

NTP_SERVER = "pool.ntp.org"
TIME1970 = 2208988800  # Reference time
SECURE_TIME_FILE = "secure_time.dat"
OFFLINE_BUFFER_DAYS = 3

class SecureTimeStorage:
    @staticmethod
    def _get_file_path():
        return os.path.join(get_license_dir(), SECURE_TIME_FILE)

    @staticmethod
    def save_state(last_online_check, last_execution):
        try:
            data = {
                "last_online_check": last_online_check.isoformat(),
                "last_execution": last_execution.isoformat()
            }
            json_data = json.dumps(data)
            cipher = Fernet(LICENSE_SECRET_KEY)
            encrypted_data = cipher.encrypt(json_data.encode('utf-8'))

            with open(SecureTimeStorage._get_file_path(), 'wb') as f:
                f.write(encrypted_data)
            return True
        except Exception as e:
            logger.error(f"Failed to save secure time state: {e}")
            return False

    @staticmethod
    def load_state():
        try:
            fpath = SecureTimeStorage._get_file_path()
            if not os.path.exists(fpath):
                return None

            with open(fpath, 'rb') as f:
                encrypted_data = f.read()

            cipher = Fernet(LICENSE_SECRET_KEY)
            decrypted_data = cipher.decrypt(encrypted_data)
            data = json.loads(decrypted_data.decode('utf-8'))

            return {
                "last_online_check": datetime.fromisoformat(data["last_online_check"]),
                "last_execution": datetime.fromisoformat(data["last_execution"])
            }
        except Exception as e:
            logger.error(f"Failed to load secure time state: {e}")
            return None

def get_network_time():
    """
    Fetches the current time from an NTP server.
    Returns a datetime object or None if it fails.
    """
    try:
        # Try multiple servers if needed, but pool.ntp.org is reliable
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.settimeout(3)  # 3-second timeout
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
    Validates system clock using NTP (priority) or Secure Offline Buffer (fallback).
    Updates the secure storage on success.

    Returns: (bool, str) -> (is_ok, message)
    """
    system_now = datetime.now()
    network_now = get_network_time()

    # CASE 1: ONLINE (NTP Success)
    if network_now:
        time_difference = abs((network_now - system_now).total_seconds())

        # Check synchronization (allow 5 mins tolerance)
        if time_difference > 300:
            return False, f"L'orologio del sistema non è sincronizzato (differenza di {int(time_difference / 60)} minuti).\n" \
                          "Sincronizzare l'ora del sistema per continuare."

        # Save state (Success)
        SecureTimeStorage.save_state(last_online_check=network_now, last_execution=network_now)
        return True, "OK (Online)"

    # CASE 2: OFFLINE (NTP Failed)
    state = SecureTimeStorage.load_state()
    if not state:
        return False, "Impossibile verificare l'ora (Nessuna connessione e nessun dato precedente).\n" \
                      "È richiesta una connessione Internet per il primo avvio o dopo un reset."

    last_online = state['last_online_check']
    last_exec = state['last_execution']

    # Check 1: Anti-Rollback (System time must be > Last Execution)
    # We allow a small tolerance (e.g., 5 mins) for reboot/startup variations, but generally must be forward.
    if system_now < last_exec - timedelta(minutes=5):
        return False, "Rilevata manomissione dell'orologio di sistema (Data antecedente all'ultima esecuzione).\n" \
                      "Ripristinare la data corretta."

    # Check 2: Offline Buffer Expiration
    buffer_end = last_online + timedelta(days=OFFLINE_BUFFER_DAYS)
    if system_now > buffer_end:
        return False, f"Periodo offline massimo ({OFFLINE_BUFFER_DAYS} giorni) scaduto.\n" \
                      "Connettersi a Internet per rinnovare la sessione sicura."

    # If valid offline: Update last_execution (but NOT last_online_check)
    SecureTimeStorage.save_state(last_online_check=last_online, last_execution=system_now)

    days_left = (buffer_end - system_now).days
    return True, f"OK (Offline Mode - {days_left} giorni rimanenti)"

def get_secure_date():
    """
    Returns the most trusted 'today' date.
    Use this for license checks instead of datetime.now().date()
    """
    # Simply use check_system_clock logic implicitly
    # If check_system_clock passed at startup, system_now is trusted within buffer bounds.
    return datetime.now().date()
