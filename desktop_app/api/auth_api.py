import builtins
import contextlib

from desktop_app.api.base_client import BaseAPIClient


class AuthAPI:
    def __init__(self, client: BaseAPIClient):
        self.client = client

    def login(self, username, password):
        data = {"username": username, "password": password}
        res = self.client.post("/auth/login", data=data)
        return res

    def logout(self):
        if self.client.access_token:
            with contextlib.suppress(builtins.BaseException):
                self.client.post("/auth/logout", timeout=5)
        self.client.access_token = None
        self.client.user_info = None

    def change_password(self, old_password, new_password):
        payload = {"old_password": old_password, "new_password": new_password}
        return self.client.post("/auth/change-password", json=payload)
