import os
import requests

class APIClient:
    def __init__(self):
        self.base_url = os.environ.get("API_URL", "http://localhost:8000/api/v1")

    def import_dipendenti_csv(self, file_path):
        url = f"{self.base_url}/dipendenti/import-csv"
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/csv')}
            response = requests.post(url, files=files)
        response.raise_for_status()
        return response.json()
