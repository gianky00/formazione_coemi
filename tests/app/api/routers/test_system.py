import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app

@patch("desktop_app.ipc_bridge.IPCBridge")
def test_open_action(mock_bridge_cls, test_client: TestClient):
    mock_instance = MagicMock()
    mock_bridge_cls.instance.return_value = mock_instance

    response = test_client.post(
        "/system/open-action",
        json={"action": "test_action", "payload": {"key": "value"}}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Action test_action dispatched"}

    mock_instance.emit_action.assert_called_once_with("test_action", {"key": "value"})

def test_open_action_invalid_payload(test_client: TestClient):
    response = test_client.post(
        "/system/open-action",
        json={"action": "test"} # Payload optional
    )
    assert response.status_code == 200

    response = test_client.post(
        "/system/open-action",
        json={} # Missing action
    )
    assert response.status_code == 422
