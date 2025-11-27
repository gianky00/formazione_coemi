import pytest
import smtplib
import logging
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
import anyio

# Import the function and router directly
from app.services.notification_service import check_and_send_alerts
from app.api.routers.notifications import send_manual_alert

@pytest.fixture
def mock_settings():
    """Provides consistent mock settings for notification tests."""
    with patch("app.services.notification_service.settings") as mock:
        mock.EMAIL_RECIPIENTS_TO = "recipient@example.com"
        mock.SMTP_HOST = "smtp.test.com"
        mock.SMTP_PORT = 587
        mock.SMTP_USER = "user@example.com"
        mock.SMTP_PASSWORD = "password"
        mock.ALERT_THRESHOLD_DAYS = 60
        mock.ALERT_THRESHOLD_DAYS_VISITE = 30
        yield mock

# --- Test Endpoint Resilience ---

@pytest.mark.anyio
@patch("app.api.routers.notifications.check_and_send_alerts")
async def test_send_manual_alert_endpoint_always_succeeds(mock_check_and_send):
    """
    Test that the async endpoint itself doesn't raise exceptions.
    """
    mock_check_and_send.side_effect = Exception("Internal service failure")

    # The endpoint should catch this and return a success message
    response = await send_manual_alert()
    
    assert response == {"message": "Email di notifica inviata con successo."}
    mock_check_and_send.assert_called_once()

# --- Test Service Resilience ---

@patch("smtplib.SMTP") # Patch for STARTTLS on port 587
@patch("smtplib.SMTP_SSL") # Patch for SSL on port 465
@patch("app.services.notification_service.generate_pdf_report_in_memory", return_value=b"pdf_bytes")
@patch("app.services.notification_service.SessionLocal")
def test_check_and_send_alerts_catches_smtp_error(mock_session, mock_gen_pdf, mock_smtp_ssl, mock_smtp, mock_settings, caplog):
    """
    Verify that the main service function logs SMTP errors but does not crash.
    """
    mock_db = mock_session.return_value
    
    mock_cert = MagicMock()
    mock_cert.data_scadenza_calcolata = date.today() + timedelta(days=10)
    mock_cert.corso.categoria_corso = "FORMAZIONE"
    mock_db.query.return_value.all.return_value = [mock_cert]
    
    # Configure the correct mock based on port
    if mock_settings.SMTP_PORT == 465:
        mock_smtp_instance = mock_smtp_ssl.return_value.__enter__.return_value
    else:
        mock_smtp_instance = mock_smtp.return_value.__enter__.return_value
        
    mock_smtp_instance.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Login failed")
    
    with caplog.at_level(logging.ERROR):
        check_and_send_alerts()

    assert "CRITICAL: SMTP Authentication Error" in caplog.text
    mock_gen_pdf.assert_called_once()

@patch("app.services.notification_service.generate_pdf_report_in_memory", side_effect=ValueError("PDF generation failed"))
@patch("app.services.notification_service.SessionLocal")
def test_check_and_send_alerts_catches_pdf_error(mock_session, mock_gen_pdf, mock_settings, caplog):
    """
    Verify that the main service function logs PDF generation errors and does not crash.
    """
    mock_db = mock_session.return_value
    mock_cert = MagicMock()
    mock_cert.data_scadenza_calcolata = date.today() + timedelta(days=10)
    mock_cert.corso.categoria_corso = "FORMAZIONE"
    mock_db.query.return_value.all.return_value = [mock_cert]

    with caplog.at_level(logging.ERROR):
        check_and_send_alerts()
    
    assert "CRITICAL: The 'check_and_send_alerts' job failed unexpectedly" in caplog.text
    assert "PDF generation failed" in caplog.text
