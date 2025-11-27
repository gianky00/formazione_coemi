from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from app.services.notification_service import check_and_send_alerts, get_report_data, generate_pdf_report_in_memory
from app.api import deps
from app.db.session import get_db
from app.core.config import settings

router = APIRouter()

@router.get("/export-report")
def export_report(db: Session = Depends(get_db)):
    """
    Generates and downloads the PDF report of expiring/overdue certificates.
    """
    try:
        expiring_visite, expiring_corsi, overdue_certificates = get_report_data(db)

        pdf_bytes = generate_pdf_report_in_memory(
            expiring_visite=expiring_visite,
            expiring_corsi=expiring_corsi,
            overdue_certificates=overdue_certificates,
            visite_threshold=settings.ALERT_THRESHOLD_DAYS_VISITE,
            corsi_threshold=settings.ALERT_THRESHOLD_DAYS
        )

        return Response(content=bytes(pdf_bytes), media_type="application/pdf", headers={
            "Content-Disposition": "attachment; filename=report_scadenze.pdf"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante la generazione del report: {e}")

@router.post("/send-manual-alert", dependencies=[Depends(deps.check_write_permission)])
async def send_manual_alert():
    """
    Manually triggers the check for expiring and overdue certificates and sends the notification email.
    """
    try:
        check_and_send_alerts()
        return {"message": "Email di notifica inviata con successo."}
    except ConnectionAbortedError as e:
        # This catches the specific SMTP errors we are now raising
        raise HTTPException(status_code=500, detail=f"Errore durante l'invio della notifica: {e}")
    except Exception as e:
        # Catch-all for any other unexpected errors
        raise HTTPException(status_code=500, detail=f"Si è verificato un errore imprevisto: {e}")
