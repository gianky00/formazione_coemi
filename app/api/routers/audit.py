from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api import deps
from app.db.models import AuditLog, User as UserModel
from app.schemas.schemas import AuditLogSchema
from app.utils.audit import log_security_action

router = APIRouter()

@router.get("/", response_model=List[AuditLogSchema])
def read_audit_logs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: UserModel = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Retrieve audit logs with filtering (Admin only).
    """
    query = db.query(AuditLog)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)

    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)

    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    return logs

@router.post("/", response_model=AuditLogSchema)
def create_audit_log(
    *,
    db: Session = Depends(get_db),
    action: str = Body(..., embed=True),
    details: Optional[str] = Body(None, embed=True),
    current_user: UserModel = Depends(deps.get_current_user),
) -> Any:
    """
    Create an audit log entry (Authenticated users).
    Useful for logging client-side actions like configuration changes.
    """
    log_entry = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=action,
        details=details
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
