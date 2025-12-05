import os
from app.core.config import get_user_data_dir

class LicenseChecker:
    @staticmethod
    def is_license_valid() -> bool:
        """
        Verifies if the license files exist.
        """
        license_dir = os.path.join(get_user_data_dir(), "Licenza")
        rkey_path = os.path.join(license_dir, "pyarmor.rkey")

        # Basic existence check for the backend
        if not os.path.exists(rkey_path):
            return False

        return True
