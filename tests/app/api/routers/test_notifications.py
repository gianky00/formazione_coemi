from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

def test_send_manual_alert_success(test_client: TestClient):
    with patch("app.api.routers.notifications.check_and_send_alerts") as mock_check:
        response = test_client.post("/notifications/send-manual-alert")
        assert response.status_code == 200
        assert "Invio email avviato in background" in response.json()["message"]
        # Background tasks are executed by TestClient, so mock should be called
        mock_check.assert_called_once()
