import os
import requests

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
