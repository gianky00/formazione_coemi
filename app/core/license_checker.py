import os
import json
import logging
from cryptography.fernet import Fernet
from app.core.config import get_user_data_dir
from app.core.license_security import get_license_secret_key
from desktop_app.services.hardware_id_service import get_machine_id
from desktop_app.constants import LABEL_HARDWARE_ID

# Configure logging
logger = logging.getLogger(__name__)

class LicenseChecker:
    @staticmethod
    def is_license_valid() -> bool:
        """
        Verifies if the license file exists AND is valid (matches HWID).
        This replaces the old PyArmor check.
        """
        try:
            license_dir = os.path.join(get_user_data_dir(), "Licenza")
            config_path = os.path.join(license_dir, "config.dat")

            if not os.path.exists(config_path):
                # Fallback to install dir (legacy)
                # Note: Backend might not know install dir easily if running as service,
                # but typically get_user_data_dir is the standard now.
                return False

            # Read & Decrypt
            with open(config_path, "rb") as f:
                encrypted_data = f.read()

            cipher = Fernet(get_license_secret_key())
            decrypted_data = cipher.decrypt(encrypted_data)

            data = json.loads(decrypted_data.decode('utf-8'))

            # Verify HWID
            stored_hw_id = data.get(LABEL_HARDWARE_ID)
            current_hw_id = get_machine_id()

            if not stored_hw_id or stored_hw_id != current_hw_id:
                logger.warning(f"License HWID mismatch: {stored_hw_id} vs {current_hw_id}")
                return False

            return True

        except Exception as e:
            logger.error(f"License validation failed: {e}")
            return False
