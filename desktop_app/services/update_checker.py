import threading
import requests
import logging

logger = logging.getLogger(__name__)

class UpdateChecker:
    """
    Checks for updates using GitHub API (or custom backend).
    Thread-safe implementation using callbacks.
    """
    def __init__(self, current_version):
        self.current_version = current_version
        # TODO: Configure real repo via config
        self.api_url = "https://api.github.com/repos/gianky00/intelleo-licenses/releases/latest" 

    def check_for_updates(self, callback):
        """
        Checks for updates in a background thread.
        callback(has_update, new_version, download_url)
        """
        threading.Thread(target=self._check_thread, args=(callback,), daemon=True).start()

    def _check_thread(self, callback):
        try:
            # Short timeout to avoid blocking startup UX perception
            response = requests.get(self.api_url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                latest_tag = data.get("tag_name", "").lstrip("v")
                
                # Simple string compare works for semantic versioning usually, but packaging.version is better
                # For now, strict inequality check
                if latest_tag != self.current_version and latest_tag > self.current_version:
                    logger.info(f"Update found: {latest_tag}")
                    callback(True, latest_tag, data.get("html_url"))
                    return
            
            callback(False, None, None)
        except Exception as e:
            logger.warning(f"Update check failed: {e}")
            callback(False, None, None)