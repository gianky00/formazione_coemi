import pytest
from unittest.mock import MagicMock, patch, mock_open
from datetime import date, timedelta
import smtplib
import logging

from app.services import notification_service
from app.db.models import Certificato, Corso, Dipendente

@pytest.fixture
def mock_settings():
    """Fixture to provide consistent mock settings for tests."""
    with patch("app.services.notification_service.settings") as mock:
        mock.EMAIL_RECIPIENTS_TO = "recipient@example.com"
        mock.EMAIL_RECIPIENTS_CC = "cc@example.com"
        mock.SMTP_USER = "user@example.com"
        mock.SMTP_PASSWORD = "password"
        mock.SMTP_HOST = "smtp.example.com"
        mock.SMTP_PORT = 587
        mock.ALERT_THRESHOLD_DAYS = 60
        mock.ALERT_THRESHOLD_DAYS_VISITE = 30
        yield mock

@pytest.fixture
def mock_db_session():
    """Fixture to mock the database session."""
    with patch("app.services.notification_service.SessionLocal") as mock_session_local:
        session = MagicMock()
        mock_session_local.return_value = session
        yield session

@pytest.fixture
def sample_certificates():
    """Provides a list of sample certificates for testing scenarios."""
    dipendente = Dipendente(matricola="M01", nome="Test", cognome="Employee")
    corso_standard = Corso(categoria_corso="FORMAZIONE", nome_corso="Sicurezza Generale")
    corso_medico = Corso(categoria_corso="VISITA MEDICA", nome_corso="Visita Periodica")

    # Certificate expiring soon (standard)
    cert1 = Certificato(dipendente=dipendente, corso=corso_standard, data_scadenza_calcolata=date.today() + timedelta(days=45))
    # Certificate expiring soon (medical)
    cert2 = Certificato(dipendente=dipendente, corso=corso_medico, data_scadenza_calcolata=date.today() + timedelta(days=15))
    # Certificate already expired
    cert3 = Certificato(dipendente=dipendente, corso=corso_standard, data_scadenza_calcolata=date.today() - timedelta(days=30))

    return [cert1, cert2, cert3]

# --- Resilience Tests ---

def test_send_email_does_not_crash_on_smtp_auth_error(mock_settings, caplog):
    """Verify that an SMTPAuthenticationError is caught, logged, and does not crash the function."""
    png_bytes = b'\x89PNG\r\n\x1a\n' # Valid PNG header
    with patch("smtplib.SMTP") as MockSMTP, \
         patch("builtins.open", mock_open(read_data=png_bytes)):

        server = MockSMTP.return_value.__enter__.return_value
        server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Authentication credentials invalid")

        with caplog.at_level(logging.ERROR):
            # This call should NOT raise an exception
            notification_service.send_email_notification(b"pdf_content", 1, 1, 1, 60, 30)

        # Check that a critical error was logged
        assert "CRITICAL: SMTP Authentication Error" in caplog.text
        assert "Authentication credentials invalid" in caplog.text

def test_check_and_send_alerts_does_not_crash_on_pdf_error(mock_db_session, sample_certificates, mock_settings, caplog):
    """Verify that the main scheduler job catches PDF generation errors and logs them without crashing."""
    mock_db_session.query.return_value.all.return_value = sample_certificates

    with patch("app.services.notification_service.certificate_logic.get_certificate_status", return_value="scaduto"), \
         patch("app.services.notification_service.generate_pdf_report_in_memory", side_effect=ValueError("PDF Generation Failed")), \
         patch("app.services.notification_service.send_email_notification") as mock_send_email:

        with caplog.at_level(logging.ERROR):
            # This call should catch the exception internally and log it
            notification_service.check_and_send_alerts()

        # Assert that the error was logged
        assert "CRITICAL: The 'check_and_send_alerts' job failed unexpectedly" in caplog.text
        assert "PDF Generation Failed" in caplog.text
        # Assert that the email sending was NOT attempted
        mock_send_email.assert_not_called()

def test_check_and_send_alerts_full_run_success(mock_db_session, sample_certificates, mock_settings):
    """Test a successful run of the main task to ensure logic is correct."""
    mock_db_session.query.return_value.all.return_value = sample_certificates

    with patch("app.services.notification_service.certificate_logic.get_certificate_status", return_value="scaduto"), \
         patch("app.services.notification_service.generate_pdf_report_in_memory", return_value=b"fake_pdf_bytes") as mock_gen_pdf, \
         patch("app.services.notification_service.send_email_notification") as mock_send_email:

        notification_service.check_and_send_alerts()

        # Verify PDF generation was called with the correct data
        mock_gen_pdf.assert_called_once()
        _, kwargs = mock_gen_pdf.call_args
        assert len(kwargs['expiring_corsi']) == 1
        assert len(kwargs['expiring_visite']) == 1
        assert len(kwargs['overdue_certificates']) == 1

        # Verify email was sent with the correct counts
        mock_send_email.assert_called_once()
        _, email_kwargs = mock_send_email.call_args
        assert email_kwargs['expiring_corsi_count'] == 1
        assert email_kwargs['expiring_visite_count'] == 1
        assert email_kwargs['overdue_count'] == 1

def test_check_and_send_alerts_no_alerts_to_send(mock_db_session, mock_settings):
    """Test that if no certificates are expiring or overdue, no actions are taken."""
    # Return an empty list from the database query
    mock_db_session.query.return_value.all.return_value = []

    with patch("app.services.notification_service.generate_pdf_report_in_memory") as mock_gen_pdf, \
         patch("app.services.notification_service.send_email_notification") as mock_send_email:

        notification_service.check_and_send_alerts()

        mock_gen_pdf.assert_not_called()
        mock_send_email.assert_not_called()
