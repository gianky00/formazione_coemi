from datetime import date
from unittest.mock import MagicMock, patch

from app.utils import audit, date_parser, file_security, security


class TestUtils:
    def test_parse_date_flexible(self):
        assert date_parser.parse_date_flexible("2024-01-01") == date(2024, 1, 1)
        assert date_parser.parse_date_flexible("01/01/2024") == date(2024, 1, 1)
        assert date_parser.parse_date_flexible("01.01.2024") == date(2024, 1, 1)
        assert date_parser.parse_date_flexible("invalid") is None
        assert date_parser.parse_date_flexible(None) is None

    def test_verify_file_signature(self):
        assert file_security.verify_file_signature(b"%PDF-1.4", "pdf") is True
        assert file_security.verify_file_signature(b"garbage", "pdf") is False
        assert file_security.verify_file_signature(b"col1,col2\nval1,val2", "csv") is True
        # Binary data should fail for CSV
        assert file_security.verify_file_signature(b"\x00\x01\x02", "csv") is False
        # Valid text
        assert file_security.verify_file_signature(b"header\nvalue", "csv") is True

    def test_obfuscation(self):
        secret = "mysecret"
        obf = security.obfuscate_string(secret)
        assert obf.startswith("obf:")
        assert obf != secret
        assert security.reveal_string(obf) == secret
        assert security.reveal_string("plain") == "plain"
        assert security.reveal_string("") == ""
        assert security.obfuscate_string("") == ""

    def test_log_security_action(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        user.username = "test"

        request = MagicMock()
        request.client.host = "127.0.0.1"
        request.headers.get.return_value = "Agent"

        # Patch GeoLocationService and Notification Service import inside the function
        with (
            patch("app.utils.audit.GeoLocationService.get_location", return_value="Localhost"),
            patch("threading.Thread") as MockThread,
            patch("app.services.notification_service.send_security_alert_email"),
        ):
            audit.log_security_action(db, user, "TEST", severity="CRITICAL", request=request)

            db.add.assert_called()
            db.commit.assert_called()

            # Check alert trigger
            MockThread.assert_called()

    def test_log_security_action_system(self):
        db = MagicMock()
        audit.log_security_action(db, None, "SYSTEM_ACTION")
        db.add.assert_called()
