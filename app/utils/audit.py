from sqlalchemy.orm import Session
from typing import Optional
from fastapi import Request
from app.db.models import AuditLog, User
from app.services.geo_service import GeoLocationService

def log_security_action(db: Session, user: Optional[User], action: str, details: str = None, category: str = None, request: Request = None, severity: str = "LOW"):
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
        severity=severity
    )
    db.add(log_entry)
    db.commit()
