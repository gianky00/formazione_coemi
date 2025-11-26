import os
import json
import logging
from cryptography.fernet import Fernet
from app.core.license_security import LICENSE_SECRET_KEY
from desktop_app.services.path_service import get_license_dir, get_app_install_dir
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class LicenseManager:
    LICENSE_FILENAME = "config.dat"

    @staticmethod
    def get_license_data():
        """
        Reads and decrypts the license data from config.dat.
        Returns a dictionary or None if failed.
        """
        file_path = LicenseManager._find_license_file()
        if not file_path:
            logger.warning(f"License file {LicenseManager.LICENSE_FILENAME} not found.")
            return None

        try:
            with open(file_path, "rb") as f:
                encrypted_data = f.read()

            cipher = Fernet(LICENSE_SECRET_KEY)
            decrypted_data = cipher.decrypt(encrypted_data)

            data = json.loads(decrypted_data.decode('utf-8'))
            return data

        except Exception as e:
            logger.error(f"Failed to decrypt license file: {e}")
            return None

    @staticmethod
    def _find_license_file():
        """
        Tries to find the license file in priority order:
        1. New user data directory (writable).
        2. Old application installation directory (for backward compatibility).
        """
        filename = LicenseManager.LICENSE_FILENAME

        # 1. New, preferred location in user data directory
        user_license_path = os.path.join(get_license_dir(), filename)
        if os.path.exists(user_license_path):
            logger.info(f"License found in user data directory: {user_license_path}")
            return user_license_path

        # 2. Fallback to old location in installation directory
        install_dir = get_app_install_dir()
        old_license_path = os.path.join(install_dir, "Licenza", filename)
        if os.path.exists(old_license_path):
            logger.info(f"License found in fallback install directory: {old_license_path}")
            return old_license_path

        # Also check root of install dir, just in case
        old_root_path = os.path.join(install_dir, filename)
        if os.path.exists(old_root_path):
            logger.info(f"License found in fallback install root: {old_root_path}")
            return old_root_path

        logger.warning("License file could not be found in any standard location.")
        return None

    @staticmethod
    def is_license_expiring_soon(license_data, days=7):
        """
        Checks if the license is expiring within the given number of days.
        """
        if not license_data or "Scadenza Licenza" not in license_data:
            return False

        try:
            expiry_date = datetime.strptime(license_data["Scadenza Licenza"], "%d/%m/%Y")
            now = datetime.now()
            return now < expiry_date < now + timedelta(days=days)
        except (ValueError, TypeError):
            return False
