from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Body, HTTPException, Request
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api import deps
from app.db.models import AuditLog, User as UserModel
from app.schemas.schemas import AuditLogSchema
from app.utils.audit import log_security_action
import pandas as pd
import csv
import io

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

def sanitize_csv_cell(value):
    """
    Sanitizes a CSV cell value to prevent Formula Injection (CSV Injection).
    Prepends a single quote if the value starts with =, @, +, or -.
    """
    if isinstance(value, str) and value.startswith(('=', '@', '+', '-')):
        return "'" + value
    return value

@router.get("/export", response_class=StreamingResponse)
def export_audit_logs(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Export all audit logs as CSV via streaming to prevent OOM.
    Sanitizes values to prevent CSV Injection.
    """
    filename = f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

    def iter_logs():
        # BOM for Excel compatibility
        yield '\ufeff'

        # Buffer for writing CSV rows
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)

        # Write Header
        writer.writerow(["Timestamp", "Category", "Action", "User", "Details", "IP Address", "Severity", "Device ID"])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        # Query with yield_per to fetch in chunks from DB cursor
        query = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).yield_per(1000)

        for log in query:
            user_str = log.username or (f"ID {log.user_id}" if log.user_id else "System")

            row = [
                log.timestamp.isoformat() if log.timestamp else "",
                log.category,
                log.action,
                user_str,
                log.details,
                log.ip_address,
                log.severity,
                log.device_id
            ]

            # Sanitize row
            sanitized_row = [sanitize_csv_cell(val) for val in row]

            writer.writerow(sanitized_row)
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

    return StreamingResponse(
        iter_logs(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/", response_model=List[AuditLogSchema])
def read_audit_logs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: UserModel = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Retrieve audit logs with filtering (Admin only).
    """
    query = db.query(AuditLog)

    if search:
        search_lower = f"%{search}%"
        query = query.filter(
            or_(
                AuditLog.action.ilike(search_lower),
                AuditLog.details.ilike(search_lower),
                AuditLog.username.ilike(search_lower),
                AuditLog.category.ilike(search_lower)
            )
        )

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
