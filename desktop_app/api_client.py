import os
import requests
from desktop_app.utils import get_device_id

class APIClient:
    def __init__(self):
        self.base_url = os.environ.get("API_URL", "http://localhost:8000/api/v1")
        self.access_token = None
        self.user_info = None

    def set_token(self, token_data):
        """
        Sets the access token and user info.
        token_data should be the dict returned by /auth/login.
        """
        self.access_token = token_data.get("access_token")
        self.user_info = {
            "id": token_data.get("user_id"),
            "username": token_data.get("username"),
            "account_name": token_data.get("account_name"),
            "gender": token_data.get("gender"),
            "is_admin": token_data.get("is_admin"),
            "read_only": token_data.get("read_only", False),
            "lock_owner": token_data.get("lock_owner"),
            "previous_login": token_data.get("previous_login"),
            "require_password_change": token_data.get("require_password_change", False)
        }

    def clear_token(self):
        self.access_token = None
        self.user_info = None

    def logout(self):
        """
        Calls the server-side logout endpoint to blacklist the token.
        """
        if self.access_token:
            try:
                url = f"{self.base_url}/auth/logout"
                requests.post(url, headers=self._get_headers(), timeout=5)
            except requests.exceptions.RequestException as e:
                # Log network errors but don't block logout - user must be able to exit
                import logging
                logging.getLogger(__name__).warning(f"Logout request failed (non-blocking): {e}")
        self.clear_token()

    def _get_headers(self):
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        try:
            headers["X-Device-ID"] = get_device_id()
        except Exception as e:
            # Device ID is optional - log but don't fail
            import logging
            logging.getLogger(__name__).debug(f"Could not get device ID (non-critical): {e}")

        return headers

    def get(self, endpoint, params=None):
        """
        Performs a generic GET request to a given endpoint.
        """
        # Ensure endpoint starts with a slash
        if not endpoint.startswith('/'):
            endpoint = f'/{endpoint}'

        url = f"{self.base_url}{endpoint}"

        try:
            # Note: For public endpoints, _get_headers might be empty, which is fine.
            response = requests.get(url, params=params, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            # S112: Replaced generic Exception/return with specific exception handling
            raise ConnectionError(f"Offline: {e}")

    def login(self, username, password):
        url = f"{self.base_url}/auth/login"
        data = {"username": username, "password": password}
        try:
            # Using data=data sends as application/x-www-form-urlencoded which OAuth2PasswordRequestForm expects
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # S112: Raise more specific ConnectionError instead of generic Exception
            raise ConnectionError("Impossibile connettersi al server (Rete irraggiungibile).")

    def change_password(self, old_password, new_password):
        url = f"{self.base_url}/auth/change-password"
        payload = {"old_password": old_password, "new_password": new_password}
        response = requests.post(url, json=payload, headers=self._get_headers(), timeout=10)
        response.raise_for_status()
        return response.json()

    # --- Chat ---

    def send_chat_message(self, message, history=None):
        """
        Sends a message to the Chatbot.
        """
        url = f"{self.base_url}/chat"
        payload = {
            "message": message,
            "history": history or []
        }
        response = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
        response.raise_for_status()
        return response.json()

    # --- Dipendenti Management ---

    def get_dipendenti_list(self):
        """Fetches the list of all employees."""
        url = f"{self.base_url}/dipendenti"
        response = requests.get(url, headers=self._get_headers(), timeout=10)
        response.raise_for_status()
        return response.json()

    def get_dipendente_detail(self, dipendente_id):
        """Fetches detailed info for a specific employee, including certificates."""
        url = f"{self.base_url}/dipendenti/{dipendente_id}"
        response = requests.get(url, headers=self._get_headers(), timeout=10)
        response.raise_for_status()
        return response.json()

    def create_dipendente(self, data):
        """Creates a new employee manually."""
        url = f"{self.base_url}/dipendenti/"
        response = requests.post(url, json=data, headers=self._get_headers(), timeout=10)
        response.raise_for_status()
        return response.json()

    def update_dipendente(self, dipendente_id, data):
        """Updates an existing employee."""
        url = f"{self.base_url}/dipendenti/{dipendente_id}"
        response = requests.put(url, json=data, headers=self._get_headers(), timeout=10)
        response.raise_for_status()
        return response.json()

    def delete_dipendente(self, dipendente_id):
        """Deletes an employee."""
        url = f"{self.base_url}/dipendenti/{dipendente_id}"
        response = requests.delete(url, headers=self._get_headers(), timeout=10)
        response.raise_for_status()
        return response.json()

    # --- System ---

    def trigger_maintenance(self):
        """Triggers the background file maintenance task."""
        url = f"{self.base_url}/system/maintenance/background"
        response = requests.post(url, headers=self._get_headers(), timeout=10)
        response.raise_for_status()
        return response.json()

    def get_lock_status(self):
        """Checks if the backend is in Read-Only mode."""
        url = f"{self.base_url}/system/lock-status"
        response = requests.get(url, headers=self._get_headers(), timeout=5)
        response.raise_for_status()
        return response.json()

    def import_dipendenti_csv(self, file_path):
        """
        Uploads a CSV file to import employee data.
        Bug 4 Fix: Check size before loading to avoid Memory Bomb.
        """
        MAX_CSV_SIZE = 5 * 1024 * 1024 # 5MB limit matching backend

        if os.path.getsize(file_path) > MAX_CSV_SIZE:
             raise ValueError(f"Il file supera il limite massimo di {MAX_CSV_SIZE // (1024*1024)}MB.")

        url = f"{self.base_url}/dipendenti/import-csv"
        # Streaming upload is automatic with open() file object in requests
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/csv')}
            response = requests.post(url, files=files, headers=self._get_headers(), timeout=60)
        response.raise_for_status()
        return response.json()

    # --- User Management ---

    def get_users(self):
        url = f"{self.base_url}/users/"
        response = requests.get(url, headers=self._get_headers(), timeout=10)
        response.raise_for_status()
        return response.json()

    def create_user(self, username, password, account_name=None, is_admin=False, gender=None):
        url = f"{self.base_url}/users/"
        payload = {
            "username": username,
            "password": password,
            "account_name": account_name,
            "is_admin": is_admin,
            "gender": gender
        }
        response = requests.post(url, json=payload, headers=self._get_headers(), timeout=10)
        response.raise_for_status()
        return response.json()

    # --- App Configuration ---

    def get_paths(self):
        """Retrieves the configured database path."""
        url = f"{self.base_url}/app_config/config/paths"
        response = requests.get(url, headers=self._get_headers(), timeout=5)
        response.raise_for_status()
        return response.json()

    def get_mutable_config(self):
        """Retrieves user-configurable settings from the backend."""
        url = f"{self.base_url}/app_config/config"
        response = requests.get(url, headers=self._get_headers(), timeout=10)
        response.raise_for_status()
        return response.json()

    def update_mutable_config(self, settings_data: dict):
        """Updates user-configurable settings on the backend."""
        url = f"{self.base_url}/app_config/config"
        response = requests.put(url, json=settings_data, headers=self._get_headers(), timeout=10)
        response.raise_for_status()
        # This endpoint returns 204 No Content, so we don't expect a body
        return True

    def move_database(self, new_path: str):
        """Moves the database file via the API."""
        url = f"{self.base_url}/config/move-database"
        payload = {"new_path": new_path}
        response = requests.post(url, json=payload, headers=self._get_headers(), timeout=60)
        response.raise_for_status()
        return response.json()

    def update_user(self, user_id, data):
        url = f"{self.base_url}/users/{user_id}"
        response = requests.put(url, json=data, headers=self._get_headers(), timeout=10)
        response.raise_for_status()
        return response.json()

    def delete_user(self, user_id):
        url = f"{self.base_url}/users/{user_id}"
        response = requests.delete(url, headers=self._get_headers(), timeout=10)
        response.raise_for_status()
        return response.json()

    # --- Audit Logs ---

    def get_audit_categories(self):
        url = f"{self.base_url}/audit/categories"
        response = requests.get(url, headers=self._get_headers(), timeout=10)
        response.raise_for_status()
        return response.json()

    def get_audit_logs(self, skip=0, limit=100, user_id=None, category=None, search=None, start_date=None, end_date=None):
        url = f"{self.base_url}/audit/"
        params = {"skip": skip, "limit": limit}
        if user_id:
            params["user_id"] = user_id
        if category:
            params["category"] = category
        if search:
            params["search"] = search
        if start_date:
            # Assuming start_date is a datetime or date object, or ISO string
            params["start_date"] = start_date.isoformat() if hasattr(start_date, 'isoformat') else start_date
        if end_date:
            params["end_date"] = end_date.isoformat() if hasattr(end_date, 'isoformat') else end_date

        response = requests.get(url, params=params, headers=self._get_headers(), timeout=10)
        response.raise_for_status()
        return response.json()

    def create_audit_log(self, action, details=None, category=None, changes=None, severity="LOW"):
        url = f"{self.base_url}/audit/"
        payload = {
            "action": action,
            "details": details,
            "category": category,
            "changes": changes,
            "severity": severity
        }
        # Short timeout for audit logs as they are fire-and-forget-ish from UI perspective
        response = requests.post(url, json=payload, headers=self._get_headers(), timeout=5)
        # We don't necessarily crash if audit fails, but logging it is good
        # response.raise_for_status()
        # Allow caller to handle or ignore
        return response.json() if response.ok else None

    # --- DB Security ---

    def get_db_security_status(self):
        url = f"{self.base_url}/config/db-security/status"
        response = requests.get(url, headers=self._get_headers(), timeout=5)
        response.raise_for_status()
        return response.json()

    def toggle_db_security(self, locked: bool):
        url = f"{self.base_url}/config/db-security/toggle"
        payload = {"locked": locked}
        response = requests.post(url, json=payload, headers=self._get_headers(), timeout=60) # Encryption might take time
        response.raise_for_status()
        return response.json()
