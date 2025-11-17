from fastapi import APIRouter, Depends
from app.services.notification_service import check_and_send_alerts

router = APIRouter()

@router.post("/send-manual-alert")
async def send_manual_alert():
    """
    Manually triggers the check for expiring and overdue certificates and sends the notification email.
    """
    try:
        check_and_send_alerts()
        return {"message": "Processo di notifica avviato con successo."}
    except Exception as e:
        return {"error": f"Errore durante l'invio della notifica: {e}"}
