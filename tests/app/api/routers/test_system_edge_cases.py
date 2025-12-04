import pytest
from unittest.mock import patch, MagicMock
import sys

def test_open_action_ipc_import_error(test_client):
    # Simulate ImportError when importing IPCBridge from desktop_app.ipc_bridge
    # We mock the module so that accessing 'IPCBridge' raises ImportError

    mock_module = MagicMock()
    # When 'from desktop_app.ipc_bridge import IPCBridge' runs, it does getattr(module, 'IPCBridge')
    # We make that raise ImportError
    type(mock_module).IPCBridge = property(lambda self: (_ for _ in ()).throw(ImportError("No IPC")))

    with patch.dict(sys.modules, {"desktop_app.ipc_bridge": mock_module}):
        payload = {"action": "TEST", "payload": {}}
        res = test_client.post("/system/open-action", json=payload)

        assert res.status_code == 500
        assert "IPC Bridge unavailable" in res.json()["detail"]

def test_open_action_generic_exception(test_client):
    # We need to allow import, but make instance() raise
    with patch("desktop_app.ipc_bridge.IPCBridge.instance", side_effect=Exception("Bridge Broken")):
        payload = {"action": "TEST", "payload": {}}
        res = test_client.post("/system/open-action", json=payload)

        assert res.status_code == 500
        assert "Bridge Broken" in res.json()["detail"]
