
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import tempfile
from fpdf import FPDF
from datetime import date, timedelta, datetime
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
        self.image('desktop_app/assets/logo.png', 10, 8, 45) # Increased logo size
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(0, 10, f"Report scadenze al {date.today().strftime('%d/%m/%Y')}", 0, 0, 'C')
        # Line break
        self.ln(20)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Confidentiality Notice
        self.cell(0, 10, 'Restricted | Internal Use Only', 0, 0, 'L')
        # Page number
        self.cell(0, 10, 'Pagina ' + str(self.page_no()) + '/{nb}', 0, 0, 'R')

def generate_pdf_report_in_memory(expiring_certificates, overdue_certificates):
    """Generates a professional PDF report and returns its content as bytes."""
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    # Table for expiring certificates
    if expiring_certificates:
        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(240, 248, 255)
        pdf.cell(30, 10, 'Matricola', 1, 0, 'C', 1)
        pdf.cell(50, 10, 'Dipendente', 1, 0, 'C', 1)
        pdf.cell(70, 10, 'Categoria', 1, 0, 'C', 1)
        pdf.cell(40, 10, 'Data Scadenza', 1, 1, 'C', 1)
        pdf.set_font('Arial', '', 9)
        fill = False
        for cert in expiring_certificates:
            pdf.set_fill_color(255, 255, 255) if not fill else pdf.set_fill_color(245, 245, 245)
            pdf.cell(30, 10, cert.dipendente.matricola if cert.dipendente else 'N/A', 1, 0, 'C', 1)
            pdf.cell(50, 10, f"{cert.dipendente.nome} {cert.dipendente.cognome}" if cert.dipendente else 'N/A', 1, 0, 'L', 1)
            pdf.cell(70, 10, cert.corso.categoria_corso, 1, 0, 'L', 1)
            pdf.cell(40, 10, cert.data_scadenza_calcolata.strftime('%d/%m/%Y'), 1, 1, 'C', 1)
            fill = not fill

    # Table for overdue certificates
    if overdue_certificates:
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(254, 242, 242)
        pdf.cell(30, 10, 'Matricola', 1, 0, 'C', 1)
        pdf.cell(50, 10, 'Dipendente', 1, 0, 'C', 1)
        pdf.cell(70, 10, 'Categoria', 1, 0, 'C', 1)
        pdf.cell(40, 10, 'Data Scadenza', 1, 1, 'C', 1)
        pdf.set_font('Arial', '', 9)
        fill = False
        for cert in overdue_certificates:
            pdf.set_fill_color(255, 255, 255) if not fill else pdf.set_fill_color(245, 245, 245)
            pdf.cell(30, 10, cert.dipendente.matricola if cert.dipendente else 'N/A', 1, 0, 'C', 1)
            pdf.cell(50, 10, f"{cert.dipendente.nome} {cert.dipendente.cognome}" if cert.dipendente else 'N/A', 1, 0, 'L', 1)
            pdf.cell(70, 10, cert.corso.categoria_corso, 1, 0, 'L', 1)
            pdf.cell(40, 10, cert.data_scadenza_calcolata.strftime('%d/%m/%Y'), 1, 1, 'C', 1)
            fill = not fill

    # Return PDF content as bytes
    return pdf.output(dest='S')

