import os
import sys

from app.core.config import get_user_data_dir


class LicenseChecker:
    @staticmethod
    def is_license_valid() -> bool:
        """
        Verifies if the license files exist.
        Checks multiple locations for robustness.
        """
        # 1. User Data Directory (Preferred)
        license_dir = os.path.join(get_user_data_dir(), "Licenza")
        if os.path.exists(os.path.join(license_dir, "pyarmor.rkey")):
            return True

        # 2. Application Root / Install Directory (Legacy)
        # In frozen apps, this is sys._MEIPASS or executable dir
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.argv[0])))

        # Check root
        if os.path.exists(os.path.join(base_path, "pyarmor.rkey")):
            return True

        # Check /Licenza subfolder in root
        if os.path.exists(os.path.join(base_path, "Licenza", "pyarmor.rkey")):
            return True

        # 3. Check current working directory
        cwd = os.getcwd()
        if os.path.exists(os.path.join(cwd, "pyarmor.rkey")):
            return True
        return bool(os.path.exists(os.path.join(cwd, "Licenza", "pyarmor.rkey")))
