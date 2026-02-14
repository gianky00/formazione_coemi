from unittest.mock import MagicMock, patch

import pytest

from app.services import notification_service


@pytest.fixture
def mock_settings_global():
    # Patch the global settings instance in app.core.config
    with patch("app.core.config.settings") as m:
        m.SMTP_HOST = "smtp.example.com"
        m.SMTP_PORT = 587
        m.SMTP_USER = "user@example.com"
        m.SMTP_PASSWORD = "obf:password"
        m.EMAIL_RECIPIENTS_TO = "to@example.com"
        m.EMAIL_RECIPIENTS_CC = ""
        m.ALERT_THRESHOLD_DAYS = 30
        m.ALERT_THRESHOLD_DAYS_VISITE = 60
        yield m


def test_generate_pdf_report_in_memory_success():
    # Basic success test
    res = notification_service.generate_pdf_report_in_memory([], [], [], 30, 60)
    assert isinstance(res, bytes)
    assert res.startswith(b"%PDF")


def test_generate_pdf_report_in_memory_error():
    with patch("app.services.notification_service.PDF") as MockPDF:
        mock_pdf = MockPDF.return_value
        mock_pdf.add_page.side_effect = Exception("PDF Fail")
        with pytest.raises(ValueError, match="generazione del PDF"):
            notification_service.generate_pdf_report_in_memory([], [], [], 30, 60)


def test_send_email_notification_ssl(mock_settings_global):
    mock_settings_global.SMTP_PORT = 465
    with patch("smtplib.SMTP_SSL") as mock_smtp:
        mock_smtp.return_value.__enter__.return_value = MagicMock()
        success = notification_service.send_email_notification(b"pdf", 1, 1, 1, 60, 30)
        assert success is True
        mock_smtp.assert_called()


def test_send_email_notification_starttls(mock_settings_global):
    mock_settings_global.SMTP_PORT = 587
    with patch("smtplib.SMTP") as mock_smtp:
        mock_smtp.return_value.__enter__.return_value = MagicMock()
        success = notification_service.send_email_notification(b"pdf", 1, 1, 1, 60, 30)
        assert success is True
        mock_smtp.assert_called()


def test_check_and_send_alerts_no_data(mock_settings_global):
    with (
        patch("app.services.notification_service.SessionLocal"),
        patch("app.services.notification_service.get_report_data", return_value=([], [], [])),
    ):
        notification_service.check_and_send_alerts()
        # No error means success


def test_check_and_send_alerts_success(mock_settings_global):
    mock_db = MagicMock()
    with (
        patch("app.services.notification_service.SessionLocal", return_value=mock_db),
        patch(
            "app.services.notification_service.get_report_data",
            return_value=([MagicMock()], [], []),
        ),
        patch(
            "app.services.notification_service.generate_pdf_report_in_memory", return_value=b"PDF"
        ),
        patch(
            "app.services.notification_service.send_email_notification", return_value=True
        ) as mock_send,
    ):
        notification_service.check_and_send_alerts()
        mock_send.assert_called_once()
