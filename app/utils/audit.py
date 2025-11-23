import threading
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import Request
from app.db.models import AuditLog, User
from app.services.geo_service import GeoLocationService

def log_security_action(db: Session, user: Optional[User], action: str, details: str = None, category: str = None, request: Request = None, severity: str = "LOW", changes: str = None, device_id: str = None):
    """
    Logs a security-critical action to the database.
    If user is None, it's logged as 'SYSTEM'.
    """
    ip_address = None
    user_agent = None
    geolocation = None

    if request:
        try:
            ip_address = request.client.host if request.client else "Unknown"
            user_agent = request.headers.get("user-agent")
            if not device_id:
                device_id = request.headers.get("X-Device-ID")

            # Resolve geolocation
            if ip_address:
                geolocation = GeoLocationService.get_location(ip_address)
        except Exception:
            pass # resilient logging

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
        device_id=device_id,
        changes=changes
    )
    db.add(log_entry)
    db.commit()

    # Active Alert for Critical Events
    if severity == "CRITICAL":
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
            <p><strong>Timestamp:</strong> {log_entry.timestamp}</p>
            """

            # Send in background thread
            t = threading.Thread(target=send_security_alert_email, args=(subject, body))
            t.start()
        except Exception as e:
            print(f"Failed to trigger alert email: {e}")
