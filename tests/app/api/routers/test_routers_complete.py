from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from app.db.models import AuditLog


# --- AUDIT ---
def test_get_audit_logs_filters(test_client, admin_token_headers, db_session):
    # Seed logs
    l1 = AuditLog(username="u1", action="LOGIN", category="AUTH", timestamp=datetime.now())
    l2 = AuditLog(
        username="u2",
        action="DELETE",
        category="DATA",
        timestamp=datetime.now() - timedelta(days=2),
    )
    db_session.add_all([l1, l2])
    db_session.commit()

    # Filter by category
    res = test_client.get("/audit/?category=AUTH", headers=admin_token_headers)
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["username"] == "u1"

    # Filter by search (username match)
    res = test_client.get("/audit/?search=u2", headers=admin_token_headers)
    assert res.status_code == 200
    assert len(res.json()) == 1

    # Filter by date
    start = (datetime.now() - timedelta(days=1)).isoformat()
    res = test_client.get(f"/audit/?start_date={start}", headers=admin_token_headers)
    assert len(res.json()) == 1  # Only l1


def test_audit_logs_export(test_client, admin_token_headers):
    res = test_client.get("/audit/export", headers=admin_token_headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]


# --- SYSTEM ---
def test_system_maintenance(test_client, user_token_headers):
    # Reset flag
    with patch("app.api.routers.system.MAINTENANCE_RUNNING", False):
        res = test_client.post("/system/maintenance/background", headers=user_token_headers)
        assert res.status_code == 200
        assert res.json()["status"] == "started"


def test_system_lock_status(test_client, user_token_headers):
    with patch("app.core.db_security.db_security.is_read_only", True):
        res = test_client.get("/system/lock-status", headers=user_token_headers)
        assert res.status_code == 200
        assert res.json()["read_only"] is True


def test_system_optimize(test_client, admin_token_headers):
    with patch("app.core.db_security.db_security.optimize_database") as mock_opt:
        res = test_client.post("/system/optimize", headers=admin_token_headers)
        assert res.status_code == 200
        mock_opt.assert_called()


def test_system_open_action(test_client):
    # This endpoint doesn't require auth in code? Let's check. No depends.
    with patch("desktop_app.ipc_bridge.IPCBridge.instance") as mock_inst:
        mock_bridge = MagicMock()
        mock_inst.return_value = mock_bridge

        payload = {"action": "TEST", "payload": {"key": "value"}}
        res = test_client.post("/system/open-action", json=payload)
        assert res.status_code == 200
        mock_bridge.emit_action.assert_called_with("TEST", {"key": "value"})


# --- CONFIG (DB Security Toggle) ---
def test_toggle_security_mode(test_client, admin_token_headers):
    with patch("app.api.routers.config.db_security") as mock_sec:
        # Schema expects 'locked', not 'encrypted'
        res = test_client.post(
            "/config/db-security/toggle", json={"locked": True}, headers=admin_token_headers
        )
        assert res.status_code == 200
        mock_sec.toggle_security_mode.assert_called_with(True)
