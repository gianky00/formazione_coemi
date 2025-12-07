import requests
import logging
from packaging import version
from app import __version__
from PyQt6.QtCore import QThread, pyqtSignal, QObject

# Placeholder for now, can be changed via config later if needed
UPDATE_URL = "https://intelleo-updates.netlify.app/version.json"

class UpdateChecker:
    """
    Checks for updates by fetching a JSON file from a remote server.
    Expected JSON format: {"latest_version": "1.1.0", "installer_url": "..."}
    """

    def __init__(self, check_url=UPDATE_URL):
        self.check_url = check_url
        self.logger = logging.getLogger(__name__)

    def check_for_updates(self):
        """
        Fetches the version.json and compares it with the local version.
        Returns a tuple (has_update, latest_version, installer_url) or (False, None, None).
        This method is blocking and should be run in a separate thread.
        """
        try:
            self.logger.info(f"Checking for updates at {self.check_url}...")
            # Set a short timeout to not hang the thread too long
            response = requests.get(self.check_url, timeout=5)
            response.raise_for_status()

            data = response.json()
            latest_version_str = data.get("latest_version")
            installer_url = data.get("installer_url")

            if not latest_version_str or not installer_url:
                self.logger.warning("Invalid update JSON format.")
                return False, None, None

            current_ver = version.parse(__version__)
            latest_ver = version.parse(latest_version_str)

            if latest_ver > current_ver:
                self.logger.info(f"Update available: {latest_ver} > {current_ver}")
                return True, latest_version_str, installer_url
            else:
                self.logger.info("Application is up to date.")
                return False, None, None

        except Exception as e:
            self.logger.error(f"Update check failed: {e}")
            return False, None, None

class UpdateWorker(QThread):
    """
    Worker thread to perform the update check asynchronously.
    Emits update_available(version, url) if an update is found.
    """
    update_available = pyqtSignal(str, str)
    check_finished = pyqtSignal() # Emitted regardless of outcome

    def __init__(self, parent=None):
        super().__init__(parent)
        self.checker = UpdateChecker()

    def run(self):
        has_update, ver, url = self.checker.check_for_updates()
        if has_update:
            self.update_available.emit(ver, url)
        self.check_finished.emit()
