import os
import sys
import json
import logging
from cryptography.fernet import Fernet
from app.core.license_security import LICENSE_SECRET_KEY

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
        filename = LicenseManager.LICENSE_FILENAME

        # Priority locations
        possible_paths = [
             os.path.join("Licenza", filename),
             filename
        ]

        if getattr(sys, 'frozen', False):
             exe_dir = os.path.dirname(sys.executable)
             possible_paths.insert(0, os.path.join(exe_dir, "Licenza", filename))
             possible_paths.insert(1, os.path.join(exe_dir, filename))

        for p in possible_paths:
            if os.path.exists(p):
                return p

        return None
