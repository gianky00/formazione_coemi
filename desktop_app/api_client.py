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
            "is_admin": token_data.get("is_admin")
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
            except Exception:
                # Ignore network errors during logout, just clear local state
                pass
        self.clear_token()

    def _get_headers(self):
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        try:
            headers["X-Device-ID"] = get_device_id()
        except Exception:
            pass

        return headers

    def login(self, username, password):
        url = f"{self.base_url}/auth/login"
        data = {"username": username, "password": password}
        # Using data=data sends as application/x-www-form-urlencoded which OAuth2PasswordRequestForm expects
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()

    def import_dipendenti_csv(self, file_path):
        url = f"{self.base_url}/dipendenti/import-csv"
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/csv')}
            response = requests.post(url, files=files, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    # --- User Management ---

    def get_users(self):
        url = f"{self.base_url}/users/"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def create_user(self, username, password, account_name=None, is_admin=False):
        url = f"{self.base_url}/users/"
        payload = {
            "username": username,
            "password": password,
            "account_name": account_name,
            "is_admin": is_admin
        }
        response = requests.post(url, json=payload, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def update_user(self, user_id, data):
        url = f"{self.base_url}/users/{user_id}"
        response = requests.put(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def delete_user(self, user_id):
        url = f"{self.base_url}/users/{user_id}"
        response = requests.delete(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    # --- Audit Logs ---

    def get_audit_logs(self, skip=0, limit=100, user_id=None, category=None, start_date=None, end_date=None):
        url = f"{self.base_url}/audit/"
        params = {"skip": skip, "limit": limit}
        if user_id:
            params["user_id"] = user_id
        if category:
            params["category"] = category
        if start_date:
            # Assuming start_date is a datetime or date object, or ISO string
            params["start_date"] = start_date.isoformat() if hasattr(start_date, 'isoformat') else start_date
        if end_date:
            params["end_date"] = end_date.isoformat() if hasattr(end_date, 'isoformat') else end_date

        response = requests.get(url, params=params, headers=self._get_headers())
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
        response = requests.post(url, json=payload, headers=self._get_headers())
        # We don't necessarily crash if audit fails, but logging it is good
        # response.raise_for_status()
        # Allow caller to handle or ignore
        return response.json() if response.ok else None

    # --- DB Security ---

    def get_db_security_status(self):
        url = f"{self.base_url}/config/db-security/status"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def toggle_db_security(self, locked: bool):
        url = f"{self.base_url}/config/db-security/toggle"
        payload = {"locked": locked}
        response = requests.post(url, json=payload, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
