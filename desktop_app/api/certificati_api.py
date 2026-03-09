from desktop_app.api.base_client import BaseAPIClient

class CertificatiAPI:
    def __init__(self, client: BaseAPIClient):
        self.client = client

    def list(self, validated=None):
        params = {}
        if validated is not None:
            params["validated"] = "true" if validated else "false"
        return self.client.get("/certificati", params=params)

    def update(self, cert_id, data):
        return self.client.put(f"/certificati/{cert_id}", json=data)

    def delete(self, cert_id):
        return self.client.delete(f"/certificati/{cert_id}")

    def validate(self, cert_id):
        return self.client.put(f"/certificati/{cert_id}/valida")
