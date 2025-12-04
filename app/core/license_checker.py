import os
import json
import logging
from datetime import datetime
from cryptography.fernet import Fernet
from app.core.license_security import get_license_secret_key
from app.core.config import get_user_data_dir

logger = logging.getLogger(__name__)

class LicenseChecker:
    LICENSE_FILENAME = "config.dat"

    @staticmethod
    def get_license_data():
        # Check User Data Directory
        user_license_path = get_user_data_dir() / "Licenza" / LicenseChecker.LICENSE_FILENAME

        if not user_license_path.exists():
            # Check legacy/install locations relative to cwd if needed
            # Assuming CWD is root of app
            legacy_path = os.path.join("Licenza", LicenseChecker.LICENSE_FILENAME)
            if os.path.exists(legacy_path):
                user_license_path = legacy_path
            elif os.path.exists(LicenseChecker.LICENSE_FILENAME):
                user_license_path = LicenseChecker.LICENSE_FILENAME
            else:
                return None

        try:
            with open(user_license_path, "rb") as f:
                encrypted_data = f.read()

            cipher = Fernet(get_license_secret_key())
            decrypted_data = cipher.decrypt(encrypted_data)
            data = json.loads(decrypted_data.decode('utf-8'))
            return data
        except Exception as e:
            logger.error(f"License check failed: {e}")
            return None

    @staticmethod
    def is_license_valid():
        data = LicenseChecker.get_license_data()
        if not data: return False

        expiry_str = data.get("Scadenza Licenza")
        if not expiry_str: return False

        try:
            # Handle formats
            if '/' in expiry_str:
                d, m, y = map(int, expiry_str.split('/'))
            elif '-' in expiry_str:
                y, m, d = map(int, expiry_str.split('-'))
            else:
                return False

            expiry_date = datetime(y, m, d).date()
            if datetime.now().date() > expiry_date:
                return False

            return True
        except:
            return False