def send_email_notification(pdf_content_bytes, expiring_count, overdue_count):
    """Sends an email with the PDF report (from bytes) attached."""
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
    msg['Subject'] = f"Intelleo: Avviso documenti in scadenza - Report del {date.today().strftime('%d/%m/%Y')}"

    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 16px; color: #333; background-color: #f9fafb; margin: 0; padding: 20px; text-align: left; }}
            .wrapper {{ background-color: #ffffff; margin: 0; padding: 30px; border-radius: 12px; max-width: 600px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .header {{ font-size: 24px; font-weight: 700; color: #1F2937; border-bottom: 2px solid #F0F8FF; padding-bottom: 15px; margin-bottom: 20px; }}
            .summary-box {{ background-color: #F0F8FF; border-left: 4px solid #1D4ED8; padding: 15px; margin: 20px 0; border-radius: 4px; }}
            .summary-box p {{ margin: 0; font-size: 16px; color: #1F2937; }}
            .summary-box strong {{ font-size: 18px; }}
            .content p {{ line-height: 1.6; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #9CA3AF; text-align: left; }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <p class="header">Sistema di Monitoraggio Intelleo</p>
            <div class="content">
                <p>Questo è un avviso generato automaticamente dal sistema di monitoraggio delle scadenze.</p>
                <p>In allegato il report PDF dettagliato contenente l'analisi delle scadenze dei certificati alla data odierna.</p>
                <div class="summary-box">
                    <p><strong>Riepilogo Analisi:</strong></p>
                    <ul style="list-style-type: none; padding-left: 0; margin-top: 10px;">
                        <li style="margin-bottom: 5px;">Certificati in avvicinamento scadenza ({settings.ALERT_THRESHOLD_DAYS} GG): <strong>{expiring_count}</strong></li>
                        <li>Certificati scaduti non rinnovati: <strong>{overdue_count}</strong></li>
                    </ul>
                </div>
                <p>Si prega di prendere visione del report per le azioni di competenza.</p>
            </div>
            <p class="footer">Email generata il {datetime.now().strftime('%d/%m/%Y alle %H:%M:%S')} dal Software Intelleo</p>
        </div>
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html'))

    # Attach the PDF from bytes
    part = MIMEBase("application", "octet-stream")
    part.set_payload(pdf_content_bytes)
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename=Report_Scadenze_{date.today().strftime('%Y-%m-%d')}.pdf",
    )
    msg.attach(part)

    try:
        if settings.SMTP_PORT == 465:
            # Use SMTP_SSL for a secure connection from the start (for services like Gmail, Aruba SSL)
            conn_method = "SMTP_SSL"
            logging.info(f"Connecting to {settings.SMTP_HOST}:{settings.SMTP_PORT} using {conn_method}.")
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.set_debuglevel(1)
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg, from_addr=settings.SMTP_USER, to_addrs=to_emails + cc_emails)
        else:
            # Use standard SMTP and upgrade to TLS (for services like Outlook, Aruba STARTTLS)
            conn_method = "SMTP with STARTTLS"
            logging.info(f"Connecting to {settings.SMTP_HOST}:{settings.SMTP_PORT} using {conn_method}.")
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.set_debuglevel(1)
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg, from_addr=settings.SMTP_USER, to_addrs=to_emails + cc_emails)

        logging.info(f"Email notification sent successfully to: {', '.join(to_emails)} using {conn_method}.")

    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"SMTP Authentication Error with {conn_method}: {e}. Check SMTP_USER and SMTP_PASSWORD.")
        raise ConnectionAbortedError(f"SMTP Authentication Error: {e}")
    except smtplib.SMTPConnectError as e:
        logging.error(f"SMTP Connection Error with {conn_method}: {e}. Check SMTP_HOST and SMTP_PORT.")
        raise ConnectionAbortedError(f"SMTP Connection Error: {e}")
    except smtplib.SMTPException as e:
        logging.error(f"Generic SMTP Error with {conn_method} while sending email: {e}")
        raise ConnectionAbortedError(f"Generic SMTP Error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred with {conn_method} while sending email: {e}", exc_info=True)
        raise ConnectionAbortedError(f"An unexpected error occurred: {e}")

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
        expiring_limit_attestati = today + timedelta(days=settings.ALERT_THRESHOLD_DAYS)
        expiring_limit_visite = today + timedelta(days=settings.ALERT_THRESHOLD_DAYS_VISITE)

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
            pdf_content_bytes = generate_pdf_report_in_memory(expiring_certificates, overdue_certificates)
            send_email_notification(pdf_content_bytes, len(expiring_certificates), len(overdue_certificates))
        else:
            logging.info("Nessuna notifica di scadenza da inviare oggi.")

    finally:
        db.close()
