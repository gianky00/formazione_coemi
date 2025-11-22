from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api import deps
from app.db.models import AuditLog, User as UserModel
from app.schemas.schemas import AuditLogSchema

router = APIRouter()

@router.get("/", response_model=List[AuditLogSchema])
def read_audit_logs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Retrieve audit logs (Admin only).
    """
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    return logs
