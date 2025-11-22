from sqlalchemy.orm import Session
from app.db.models import AuditLog, User

def log_security_action(db: Session, user: User, action: str, details: str = None):
    """
    Logs a security-critical action to the database.
    """
    log_entry = AuditLog(
        user_id=user.id,
        username=user.username,
        action=action,
        details=details
    )
    db.add(log_entry)
    db.commit()
