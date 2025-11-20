import pytest
from unittest.mock import MagicMock, patch, mock_open
from datetime import date, timedelta
from app.services import notification_service
from app.db.models import Certificato, Corso, Dipendente
import smtplib

@pytest.fixture
def mock_settings():
    with patch("app.services.notification_service.settings") as mock:
        mock.EMAIL_RECIPIENTS_TO = "to@example.com"
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
    with patch("app.services.notification_service.SessionLocal") as mock:
        session = MagicMock()
        mock.return_value = session
        yield session

@pytest.fixture
def sample_certificates():
    # Create sample data
    dip = Dipendente(matricola="123", nome="Mario", cognome="Rossi")
    corso_gen = Corso(categoria_corso="ANTINCENDIO", nome_corso="Antincendio")
    corso_med = Corso(categoria_corso="VISITA MEDICA", nome_corso="Visita")

    cert1 = Certificato(dipendente=dip, corso=corso_gen, data_scadenza_calcolata=date.today() + timedelta(days=10))
    cert2 = Certificato(dipendente=dip, corso=corso_med, data_scadenza_calcolata=date.today() + timedelta(days=5))
    cert3 = Certificato(dipendente=dip, corso=corso_gen, data_scadenza_calcolata=date.today() - timedelta(days=5)) # Expired

    return [cert1, cert2, cert3]

# --- generate_pdf_report_in_memory Tests ---

def test_generate_pdf_report_in_memory_success():
    # Mock PDF class to avoid file system access and actual PDF generation logic issues
    with patch("app.services.notification_service.PDF") as MockPDF:
        mock_pdf_instance = MockPDF.return_value
        mock_pdf_instance.output.return_value = b"fake_pdf_bytes"

        # Mock file open for logo check. The code calls self.image(...) in header.
        # We mock the image method to do nothing.
        mock_pdf_instance.image.return_value = None

        # Mock layout methods/properties
        mock_pdf_instance.get_y.return_value = 10
        mock_pdf_instance.page_break_trigger = 280

        data = [MagicMock(spec=Certificato)]

        # We also need to mock Certificato attributes accessed in the loop
        data[0].dipendente.matricola = "123"
        data[0].dipendente.nome = "Mario"
        data[0].dipendente.cognome = "Rossi"
        data[0].corso.categoria_corso = "ANTINCENDIO"
        data[0].data_scadenza_calcolata = date(2025, 1, 1)

        result = notification_service.generate_pdf_report_in_memory(
            expiring_visite=data,
            expiring_corsi=data,
            overdue_certificates=data,
            visite_threshold=30,
            corsi_threshold=60
        )

        assert result == b"fake_pdf_bytes"
        mock_pdf_instance.add_page.assert_called()
        mock_pdf_instance.output.assert_called_with(dest='S')

def test_generate_pdf_report_in_memory_missing_logo():
    # If the logo is missing, PDF() creation or usage might fail if we don't mock it well,
    # but the specific try/except block in the function catches FileNotFoundError.
    # The function catches FileNotFoundError during PDF operations.

    # We need to force PDF.header or PDF.image to raise FileNotFoundError
    # Since PDF is defined in the module, we need to patch the class method in the module's namespace?
    # Actually, PDF is defined *inside* the module.

    with patch("app.services.notification_service.PDF") as MockPDF:
        mock_pdf_instance = MockPDF.return_value
        # Simulate error during processing (e.g. when add_page calls header)
        mock_pdf_instance.add_page.side_effect = FileNotFoundError("Logo missing")

        with pytest.raises(ValueError, match="Impossibile generare il PDF"):
            notification_service.generate_pdf_report_in_memory([], [], [], 30, 60)

def test_generate_pdf_report_in_memory_unexpected_error():
    with patch("app.services.notification_service.PDF") as MockPDF:
        mock_pdf_instance = MockPDF.return_value
        mock_pdf_instance.add_page.side_effect = Exception("Boom")

        with pytest.raises(ValueError, match="Si è verificato un errore imprevisto"):
            notification_service.generate_pdf_report_in_memory([], [], [], 30, 60)

# --- send_email_notification Tests ---

