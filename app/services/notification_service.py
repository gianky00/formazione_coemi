import logging
import smtplib
import threading
from datetime import date, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from fpdf import FPDF
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Certificato
from app.db.session import SessionLocal
from app.services import certificate_logic
from app.utils.audit import log_security_action

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

EXCLUDED_CATEGORIES: list[str] = [
    "ATEX",
    "BLSD",
    "DIRETTIVA SEVESO",
    "DIRIGENTI E FORMATORI",
    "H2S",
    "MEDICO COMPETENTE",
    "HLO",
]


def safe_text(text: Any) -> str:
    """
    Sanitizes text for FPDF (Latin-1) to prevent encoding crashes.
    """
    if not text:
        return ""
    return str(text).encode("latin-1", "replace").decode("latin-1")


class PDF(FPDF):
    def header(self) -> None:
        try:
            self.image("desktop_app/assets/logo.png", 10, 8, 45)
        except Exception:
            pass
        self.set_font("Arial", "B", 15)
        self.cell(80)
        self.cell(0, 10, f"Report scadenze al {date.today().strftime('%d/%m/%Y')}", 0, 0, "C")
        self.ln(20)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, "Restricted | Internal Use Only", 0, 0, "L")
        self.cell(0, 10, "Pagina " + str(self.page_no()) + "/{nb}", 0, 0, "R")


def _draw_table_header(
    pdf: PDF, header: list[str], col_widths: list[int], color: tuple[int, int, int]
) -> None:
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(color[0], color[1], color[2])
    for i, header_text in enumerate(header):
        pdf.cell(col_widths[i], 10, safe_text(header_text), 1, 0, "C", 1)
    pdf.ln()


def _draw_table_rows(
    pdf: PDF,
    data: list[Certificato],
    col_widths: list[int],
    header: list[str],
    color: tuple[int, int, int],
) -> None:
    pdf.set_font("Arial", "", 8)
    row_num = 1
    for cert in data:
        if pdf.get_y() > (pdf.page_break_trigger - 20):
            pdf.add_page()
            _draw_table_header(pdf, header, col_widths, color)
            pdf.set_font("Arial", "", 8)

        # Get matricola
        matricola = ""
        if cert.dipendente and cert.dipendente.matricola:
            matricola = str(cert.dipendente.matricola)
        elif hasattr(cert, "matricola_raw") and cert.matricola_raw:
            matricola = str(cert.matricola_raw)
        if not matricola:
            matricola = "-"

        # Get dipendente name
        dipendente_nome = ""
        if cert.dipendente:
            cognome = cert.dipendente.cognome or ""
            nome = cert.dipendente.nome or ""
            dipendente_nome = f"{cognome} {nome}".strip()
        if (
            not dipendente_nome
            and hasattr(cert, "nome_dipendente_raw")
            and cert.nome_dipendente_raw
        ):
            dipendente_nome = str(cert.nome_dipendente_raw)
        if not dipendente_nome:
            dipendente_nome = "-"

        # Get categoria
        categoria = cert.corso.categoria_corso if cert.corso else "-"
        if len(categoria) > 20:
            categoria = categoria[:18] + ".."

        data_scadenza = (
            cert.data_scadenza_calcolata.strftime("%d/%m/%Y")
            if cert.data_scadenza_calcolata
            else "-"
        )

        pdf.cell(col_widths[0], 8, str(row_num), 1, 0, "C")
        pdf.cell(col_widths[1], 8, safe_text(matricola), 1, 0, "C")
        pdf.cell(
            col_widths[2],
            8,
            safe_text(dipendente_nome[:25] if len(dipendente_nome) > 25 else dipendente_nome),
            1,
            0,
            "L",
        )
        pdf.cell(col_widths[3], 8, safe_text(categoria), 1, 0, "L")
        pdf.cell(col_widths[4], 8, safe_text(data_scadenza), 1, 1, "C")
        row_num += 1
    pdf.ln(10)


