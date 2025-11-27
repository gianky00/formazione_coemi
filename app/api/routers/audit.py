from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Body, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api import deps
from app.db.models import AuditLog, User as UserModel
from app.schemas.schemas import AuditLogSchema
from app.utils.audit import log_security_action

router = APIRouter()

@router.get("/categories", response_model=List[str])
def read_audit_categories(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Retrieve distinct audit log categories (Admin only).
    """
    categories = db.query(AuditLog.category).distinct().filter(AuditLog.category.isnot(None)).all()
    # Flatten list of tuples
    return sorted([c[0] for c in categories if c[0]])

@router.get("/", response_model=List[AuditLogSchema])
def read_audit_logs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    category: Optional[str] = None,
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

    if category:
        query = query.filter(AuditLog.category == category)

    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)

    if end_date:
        # Fix: If end_date is exactly midnight (00:00:00), assume it's a date selection
        # and we want to include the entire day (up to 23:59:59).
        if end_date.hour == 0 and end_date.minute == 0 and end_date.second == 0:
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        query = query.filter(AuditLog.timestamp <= end_date)

    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    return logs

@router.post("/", response_model=AuditLogSchema)
def create_audit_log(
    *,
    request: Request,
    db: Session = Depends(get_db),
    action: str = Body(..., embed=True),
    category: Optional[str] = Body(None, embed=True),
    details: Optional[str] = Body(None, embed=True),
    changes: Optional[str] = Body(None, embed=True),
    severity: Optional[str] = Body("LOW", embed=True),
    current_user: UserModel = Depends(deps.get_current_user),
) -> Any:
    """
    Create an audit log entry (Authenticated users).
    Useful for logging client-side actions like configuration changes.
    """
    log_security_action(
        db,
        current_user,
        action,
        details=details,
        category=category,
        request=request,
        severity=severity,
        changes=changes
    )

    # Retrieve the created log to return it
    log_entry = db.query(AuditLog).filter(AuditLog.user_id == current_user.id).order_by(AuditLog.id.desc()).first()
    return log_entry
