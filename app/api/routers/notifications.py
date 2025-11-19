from fastapi import APIRouter, HTTPException
from app.services.notification_service import check_and_send_alerts

router = APIRouter()

@router.post("/send-manual-alert")
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
