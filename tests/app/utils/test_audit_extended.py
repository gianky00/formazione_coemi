from datetime import datetime
from unittest.mock import MagicMock, patch

from app.utils.audit import _extract_request_info, _send_alert, log_security_action


def test_extract_request_info_exception_handling():
    # Simulate a request object that raises exception on property access
    mock_request = MagicMock()
    type(mock_request.client).host = PropertyMock(side_effect=Exception("Request error"))

    with patch("app.utils.audit.logger") as mock_logger:
        ip, ua, _geo, _dev = _extract_request_info(mock_request)

        assert ip is None
        assert ua is None
        mock_logger.warning.assert_called()


from unittest.mock import PropertyMock


def test_log_security_action_device_id_priority(db_session):
    mock_request = MagicMock()
    mock_request.client.host = "1.2.3.4"
    mock_request.headers.get.side_effect = lambda k: "HeaderID" if k == "X-Device-ID" else "UA"

    # Patch GeoLocation to avoid real calls
    with patch("app.utils.audit.GeoLocationService.get_location", return_value="TestLoc"):
        # Explicit device_id should win over header device_id
        log_security_action(
            db_session, None, "ACTION", device_id="ExplicitID", request=mock_request
        )

        # Verify the last audit log
        from app.db.models import AuditLog

        log = db_session.query(AuditLog).order_by(AuditLog.id.desc()).first()
        assert log.device_id == "ExplicitID"
        assert log.user_agent == "UA"


def test_send_alert_failure_logging():
    # Test that if notification service fails, we log an error instead of crashing
    user = MagicMock()
    user.username = "admin"

    with (
        patch(
            "app.services.notification_service.send_security_alert_email",
            side_effect=Exception("SMTP Fail"),
        ),
        patch("app.utils.audit.logger") as mock_logger,
    ):
        _send_alert(user, "BREACH", "Details", "1.1.1.1", "Italy", datetime.now())
        mock_logger.error.assert_called_with("Failed to trigger alert email: SMTP Fail")


def test_extract_request_info_no_client():
    mock_request = MagicMock()
    mock_request.client = None
    ip, _ua, _geo, _dev = _extract_request_info(mock_request)
    assert ip == "Unknown"
