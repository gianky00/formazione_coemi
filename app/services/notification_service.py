
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
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

def generate_pdf_report_in_memory(expiring_visite, expiring_corsi, overdue_certificates, visite_threshold, corsi_threshold):
    """Generates a professional PDF report and returns its content as bytes."""
    try:
        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)

        # Table for expiring certificates
        if expiring_corsi:
            pdf.set_font('Arial', 'B', 10)
            pdf.set_fill_color(240, 248, 255)
            pdf.cell(30, 10, 'Matricola', 1, 0, 'C', 1)
            pdf.cell(50, 10, 'Dipendente', 1, 0, 'C', 1)
            pdf.cell(70, 10, 'Categoria', 1, 0, 'C', 1)
            pdf.cell(40, 10, 'Data Scadenza', 1, 1, 'C', 1)
            pdf.set_font('Arial', '', 9)
            fill = False
            for cert in expiring_corsi:
                matricola = cert.dipendente.matricola if cert.dipendente and cert.dipendente.matricola is not None else "N/A"
                dipendente_nome = f"{cert.dipendente.nome or ''} {cert.dipendente.cognome or ''}".strip() if cert.dipendente else "N/A"
                categoria = cert.corso.categoria_corso if cert.corso else "N/A"
                data_scadenza = cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else "N/A"

                pdf.set_fill_color(255, 255, 255) if not fill else pdf.set_fill_color(245, 245, 245)
                pdf.cell(30, 10, matricola, 1, 0, 'C', 1)
                pdf.cell(50, 10, dipendente_nome, 1, 0, 'L', 1)
                pdf.cell(70, 10, categoria, 1, 0, 'L', 1)
                pdf.cell(40, 10, data_scadenza, 1, 1, 'C', 1)
                fill = not fill

        if expiring_visite:
            pdf.ln(10)
            pdf.set_font('Arial', 'B', 10)
            pdf.set_fill_color(240, 248, 255)
            pdf.cell(30, 10, 'Matricola', 1, 0, 'C', 1)
            pdf.cell(50, 10, 'Dipendente', 1, 0, 'C', 1)
            pdf.cell(70, 10, 'Categoria', 1, 0, 'C', 1)
            pdf.cell(40, 10, 'Data Scadenza', 1, 1, 'C', 1)
            pdf.set_font('Arial', '', 9)
            fill = False
            for cert in expiring_visite:
                matricola = cert.dipendente.matricola if cert.dipendente and cert.dipendente.matricola is not None else "N/A"
                dipendente_nome = f"{cert.dipendente.nome or ''} {cert.dipendente.cognome or ''}".strip() if cert.dipendente else "N/A"
                categoria = cert.corso.categoria_corso if cert.corso else "N/A"
                data_scadenza = cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else "N/A"

                pdf.set_fill_color(255, 255, 255) if not fill else pdf.set_fill_color(245, 245, 245)
                pdf.cell(30, 10, matricola, 1, 0, 'C', 1)
                pdf.cell(50, 10, dipendente_nome, 1, 0, 'L', 1)
                pdf.cell(70, 10, categoria, 1, 0, 'L', 1)
                pdf.cell(40, 10, data_scadenza, 1, 1, 'C', 1)
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
                matricola = cert.dipendente.matricola if cert.dipendente and cert.dipendente.matricola is not None else "N/A"
                dipendente_nome = f"{cert.dipendente.nome or ''} {cert.dipendente.cognome or ''}".strip() if cert.dipendente else "N/A"
                categoria = cert.corso.categoria_corso if cert.corso else "N/A"
                data_scadenza = cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else "N/A"

                pdf.set_fill_color(255, 255, 255) if not fill else pdf.set_fill_color(245, 245, 245)
                pdf.cell(30, 10, matricola, 1, 0, 'C', 1)
                pdf.cell(50, 10, dipendente_nome, 1, 0, 'L', 1)
                pdf.cell(70, 10, categoria, 1, 0, 'L', 1)
                pdf.cell(40, 10, data_scadenza, 1, 1, 'C', 1)
                fill = not fill

        # Return PDF content as bytes
        return pdf.output(dest='S')
    except FileNotFoundError as e:
        logging.error(f"Errore durante la generazione del PDF: File non trovato, probabilmente il logo. {e}")
        raise ValueError(f"Impossibile generare il PDF: assicurarsi che il file 'desktop_app/assets/logo.png' esista.")
    except Exception as e:
        logging.error(f"Errore imprevisto durante la generazione del PDF: {e}", exc_info=True)
        raise ValueError(f"Si è verificato un errore imprevisto durante la creazione del report PDF: {e}")