def generate_pdf_report_in_memory(
    expiring_visite: list[Certificato],
    expiring_corsi: list[Certificato],
    overdue_certificates: list[Certificato],
    visite_threshold: int,
    corsi_threshold: int,
) -> Any:
    """Generates a professional, multi-table PDF report with pagination logic."""
    try:
        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()

        def draw_table(title: str, data: list[Certificato], color: tuple[int, int, int]) -> None:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, safe_text(title), 0, 1, "L")
            pdf.ln(2)

            header = ["Nr.", "Matr.", "Dipendente", "Categoria", "Scadenza"]
            col_widths = [12, 22, 58, 42, 26]

            _draw_table_header(pdf, header, col_widths, color)
            _draw_table_rows(pdf, data, col_widths, header, color)

        if expiring_corsi:
            draw_table(
                f"Certificati in avvicinamento scadenza ({corsi_threshold} giorni)",
                expiring_corsi,
                (240, 248, 255),
            )
        if expiring_visite:
            draw_table(
                f"Visite mediche in avvicinamento scadenza ({visite_threshold} giorni)",
                expiring_visite,
                (240, 248, 255),
            )
        if overdue_certificates:
            draw_table("Certificati scaduti non rinnovati", overdue_certificates, (254, 242, 242))

        return pdf.output(dest="S")
    except Exception as e:
        logging.error(f"Errore imprevisto durante la generazione del PDF: {e}", exc_info=True)
        raise ValueError(
            f"Si è verificato un errore imprevisto durante la creazione del report PDF: {e}"
        )


def send_email_notification(
    pdf_content_bytes: bytes,
    expiring_corsi_count: int,
    expiring_visite_count: int,
    overdue_count: int,
    corsi_threshold: int,
    visite_threshold: int,
) -> None:
    """Sends an email with the PDF report attached."""
    to_emails = [
        email.strip() for email in settings.EMAIL_RECIPIENTS_TO.split(",") if email.strip()
    ]
    cc_emails = [
        email.strip() for email in settings.EMAIL_RECIPIENTS_CC.split(",") if email.strip()
    ]

    if not to_emails:
        logging.warning("Nessun destinatario (To) configurato. Invio email annullato.")
        return

    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_USER
    msg["To"] = ", ".join(to_emails)
    if cc_emails:
        msg["Cc"] = ", ".join(cc_emails)
    msg["Subject"] = (
        f"Intelleo: Avviso documenti in scadenza - Report del {date.today().strftime('%d/%m/%Y')}"
    )

    html_body = f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <p>Questo è un avviso generato automaticamente dal sistema di monitoraggio delle scadenze.</p>
            <ul>
                <li>Certificati in avvicinamento scadenza ({corsi_threshold} giorni): <strong>{expiring_corsi_count}</strong></li>
                <li>Visite mediche in avvicinamento scadenza ({visite_threshold} giorni): <strong>{expiring_visite_count}</strong></li>
                <li>Certificati scaduti non rinnovati: <strong>{overdue_count}</strong></li>
            </ul>
            <p>In allegato il report PDF dettagliato.</p>
        </div>
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, "html"))

    part = MIMEBase("application", "octet-stream")
    part.set_payload(pdf_content_bytes)
    encoders.encode_base64(part)

    filename_date = date.today().strftime("%d_%m_%Y")
    part.add_header(
        "Content-Disposition",
        f"attachment; filename=Report scadenze del {filename_date}.pdf",
    )
    msg.attach(part)

    SMTP_TIMEOUT = 30
    try:
        if settings.SMTP_PORT == 465:
            with smtplib.SMTP_SSL(
                settings.SMTP_HOST, settings.SMTP_PORT, timeout=SMTP_TIMEOUT
            ) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(
                settings.SMTP_HOST, settings.SMTP_PORT, timeout=SMTP_TIMEOUT
            ) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        logging.info("Email notification sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send email notification: {e}")
        raise ConnectionAbortedError(f"SMTP Error: {e}")


