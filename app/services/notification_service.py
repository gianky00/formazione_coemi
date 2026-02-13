import logging
import os
import tempasyncio
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any

from fpdf import FPDF
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Certificato, Dipendente, ValidationStatus
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

DATE_FORMAT_DMY = "%d/%m/%Y"


def safe_text(text: Any) -> str:
    """Standardizes text for PDF generation by removing non-latin characters."""
    if text is None:
        return ""
    return str(text).encode("latin-1", "replace").decode("latin-1")


class PDF(FPDF):
    def header(self) -> None:
        # Logo
        # self.image('logo.png', 10, 8, 33)
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "COEMI - Report Scadenze Formazione", 0, 1, "C")
        self.set_font("Arial", "I", 10)
        self.cell(0, 10, f"Generato il: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, "C")
        self.ln(20)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, "Restricted | Internal Use Only", 0, 0, "L")
        self.cell(0, 10, "Pagina " + str(self.page_no()) + "/{nb}", 0, 0, "R")


def _draw_table_header(
    pdf: Any, header: list[str], col_widths: list[int], color: tuple[int, int, int]
) -> None:
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(color[0], color[1], color[2])
    for i, header_text in enumerate(header):
        pdf.cell(col_widths[i], 10, safe_text(header_text), 1, 0, "C", True)
    pdf.ln()


def _draw_table_rows(
    pdf: Any,
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
        elif hasattr(cert, "matricola_raw") and getattr(cert, "matricola_raw"):
            matricola = str(getattr(cert, "matricola_raw"))
        if not matricola:
            matricola = "-"

        # Get dipendente name
        dipendente_nome = ""
        if cert.dipendente:
            cognome = cert.dipendente.cognome or ""
            nome = cert.dipendente.nome or ""
            dipendente_nome = f"{cognome} {nome}".strip()
        if not dipendente_nome and hasattr(cert, "nome_dipendente_raw") and getattr(cert, "nome_dipendente_raw"):
            dipendente_nome = str(getattr(cert, "nome_dipendente_raw"))
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
        pdf.cell(col_widths[4], 8, safe_text(cert.corso.nome_corso if cert.corso else "-"), 1, 0, "L")
        pdf.cell(col_widths[5], 8, data_scadenza, 1, 1, "C")
        row_num += 1


def get_report_data(db: Session) -> tuple[list[Certificato], list[Certificato], list[Certificato]]:
    """
    Retrieves the certificates that are expiring or overdue for the report.
    """
    today = date.today()
    threshold_corsi = today + timedelta(days=settings.ALERT_THRESHOLD_DAYS)
    threshold_visite = today + timedelta(days=settings.ALERT_THRESHOLD_DAYS_VISITE)

    # Base query: only manual validated certificates
    base_q = db.query(Certificato).filter(Certificato.stato_validazione == ValidationStatus.MANUAL)

    # 1. Overdue (Expired)
    overdue = (
        base_q.filter(Certificato.data_scadenza_calcolata < today)
        .order_by(Certificato.data_scadenza_calcolata.asc())
        .all()
    )

    # 2. Expiring Courses (Not Visite)
    expiring_corsi = (
        base_q.join(Certificato.corso)
        .filter(
            Certificato.data_scadenza_calcolata >= today,
            Certificato.data_scadenza_calcolata <= threshold_corsi,
            Certificato.corso.has(Certificato.corso.property.mapper.class_.categoria_corso != "VISITA MEDICA"),
        )
        .order_by(Certificato.data_scadenza_calcolata.asc())
        .all()
    )

    # 3. Expiring Medical Visits
    expiring_visite = (
        base_q.join(Certificato.corso)
        .filter(
            Certificato.data_scadenza_calcolata >= today,
            Certificato.data_scadenza_calcolata <= threshold_visite,
            Certificato.corso.has(Certificato.corso.property.mapper.class_.categoria_corso == "VISITA MEDICA"),
        )
        .order_by(Certificato.data_scadenza_calcolata.asc())
        .all()
    )

    return expiring_visite, expiring_corsi, overdue


def generate_pdf_report_in_memory(
    expiring_visite: list[Certificato],
    expiring_corsi: list[Certificato],
    overdue_certificates: list[Certificato],
    visite_threshold: int,
    corsi_threshold: int,
) -> bytes:
    """
    Generates the PDF report and returns it as bytes.
    """
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    col_widths = [10, 20, 50, 35, 55, 20]
    header = ["#", "Matr.", "Dipendente", "Categoria", "Corso/Visita", "Scadenza"]

    # --- SECTION 1: OVERDUE ---
    if overdue_certificates:
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 10, "SCADUTI (AZIONI IMMEDIATE RICHIESTE)", 0, 1, "L")
        pdf.set_text_color(0, 0, 0)
        _draw_table_header(pdf, header, col_widths, (255, 200, 200))
        _draw_table_rows(pdf, overdue_certificates, col_widths, header, (255, 200, 200))
        pdf.ln(10)

    # --- SECTION 2: EXPIRING VISITE ---
    if expiring_visite:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"VISITE MEDICHE IN SCADENZA (PROSSIMI {visite_threshold} GG)", 0, 1, "L")
        _draw_table_header(pdf, header, col_widths, (255, 255, 200))
        _draw_table_rows(pdf, expiring_visite, col_widths, header, (255, 255, 200))
        pdf.ln(10)

    # --- SECTION 3: EXPIRING CORSI ---
    if expiring_corsi:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"CORSI IN SCADENZA (PROSSIMI {corsi_threshold} GG)", 0, 1, "L")
        _draw_table_header(pdf, header, col_widths, (200, 255, 200))
        _draw_table_rows(pdf, expiring_corsi, col_widths, header, (200, 255, 200))

    if not overdue_certificates and not expiring_visite and not expiring_corsi:
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, "Nessun certificato in scadenza o scaduto rilevato.", 0, 1, "C")

    return bytes(pdf.output(dest="S"))


