import logging
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.db.models import AuditLog, User as UserModel
from app.db.session import get_db
from app.schemas.schemas import AuditLogSchema
from app.utils.audit import log_security_action

router = APIRouter(prefix="/audit", tags=["audit"])

logger = logging.getLogger(__name__)


@router.get("/categories", response_model=list[str])
def read_audit_categories(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(deps.get_current_active_admin)],
) -> Any:
    """Ritorna le categorie uniche presenti nei log di audit."""
    categories = db.query(AuditLog.category).distinct().all()
    return [c[0] for c in categories if c[0]]


def sanitize_csv_cell(value: Any) -> str:
    """Sanitizes a value for CSV output."""
    if value is None:
        return ""
    return str(value).replace(";", ",")


@router.get("/export", response_class=StreamingResponse)
def export_audit_logs(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(deps.get_current_active_admin)],
) -> Any:
    """Esporta i log di audit in formato CSV."""

    def iter_logs() -> Any:
        # UTF-8 BOM for Excel compatibility (yield as bytes to avoid auto-encoding issues)
        yield b"\xef\xbb\xbf"
        # Header
        yield "ID;Timestamp;User;Action;Category;IP;Geolocation;Severity;Details;Changes\r\n"

        # Data (streamed from DB)
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).yield_per(100)
        for log in logs:
            row = [
                log.id,
                log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                log.username or "SYSTEM",
                log.action,
                log.category or "",
                log.ip_address or "",
                log.geolocation or "",
                log.severity or "LOW",
                log.details or "",
                log.changes or "",
            ]
            sanitized_row = [sanitize_csv_cell(val) for val in row]
            yield ";".join(map(str, sanitized_row)) + "\r\n"

    return StreamingResponse(
        iter_logs(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=audit_logs_{datetime.now().strftime('%Y%m%d')}.csv"
        },
    )


@router.get("/", response_model=list[AuditLogSchema])
def read_audit_logs(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(deps.get_current_active_admin)],
    skip: int = 0,
    limit: int = 100,
    user_id: int | None = None,
    category: str | None = None,
    action: str | None = None,
    severity: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    search: str | None = None,
) -> Any:
    """Ritorna l'elenco dei log di audit con filtri opzionali."""
    query = db.query(AuditLog)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if category:
        query = query.filter(AuditLog.category == category)
    if action:
        query = query.filter(AuditLog.action == action)
    if severity:
        query = query.filter(AuditLog.severity == severity)
    if search:
        from sqlalchemy import or_

        query = query.filter(
            or_(
                AuditLog.username.ilike(f"%{search}%"),
                AuditLog.details.ilike(f"%{search}%"),
            )
        )
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        # If end_date is at midnight, assume it means "until the end of this day"
        if end_date.hour == 0 and end_date.minute == 0 and end_date.second == 0:
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        query = query.filter(AuditLog.timestamp <= end_date)

    return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=AuditLogSchema)
def create_audit_log(
    *,
    db: Annotated[Session, Depends(get_db)],
    request: Request,
    current_user: Annotated[UserModel, Depends(deps.get_current_user)],
    action: str = Body(..., embed=True),
    category: str | None = Body(None, embed=True),
    details: str | None = Body(None, embed=True),
    changes: str | None = Body(None, embed=True),
    severity: str = Body("LOW", embed=True),
) -> Any:
    """Crea manualmente una voce nel log di audit (usato dal frontend)."""
    log_security_action(
        db,
        current_user,
        action=action,
        details=details,
        category=category,
        changes=changes,
        severity=severity,
        request=request,
    )
    # Ritorna l'ultimo log creato per l'utente
    return (
        db.query(AuditLog)
        .filter(AuditLog.user_id == current_user.id)
        .order_by(AuditLog.timestamp.desc())
        .first()
    )
