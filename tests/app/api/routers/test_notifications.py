from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

def test_send_manual_alert_success(test_client: TestClient):
    with patch("app.api.routers.notifications.check_and_send_alerts") as mock_check:
        response = test_client.post("/notifications/send-manual-alert")
        assert response.status_code == 200
        assert response.json() == {"message": "Email di notifica inviata con successo."}
        mock_check.assert_called_once()

def test_send_manual_alert_connection_error(test_client: TestClient):
    with patch("app.api.routers.notifications.check_and_send_alerts", side_effect=ConnectionAbortedError("SMTP failure")):
        response = test_client.post("/notifications/send-manual-alert")
        assert response.status_code == 500
        assert "Errore durante l'invio della notifica" in response.json()["detail"]

def test_send_manual_alert_generic_error(test_client: TestClient):
    with patch("app.api.routers.notifications.check_and_send_alerts", side_effect=Exception("Unexpected")):
        response = test_client.post("/notifications/send-manual-alert")
        assert response.status_code == 500
        assert "Si è verificato un errore imprevisto" in response.json()["detail"]
