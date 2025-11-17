
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from fpdf import FPDF
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Certificato, Corso
from app.core.config import settings
from app.services import certificate_logic
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_pdf_report(expiring_certificates, overdue_certificates):
    """Generates a PDF report of expiring and overdue certificates."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="Report Scadenze Certificati", ln=True, align='C')
    pdf.set_font("Arial", size=12)

    if expiring_certificates:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', size=14)
        pdf.cell(200, 10, txt="Certificati in Scadenza", ln=True, align='L')
        pdf.set_font("Arial", size=10)
        for cert in expiring_certificates:
            pdf.ln(5)
            pdf.multi_cell(0, 10, f"Dipendente: {cert.dipendente.nome} {cert.dipendente.cognome}\n"
                                f"Corso: {cert.corso.nome_corso}\n"
                                f"Scadenza: {cert.data_scadenza_calcolata.strftime('%d/%m/%Y')}\n")

    if overdue_certificates:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', size=14)
        pdf.cell(200, 10, txt="Certificati Scaduti e non Rinnovati", ln=True, align='L')
        pdf.set_font("Arial", size=10)
        for cert in overdue_certificates:
            pdf.ln(5)
            pdf.multi_cell(0, 10, f"Dipendente: {cert.dipendente.nome} {cert.dipendente.cognome}\n"
                                f"Corso: {cert.corso.nome_corso}\n"
                                f"Scaduto il: {cert.data_scadenza_calcolata.strftime('%d/%m/%Y')}\n")

    pdf_path = "/tmp/report_scadenze.pdf"
    pdf.output(pdf_path)
    return pdf_path

def send_email_notification(pdf_path, expiring_count, overdue_count):
    """Sends an email with the PDF report attached."""
    msg = MIMEMultipart()
    msg['From'] = settings.SMTP_USER
    msg['To'] = settings.EMAIL_RECIPIENT
    msg['Subject'] = f"Report Scadenze Certificati - {date.today().strftime('%d/%m/%Y')}"

    body = (
        f"Buongiorno,\n\n"
        f"In allegato il report riepilogativo dei certificati.\n\n"
        f"Riepilogo:\n"
        f"- Certificati in scadenza: {expiring_count}\n"
        f"- Certificati scaduti da oltre un mese e non rinnovati: {overdue_count}\n\n"
        f"Cordiali saluti,\n"
        f"Intelleo Automated System"
    )
    msg.attach(MIMEText(body, 'plain'))

    with open(pdf_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename=Report_Scadenze_{date.today().strftime('%Y-%m-%d')}.pdf",
    )
    msg.attach(part)

    try:
        # Note: For production, use a more secure way to handle credentials
        # and consider using SSL/TLS appropriately.
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            logging.info(f"Email di notifica inviata con successo a {settings.EMAIL_RECIPIENT}")
    except Exception as e:
        logging.error(f"Errore nell'invio dell'email di notifica: {e}")

def check_and_send_alerts():
    """
    Checks for certificates that are expiring soon or are overdue and sends
    a single summary email with a PDF report if any are found.
    """
    db = SessionLocal()
    try:
        today = date.today()
        expiring_certificates = []
        overdue_certificates = []

        # 1. Check for certificates expiring soon
        expiring_limit_attestati = today + timedelta(days=60)  # 2 months
        expiring_limit_visite = today + timedelta(days=30)     # 1 month

        all_certs = db.query(Certificato).all()

        for cert in all_certs:
            if not cert.data_scadenza_calcolata:
                continue

            # Check for expiring certificates
            if cert.corso.categoria_corso == "VISITA MEDICA":
                if today < cert.data_scadenza_calcolata <= expiring_limit_visite:
                    expiring_certificates.append(cert)
            else:
                if today < cert.data_scadenza_calcolata <= expiring_limit_attestati:
                    expiring_certificates.append(cert)

            # 2. Check for overdue and un-renewed certificates
            overdue_date = today - timedelta(days=30)
            if cert.data_scadenza_calcolata < overdue_date:
                status = certificate_logic.get_certificate_status(db, cert)
                if status != "rinnovato":
                    overdue_certificates.append(cert)

        # 3. Generate report and send email if there's anything to report
        if expiring_certificates or overdue_certificates:
            logging.info(f"Trovati {len(expiring_certificates)} certificati in scadenza e {len(overdue_certificates)} scaduti.")
            pdf_path = generate_pdf_report(expiring_certificates, overdue_certificates)
            send_email_notification(pdf_path, len(expiring_certificates), len(overdue_certificates))
        else:
            logging.info("Nessuna notifica di scadenza da inviare oggi.")

    finally:
        db.close()
