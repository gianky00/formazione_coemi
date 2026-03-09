import logging
import os

import requests

from desktop_app.utils import get_device_id

logger = logging.getLogger(__name__)


class BaseAPIClient:
    """
    Classe base per gestire sessione, token e richieste HTTP comuni.
    """

    def __init__(self):
        self.base_url = os.environ.get("API_URL", "http://localhost:8000/api/v1")
        self.access_token = None
        self.user_info = None

    def _get_headers(self):
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        try:
            headers["X-Device-ID"] = get_device_id()
        except Exception as e:
            logger.debug(f"Could not get device ID: {e}")
        return headers

    def request(self, method, endpoint, **kwargs):
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
        url = f"{self.base_url}{endpoint}"

        # Merge headers
        headers = kwargs.pop("headers", {})
        headers.update(self._get_headers())

        # Set default timeout
        kwargs.setdefault("timeout", 30)

        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            if response.status_code == 204:
                return True
            return response.json()
        except requests.exceptions.HTTPError:
            logger.error(f"HTTP Error {response.status_code} on {endpoint}: {response.text}")
            raise
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.error(f"Network error on {endpoint}: {e}")
            raise ConnectionError(f"Server non raggiungibile: {e}") from e

    def get(self, endpoint, params=None, **kwargs):
        return self.request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint, json=None, data=None, **kwargs):
        return self.request("POST", endpoint, json=json, data=data, **kwargs)

    def put(self, endpoint, json=None, **kwargs):
        return self.request("PUT", endpoint, json=json, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.request("DELETE", endpoint, **kwargs)
