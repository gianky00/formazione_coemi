import os

from desktop_app.api.base_client import BaseAPIClient


class DipendentiAPI:
    def __init__(self, client: BaseAPIClient):
        self.client = client

    def list(self):
        return self.client.get("/dipendenti")

    def get(self, dipendente_id):
        return self.client.get(f"/dipendenti/{dipendente_id}")

    def create(self, data):
        return self.client.post("/dipendenti/", json=data)

    def update(self, dipendente_id, data):
        return self.client.put(f"/dipendenti/{dipendente_id}", json=data)

    def delete(self, dipendente_id):
        return self.client.delete(f"/dipendenti/{dipendente_id}")

    def import_csv(self, file_path):
        MAX_CSV_SIZE = 5 * 1024 * 1024
        if os.path.getsize(file_path) > MAX_CSV_SIZE:
            raise ValueError("File troppo grande (>5MB)")

        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "text/csv")}
            return self.client.post("/dipendenti/import-csv", files=files, timeout=300)