def send_email_notification(pdf_content_bytes, expiring_corsi_count, expiring_visite_count, overdue_count, corsi_threshold, visite_threshold):
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
            .wrapper {{ background-color: #ffffff; margin: 0 auto; padding: 30px; border-radius: 12px; max-width: 600px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; padding-bottom: 15px; margin-bottom: 20px; border-bottom: 1px solid #e5e7eb; }}
            .summary-box {{ background-color: #F0F8FF; border-left: 4px solid #1D4ED8; padding: 15px; margin: 20px 0; border-radius: 4px; }}
            .summary-box p {{ margin: 0; font-size: 16px; color: #1F2937; }}
            .summary-box strong {{ font-size: 18px; }}
            .content p {{ line-height: 1.6; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #9CA3AF; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="header">
                <img src="cid:logo" alt="Logo" style="width: 150px; margin-bottom: 10px;">
            </div>
            <div class="content">
                <p>Questo è un avviso generato automaticamente dal sistema di monitoraggio delle scadenze.</p>
                <p>In allegato il report PDF dettagliato contenente l'analisi delle scadenze dei certificati alla data odierna.</p>
                <div class="summary-box">
                    <p><strong>Riepilogo Analisi:</strong></p>
                    <ul style="list-style-type: none; padding-left: 0; margin-top: 10px;">
                        <li style="margin-bottom: 5px;">Certificati in avvicinamento scadenza ({corsi_threshold} giorni): <strong>{expiring_corsi_count}</strong></li>
                        <li style="margin-bottom: 5px;">Visite mediche in avvicinamento scadenza ({visite_threshold} giorni): <strong>{expiring_visite_count}</strong></li>
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

    # --- Logo Embedding ---
    try:
        with open('desktop_app/assets/logo.png', 'rb') as f:
            logo_data = f.read()
        logo_image = MIMEImage(logo_data, name='logo.png')
        logo_image.add_header('Content-ID', '<logo>')
        logo_image.add_header('Content-Disposition', 'inline', filename='logo.png')
        msg.attach(logo_image)
    except FileNotFoundError:
        logging.warning("File del logo non trovato in 'desktop_app/assets/logo.png'. L'email verrà inviata senza logo.")
    # --- End Logo Embedding ---

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
        expiring_visite = []
        expiring_corsi = []
        overdue_certificates = []

        expiring_limit_attestati = today + timedelta(days=settings.ALERT_THRESHOLD_DAYS)
        expiring_limit_visite = today + timedelta(days=settings.ALERT_THRESHOLD_DAYS_VISITE)

        all_certs = db.query(Certificato).all()

        for cert in all_certs:
            if not cert.data_scadenza_calcolata or not cert.corso:
                continue

            # Check for expiring certificates and separate them
            if cert.corso.categoria_corso == "VISITA MEDICA":
                if today < cert.data_scadenza_calcolata <= expiring_limit_visite:
                    expiring_visite.append(cert)
            else:
                if today < cert.data_scadenza_calcolata <= expiring_limit_attestati:
                    expiring_corsi.append(cert)

            # Check for overdue and un-renewed certificates
            if cert.data_scadenza_calcolata < today:
                status = certificate_logic.get_certificate_status(db, cert)
                if status == "scaduto":
                    overdue_certificates.append(cert)

        total_expiring = len(expiring_visite) + len(expiring_corsi)
        if total_expiring > 0 or overdue_certificates:
            logging.info(f"Trovati {total_expiring} certificati in scadenza ({len(expiring_visite)} visite, {len(expiring_corsi)} corsi) e {len(overdue_certificates)} scaduti.")

            pdf_content_bytes = generate_pdf_report_in_memory(
                expiring_visite=expiring_visite,
                expiring_corsi=expiring_corsi,
                overdue_certificates=overdue_certificates,
                visite_threshold=settings.ALERT_THRESHOLD_DAYS_VISITE,
                corsi_threshold=settings.ALERT_THRESHOLD_DAYS
            )

            if not pdf_content_bytes:
                logging.error("La generazione del PDF è fallita e ha restituito un contenuto vuoto.")
                raise ValueError("La generazione del PDF è fallita.")

            send_email_notification(
                pdf_content_bytes=pdf_content_bytes,
                expiring_corsi_count=len(expiring_corsi),
                expiring_visite_count=len(expiring_visite),
                overdue_count=len(overdue_certificates),
                corsi_threshold=settings.ALERT_THRESHOLD_DAYS,
                visite_threshold=settings.ALERT_THRESHOLD_DAYS_VISITE
            )
        else:
            logging.info("Nessuna notifica di scadenza da inviare oggi.")

    finally:
        db.close()
