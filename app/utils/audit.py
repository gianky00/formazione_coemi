import threading
import logging
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import Request
from app.db.models import AuditLog, User
from app.services.geo_service import GeoLocationService

logger = logging.getLogger(__name__)

def _extract_request_info(request):
    ip_address = None
    user_agent = None
    geolocation = None
    device_id = None

    if request:
        try:
            ip_address = request.client.host if request.client else "Unknown"
            user_agent = request.headers.get("user-agent")
            device_id = request.headers.get("X-Device-ID")
            if ip_address:
                geolocation = GeoLocationService.get_location(ip_address)
        except Exception as e:
            logger.warning(f"Error extracting request details for audit: {e}")

    return ip_address, user_agent, geolocation, device_id

def _send_alert(user, action, details, ip_address, geolocation, timestamp):
    try:
        from app.services.notification_service import send_security_alert_email

        subject = f"SECURITY ALERT: {action}"
        body = f"""
        <h3>Critical Security Event Detected</h3>
        <p><strong>Action:</strong> {action}</p>
        <p><strong>Severity:</strong> <span style="color:red;">CRITICAL</span></p>
        <p><strong>User:</strong> {user.username if user else 'SYSTEM'}</p>
        <p><strong>IP:</strong> {ip_address} ({geolocation})</p>
        <p><strong>Details:</strong> {details}</p>
        <p><strong>Timestamp:</strong> {timestamp}</p>
        """
        send_security_alert_email(subject, body)
    except Exception as e:
        logger.error(f"Failed to trigger alert email: {e}")

def log_security_action(db: Session, user: Optional[User], action: str, details: str = None, category: str = None, request: Request = None, severity: str = "LOW", changes: str = None, device_id: str = None):
    """
    Logs a security-critical action to the database.
    If user is None, it's logged as 'SYSTEM'.
    """
    # S3776: Refactored to reduce complexity
    ip_address, user_agent, geolocation, req_device_id = _extract_request_info(request)

    # Prioritize explicitly passed device_id
    final_device_id = device_id or req_device_id

    log_entry = AuditLog(
        user_id=user.id if user else None,
        username=user.username if user else "SYSTEM",
        action=action,
        details=details,
        category=category,
        ip_address=ip_address,
        user_agent=user_agent,
        geolocation=geolocation,
        severity=severity,
        device_id=final_device_id,
        changes=changes
    )
    db.add(log_entry)
    db.commit()

    if severity == "CRITICAL":
        t = threading.Thread(target=_send_alert, args=(user, action, details, ip_address, geolocation, log_entry.timestamp))
        t.start()
