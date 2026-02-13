from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

from app.db.models import Certificato, Corso, Dipendente
from app.services import notification_service

# --- Mocks ---


@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture
def sample_certificates():
    today = date.today()

    # 1. Expiring Course
    cert1 = MagicMock(spec=Certificato)
    cert1.id = 1
    cert1.data_scadenza_calcolata = today + timedelta(days=30)
    cert1.corso = MagicMock(spec=Corso)
    cert1.corso.categoria_corso = "SICUREZZA"
    cert1.corso.nome_corso = "Corso Base"
    cert1.dipendente = MagicMock(spec=Dipendente)
    cert1.dipendente.matricola = "001"
    cert1.dipendente.nome = "Mario"
    cert1.dipendente.cognome = "Rossi"

    # 2. Expiring Medical Visit
    cert2 = MagicMock(spec=Certificato)
    cert2.id = 2
    cert2.data_scadenza_calcolata = today + timedelta(days=15)
    cert2.corso = MagicMock(spec=Corso)
    cert2.corso.categoria_corso = "VISITA MEDICA"
    cert2.corso.nome_corso = "Visita Annuale"
    cert2.dipendente = MagicMock(spec=Dipendente)
    cert2.dipendente.matricola = "002"
    cert2.dipendente.nome = "Luigi"
    cert2.dipendente.cognome = "Bianchi"

    # 3. Overdue Certificate
    cert3 = MagicMock(spec=Certificato)
    cert3.id = 3
    cert3.data_scadenza_calcolata = today - timedelta(days=10)
    cert3.corso = MagicMock(spec=Corso)
    cert3.corso.categoria_corso = "PRIMO SOCCORSO"
    cert3.corso.nome_corso = "Primo Soccorso"
    cert3.dipendente = MagicMock(spec=Dipendente)
    cert3.dipendente.matricola = "003"
    cert3.dipendente.nome = "Anna"
    cert3.dipendente.cognome = "Verdi"

    return [cert1, cert2, cert3]


@pytest.fixture
def mock_settings():
    with patch("app.services.notification_service.settings") as mock_settings:
        mock_settings.EMAIL_RECIPIENTS_TO = "to@example.com"
        mock_settings.EMAIL_RECIPIENTS_CC = "cc@example.com"
        mock_settings.SMTP_USER = "user@example.com"
        mock_settings.SMTP_PASSWORD = "password"
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.ALERT_THRESHOLD_DAYS = 60
        mock_settings.ALERT_THRESHOLD_DAYS_VISITE = 30
        yield mock_settings


# --- Tests ---


def test_generate_pdf_report_in_memory_success(sample_certificates):
    expiring_visite = [sample_certificates[1]]
    expiring_corsi = [sample_certificates[0]]
    overdue_certificates = [sample_certificates[2]]

    # Mock FPDF and image to avoid file system dependency
    with patch("app.services.notification_service.PDF") as MockPDF:
        mock_pdf_instance = MockPDF.return_value
        mock_pdf_instance.output.return_value = b"%PDF-1.4..."  # Mock output bytes

        # Mock image to avoid FileNotFoundError
        mock_pdf_instance.image = MagicMock()
        mock_pdf_instance.get_y.return_value = 100
        mock_pdf_instance.page_break_trigger = 250

        pdf_bytes = notification_service.generate_pdf_report_in_memory(
            expiring_visite, expiring_corsi, overdue_certificates, 30, 60
        )

        assert pdf_bytes == b"%PDF-1.4..."
        assert mock_pdf_instance.add_page.called
        # Verify headers were drawn (indirectly via cell calls)
        assert mock_pdf_instance.cell.call_count > 0


def test_generate_pdf_report_in_memory_missing_logo():
    with patch("app.services.notification_service.PDF") as MockPDF:
        mock_pdf_instance = MockPDF.return_value
        mock_pdf_instance.output.return_value = b"%PDF-1.4..."

        # Test generic failure behavior
        mock_pdf_instance.add_page.side_effect = Exception("Generic PDF Error")

        with pytest.raises(ValueError, match="Si è verificato un errore imprevisto"):
            notification_service.generate_pdf_report_in_memory([], [], [], 30, 60)


def test_send_email_notification_ssl(mock_settings):
    mock_settings.SMTP_PORT = 465
    pdf_content = b"PDF_CONTENT"

    with patch("smtplib.SMTP_SSL") as mock_smtp_ssl:
        # SMTP_SSL works as a context manager: with smtplib.SMTP_SSL() as server
        mock_server = mock_smtp_ssl.return_value.__enter__.return_value

        with patch("builtins.open", create=True) as mock_open:
            mock_open.side_effect = FileNotFoundError
            notification_service.send_email_notification(pdf_content, 1, 1, 1, 60, 30)

        mock_smtp_ssl.assert_called_with("smtp.example.com", 465, timeout=30)
        mock_server.login.assert_called_with("user@example.com", "password")
        mock_server.send_message.assert_called()


def test_send_email_notification_starttls(mock_settings):
    mock_settings.SMTP_PORT = 587
    pdf_content = b"PDF_CONTENT"

    with patch("smtplib.SMTP") as mock_smtp:
        mock_server = mock_smtp.return_value.__enter__.return_value

        with patch("builtins.open", create=True) as mock_open:
            mock_open.side_effect = FileNotFoundError
            notification_service.send_email_notification(pdf_content, 1, 1, 1, 60, 30)

        mock_smtp.assert_called_with("smtp.example.com", 587, timeout=30)
        mock_server.starttls.assert_called()
        mock_server.login.assert_called_with("user@example.com", "password")
        mock_server.send_message.assert_called()


def test_check_and_send_alerts_success(mock_db_session, sample_certificates, mock_settings):
    # Setup
    mock_db_session.query.return_value.all.return_value = sample_certificates

    with (
        patch("app.services.notification_service.SessionLocal", return_value=mock_db_session),
        patch(
            "app.services.notification_service.certificate_logic.get_certificate_status",
            return_value="scaduto",
        ),
        patch(
            "app.services.notification_service.generate_pdf_report_in_memory", return_value=b"PDF"
        ),
        patch("app.services.notification_service.send_email_notification") as mock_send,
    ):
        notification_service.check_and_send_alerts()

        mock_send.assert_called_once()
        # Verify kwargs mainly
        _, kwargs = mock_send.call_args
        assert kwargs["pdf_content_bytes"] == b"PDF"


def test_check_and_send_alerts_pdf_gen_failure(mock_db_session, sample_certificates, mock_settings):
    mock_db_session.query.return_value.all.return_value = sample_certificates

    with (
        patch("app.services.notification_service.SessionLocal", return_value=mock_db_session),
        patch(
            "app.services.notification_service.certificate_logic.get_certificate_status",
            return_value="scaduto",
        ),
        patch("app.services.notification_service.generate_pdf_report_in_memory", return_value=None),
        patch("app.services.notification_service.logging.error") as mock_log,
    ):
        notification_service.check_and_send_alerts()

        assert mock_log.call_count >= 1
        found = False
        for call in mock_log.call_args_list:
            if "La generazione del PDF è fallita" in str(call):
                found = True
                break
        assert found


def test_check_and_send_alerts_locking(mock_db_session):
    # Cannot patch acquire on the lock object directly as it is read-only in CPython
    # We patch the lock object itself in the module

    mock_lock = MagicMock()
    mock_lock.acquire.return_value = False

    with (
        patch("app.services.notification_service.SessionLocal", return_value=mock_db_session),
        patch("app.services.notification_service._email_lock", mock_lock),
    ):
        notification_service.check_and_send_alerts()

        mock_db_session.query.assert_not_called()
