from desktop_app.api.base_client import BaseAPIClient

class SystemAPI:
    def __init__(self, client: BaseAPIClient):
        self.client = client

    def get_audit_logs(self, skip=0, limit=100, **kwargs):
        params = {"skip": skip, "limit": limit}
        params.update(kwargs)
        return self.client.get("/audit/", params=params)

    def trigger_maintenance(self):
        return self.client.post("/system/maintenance/background")

    def get_lock_status(self):
        return self.client.get("/system/lock-status")

    def get_config(self):
        return self.client.get("/app_config/config")

    def update_config(self, data):
        return self.client.put("/app_config/config", json=data)

    def get_users(self):
        return self.client.get("/users/")

    def update_user(self, uid, data):
        return self.client.put(f"/users/{uid}", json=data)

    def delete_user(self, uid):
        return self.client.delete(f"/users/{uid}")

    def create_user(self, data):
        return self.client.post("/users/", json=data)