def send_security_alert_email(subject: str, body_html: str) -> None:
    """Sends a critical security alert email."""
    to_emails = [
        email.strip() for email in settings.EMAIL_RECIPIENTS_TO.split(",") if email.strip()
    ]
    if not to_emails:
        return

    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_USER
    msg["To"] = ", ".join(to_emails)
    msg["Subject"] = subject
    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        logging.error(f"Failed to send security alert: {e}")


def _process_cert_for_report(
    cert: Certificato,
    db: Session,
    today: date,
    limits: tuple[date, date],
    results: tuple[list[Certificato], list[Certificato], list[Certificato]],
) -> None:
    """Helper to process a single certificate for reporting."""
    if not cert.data_scadenza_calcolata or not cert.corso:
        return

    if cert.corso.categoria_corso in EXCLUDED_CATEGORIES:
        return

    expiring_limit_attestati, expiring_limit_visite = limits
    expiring_visite, expiring_corsi, overdue_certificates = results

    if cert.corso.categoria_corso == "VISITA MEDICA":
        if today < cert.data_scadenza_calcolata <= expiring_limit_visite:
            expiring_visite.append(cert)
    else:
        if today < cert.data_scadenza_calcolata <= expiring_limit_attestati:
            expiring_corsi.append(cert)

    if cert.data_scadenza_calcolata < today:
        status = certificate_logic.get_certificate_status(db, cert)
        if status == "scaduto":
            overdue_certificates.append(cert)


def get_report_data(db: Session) -> tuple[list[Certificato], list[Certificato], list[Certificato]]:
    today = date.today()
    expiring_visite: list[Certificato] = []
    expiring_corsi: list[Certificato] = []
    overdue_certificates: list[Certificato] = []

    expiring_limit_attestati = today + timedelta(days=settings.ALERT_THRESHOLD_DAYS)
    expiring_limit_visite = today + timedelta(days=settings.ALERT_THRESHOLD_DAYS_VISITE)

    limits = (expiring_limit_attestati, expiring_limit_visite)
    results = (expiring_visite, expiring_corsi, overdue_certificates)

    all_certs = db.query(Certificato).all()
    for cert in all_certs:
        _process_cert_for_report(cert, db, today, limits, results)

    return expiring_visite, expiring_corsi, overdue_certificates


_email_lock: threading.Lock = threading.Lock()


def check_and_send_alerts() -> None:
    """
    Checks for expiring or overdue certificates and sends a summary email.
    """
    if not _email_lock.acquire(blocking=False):
        logging.warning("Email alert task already running. Skipping concurrent execution.")
        return

    db = SessionLocal()
    try:
        expiring_visite, expiring_corsi, overdue_certificates = get_report_data(db)
        total_expiring = len(expiring_visite) + len(expiring_corsi)

        if total_expiring > 0 or overdue_certificates:
            pdf_content_bytes = generate_pdf_report_in_memory(
                expiring_visite=expiring_visite,
                expiring_corsi=expiring_corsi,
                overdue_certificates=overdue_certificates,
                visite_threshold=settings.ALERT_THRESHOLD_DAYS_VISITE,
                corsi_threshold=settings.ALERT_THRESHOLD_DAYS,
            )

            if pdf_content_bytes:
                send_email_notification(
                    pdf_content_bytes=bytes(pdf_content_bytes),
                    expiring_corsi_count=len(expiring_corsi),
                    expiring_visite_count=len(expiring_visite),
                    overdue_count=len(overdue_certificates),
                    corsi_threshold=settings.ALERT_THRESHOLD_DAYS,
                    visite_threshold=settings.ALERT_THRESHOLD_DAYS_VISITE,
                )
                log_security_action(
                    db, None, "SYSTEM_ALERT", "Sent expiration report email.", category="SYSTEM"
                )
    except Exception as e:
        logging.error(f"Error in check_and_send_alerts: {e}")
    finally:
        db.close()
        _email_lock.release()