def test_send_email_notification_success_starttls(mock_settings):
    mock_settings.SMTP_PORT = 587
    # Use PNG magic bytes so MIMEImage doesn't fail
    png_bytes = b'\x89PNG\r\n\x1a\n'
    with patch("smtplib.SMTP") as MockSMTP, \
         patch("builtins.open", mock_open(read_data=png_bytes)):

        server = MockSMTP.return_value
        server.__enter__.return_value = server

        notification_service.send_email_notification(b"pdf_bytes", 1, 1, 1, 60, 30)

        server.starttls.assert_called_once()
        server.login.assert_called_with("user@example.com", "password")
        server.send_message.assert_called_once()

def test_send_email_notification_success_ssl(mock_settings):
    mock_settings.SMTP_PORT = 465
    png_bytes = b'\x89PNG\r\n\x1a\n'
    with patch("smtplib.SMTP_SSL") as MockSMTP_SSL, \
         patch("builtins.open", mock_open(read_data=png_bytes)):

        server = MockSMTP_SSL.return_value
        server.__enter__.return_value = server

        notification_service.send_email_notification(b"pdf_bytes", 1, 1, 1, 60, 30)

        # starttls should NOT be called for SSL
        assert not hasattr(server, "starttls") or not server.starttls.called
        server.login.assert_called_with("user@example.com", "password")
        server.send_message.assert_called_once()

def test_send_email_notification_no_recipients(mock_settings):
    mock_settings.EMAIL_RECIPIENTS_TO = ""
    with patch("smtplib.SMTP") as MockSMTP:
        notification_service.send_email_notification(b"pdf", 0, 0, 0, 60, 30)
        MockSMTP.assert_not_called()

def test_send_email_notification_smtp_error(mock_settings):
    mock_settings.SMTP_PORT = 587
    png_bytes = b'\x89PNG\r\n\x1a\n'
    with patch("smtplib.SMTP") as MockSMTP, \
         patch("builtins.open", mock_open(read_data=png_bytes)):

        server = MockSMTP.return_value
        server.__enter__.return_value = server
        server.send_message.side_effect = smtplib.SMTPException("SMTP Error")

        with pytest.raises(ConnectionAbortedError, match="Generic SMTP Error"):
            notification_service.send_email_notification(b"pdf", 0, 0, 0, 60, 30)

# --- check_and_send_alerts Tests ---

def test_check_and_send_alerts_triggers_email(mock_db_session, sample_certificates, mock_settings):
    mock_db_session.query.return_value.all.return_value = sample_certificates

    # Mock certificate_logic.get_certificate_status for the expired one
    with patch("app.services.notification_service.certificate_logic.get_certificate_status", return_value="scaduto"), \
         patch("app.services.notification_service.generate_pdf_report_in_memory", return_value=b"pdf") as mock_gen_pdf, \
         patch("app.services.notification_service.send_email_notification") as mock_send_email:

         notification_service.check_and_send_alerts()

         mock_gen_pdf.assert_called_once()
         mock_send_email.assert_called_once()

         # Check arguments - checking kwargs because generate_pdf_report_in_memory is called with kwargs
         _, kwargs = mock_gen_pdf.call_args
         exp_visite = kwargs['expiring_visite']
         exp_corsi = kwargs['expiring_corsi']
         overdue = kwargs['overdue_certificates']

         assert len(exp_visite) == 1 # cert2
         assert len(exp_corsi) == 1 # cert1
         assert len(overdue) == 1 # cert3

def test_check_and_send_alerts_no_data(mock_db_session, mock_settings):
    mock_db_session.query.return_value.all.return_value = []

    with patch("app.services.notification_service.generate_pdf_report_in_memory") as mock_gen_pdf, \
         patch("app.services.notification_service.send_email_notification") as mock_send_email:

         notification_service.check_and_send_alerts()

         mock_gen_pdf.assert_not_called()
         mock_send_email.assert_not_called()

def test_check_and_send_alerts_pdf_gen_failure(mock_db_session, sample_certificates, mock_settings):
    mock_db_session.query.return_value.all.return_value = sample_certificates

    with patch("app.services.notification_service.certificate_logic.get_certificate_status", return_value="scaduto"), \
         patch("app.services.notification_service.generate_pdf_report_in_memory", return_value=None), \
         pytest.raises(ValueError, match="La generazione del PDF è fallita"):

         notification_service.check_and_send_alerts()
