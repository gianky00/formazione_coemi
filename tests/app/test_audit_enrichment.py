import json
from unittest.mock import patch

from app.db.models import AuditLog


def test_audit_log_enrichment(test_client, db_session):
    changes = {"key": {"old": "val1", "new": "val2"}}
    payload = {
        "action": "TEST_ENRICHMENT",
        "category": "TEST",
        "details": "Testing device ID and changes",
        "changes": json.dumps(changes),
        "severity": "LOW",
    }
    headers = {"X-Device-ID": "device-xyz-789", "User-Agent": "TestAgent/1.0"}

    response = test_client.post("/audit/", json=payload, headers=headers)
    assert response.status_code == 200

    # Verify DB
    log = db_session.query(AuditLog).filter(AuditLog.action == "TEST_ENRICHMENT").first()
    assert log is not None
    assert log.device_id == "device-xyz-789"
    assert log.user_agent == "TestAgent/1.0"
    assert log.changes == json.dumps(changes)


def test_critical_alert_trigger(test_client, db_session):
    # Mock threading.Thread to verify it is instantiated for CRITICAL events
    with patch("threading.Thread") as mock_thread:
        payload = {"action": "CRITICAL_TEST", "severity": "CRITICAL"}
        response = test_client.post("/audit/", json=payload)
        assert response.status_code == 200

        # Verify thread start
        mock_thread.assert_called_once()
        call_args = mock_thread.call_args[1]  # kwargs
        assert "target" in call_args
        # We assume target is the email sender.

        # Also verify DB
        log = db_session.query(AuditLog).filter(AuditLog.action == "CRITICAL_TEST").first()
        assert log.severity == "CRITICAL"


def test_medium_alert_no_trigger(test_client, db_session):
    with patch("threading.Thread") as mock_thread:
        payload = {"action": "MEDIUM_TEST", "severity": "MEDIUM"}
        response = test_client.post("/audit/", json=payload)
        assert response.status_code == 200

        mock_thread.assert_not_called()
