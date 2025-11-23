from sqlalchemy.orm import Session
from typing import Optional
from app.db.models import AuditLog, User

def log_security_action(db: Session, user: Optional[User], action: str, details: str = None):
    """
    Logs a security-critical action to the database.
    If user is None, it's logged as 'SYSTEM'.
    """
    log_entry = AuditLog(
        user_id=user.id if user else None,
        username=user.username if user else "SYSTEM",
        action=action,
        details=details
    )
    db.add(log_entry)
    db.commit()
