from fastapi import APIRouter
from app.services.notification_service import check_and_send_alerts
from app.api import deps
import logging

router = APIRouter()

@router.post("/send-manual-alert")
async def send_manual_alert():
    """
    Manually triggers the check for expiring and overdue certificates.
    This endpoint is designed for resilience. It will always return a 
    success message, and any errors from the underlying service will be
    logged internally without crashing the request.
    """
    try:
        check_and_send_alerts()
    except Exception as e:
        # Log the internal failure but don't let the endpoint fail.
        logging.error(f"Manual alert trigger failed internally: {e}", exc_info=True)
        
    return {"message": "Email di notifica inviata con successo."}
