
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import tempfile
from fpdf import FPDF
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Certificato, Corso
from app.core.config import settings
from app.services import certificate_logic
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PDF(FPDF):
    def header(self):
        # Logo
        self.image('desktop_app/assets/logo.png', 10, 8, 33)
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, 'Report Scadenze', 0, 0, 'C')
        # Line break
        self.ln(20)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Pagina ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def generate_pdf_report(expiring_certificates, overdue_certificates):
    """Generates a professional PDF report of expiring and overdue certificates."""
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    # Table for expiring certificates
    if expiring_certificates:
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Certificati in Scadenza', 0, 1, 'L')
        pdf.ln(5)

        # Table Header
        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(240, 248, 255) # Light Alice Blue
        pdf.cell(60, 10, 'Dipendente', 1, 0, 'C', 1)
        pdf.cell(80, 10, 'Corso', 1, 0, 'C', 1)
        pdf.cell(40, 10, 'Data Scadenza', 1, 1, 'C', 1)

        # Table Rows
        pdf.set_font('Arial', '', 9)
        fill = False
        for cert in expiring_certificates:
            pdf.set_fill_color(255, 255, 255) if not fill else pdf.set_fill_color(245, 245, 245)
            pdf.cell(60, 10, f"{cert.dipendente.nome} {cert.dipendente.cognome}", 1, 0, 'L', 1)
            pdf.cell(80, 10, cert.corso.nome_corso, 1, 0, 'L', 1)
            pdf.cell(40, 10, cert.data_scadenza_calcolata.strftime('%d/%m/%Y'), 1, 1, 'C', 1)
            fill = not fill

    # Table for overdue certificates
    if overdue_certificates:
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Certificati Scaduti non Rinnovati', 0, 1, 'L')
        pdf.ln(5)

        # Table Header
        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(254, 242, 242) # Light Red
        pdf.cell(60, 10, 'Dipendente', 1, 0, 'C', 1)
        pdf.cell(80, 10, 'Corso', 1, 0, 'C', 1)
        pdf.cell(40, 10, 'Data Scadenza', 1, 1, 'C', 1)

        # Table Rows
        pdf.set_font('Arial', '', 9)
        fill = False
        for cert in overdue_certificates:
            pdf.set_fill_color(255, 255, 255) if not fill else pdf.set_fill_color(245, 245, 245)
            pdf.cell(60, 10, f"{cert.dipendente.nome} {cert.dipendente.cognome}", 1, 0, 'L', 1)
            pdf.cell(80, 10, cert.corso.nome_corso, 1, 0, 'L', 1)
            pdf.cell(40, 10, cert.data_scadenza_calcolata.strftime('%d/%m/%Y'), 1, 1, 'C', 1)
            fill = not fill

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf_path = tmp_file.name
        pdf.output(pdf_path)
    return pdf_path

def send_email_notification(pdf_path, expiring_count, overdue_count):
    """Sends an email with the PDF report attached."""
    to_emails = [email.strip() for email in settings.EMAIL_RECIPIENTS_TO.split(',') if email.strip()]
    cc_emails = [email.strip() for email in settings.EMAIL_RECIPIENTS_CC.split(',') if email.strip()]

    if not to_emails:
        logging.warning("Nessun destinatario (To) configurato. Invio email annullato.")
        return

    msg = MIMEMultipart()
    msg['From'] = settings.SMTP_USER
    msg['To'] = ", ".join(to_emails)
    if cc_emails:
        msg['Cc'] = ", ".join(cc_emails)
    msg['Subject'] = f"Report Scadenze Certificati - {date.today().strftime('%d/%m/%Y')}"

    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 14px; color: #333; }}
            .container {{ padding: 20px; border: 1px solid #ddd; border-radius: 8px; max-width: 600px; }}
            .header {{ font-size: 18px; font-weight: bold; color: #1F2937; }}
            .summary {{ margin-top: 20px; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #888; }}
        </style>
    </head>
    <body>
        <div class="container">
            <p class="header">Report Scadenze Certificati</p>
            <p>Buongiorno,</p>
            <p>In allegato il report PDF dettagliato contenente l'elenco dei certificati in scadenza e di quelli scaduti da oltre un mese per i quali non risulta ancora caricato un rinnovo.</p>
            <div class="summary">
                <p><b>Riepilogo:</b></p>
                <ul>
                    <li>Certificati in scadenza: <strong>{expiring_count}</strong></li>
                    <li>Certificati scaduti non rinnovati: <strong>{overdue_count}</strong></li>
                </ul>
            </div>
            <p>Cordiali saluti,</p>
            <br>
            <p class="footer">Email generata automaticamente dal Software Intelleo</p>
        </div>
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html'))

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
            server.send_message(msg, from_addr=settings.SMTP_USER, to_addrs=to_emails + cc_emails)
            logging.info(f"Email di notifica inviata con successo a: {', '.join(to_emails)}")
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