def check_and_send_alerts() -> None:
    """
    Checks for expiring certificates and sends email alerts.
    """
    db = SessionLocal()
    try:
        expiring_visite, expiring_corsi, overdue = get_report_data(db)

        if not (expiring_visite or expiring_corsi or overdue):
            logger.info("No expiring or overdue certificates found. Skipping email.")
            return

        # Generate report
        pdf_content = generate_pdf_report_in_memory(
            expiring_visite,
            expiring_corsi,
            overdue,
            settings.ALERT_THRESHOLD_DAYS_VISITE,
            settings.ALERT_THRESHOLD_DAYS,
        )

        # Prepare summary for email body
        summary = f"""
        Riepilogo Scadenze Formazione e Visite Mediche:
        - Certificati SCADUTI: {len(overdue)}
        - Visite Mediche in scadenza: {len(expiring_visite)}
        - Corsi di formazione in scadenza: {len(expiring_corsi)}

        In allegato il report dettagliato in formato PDF.
        """

        # Send email (using existing settings logic)
        from app.utils.security import send_email_with_attachment

        recipients = settings.EMAIL_RECIPIENTS_TO.split(",") if settings.EMAIL_RECIPIENTS_TO else []
        cc = settings.EMAIL_RECIPIENTS_CC.split(",") if settings.EMAIL_RECIPIENTS_CC else []

        if recipients:
            success = send_email_with_attachment(
                subject=f"REPORT SCADENZE FORMAZIONE - {datetime.now().strftime('%d/%m/%Y')}",
                body=summary,
                to_emails=recipients,
                cc_emails=cc,
                attachment_data=pdf_content,
                attachment_filename="report_scadenze.pdf",
            )
            if success:
                logger.info("Alert email sent successfully.")
            else:
                logger.error("Failed to send alert email.")
        else:
            logger.warning("No email recipients configured. Alert not sent.")

    except Exception as e:
        logger.error(f"Error during alert check: {e}", exc_info=True)
    finally:
        db.close()
