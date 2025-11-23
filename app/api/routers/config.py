from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.core.db_security import db_security
from app.utils.audit import log_security_action
from app.db.session import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel

router = APIRouter()

class SecurityModeSchema(BaseModel):
    locked: bool

@router.get("/db-security/status")
def get_security_status(
    current_user: deps.User = Depends(deps.get_current_active_admin)
):
    """
    Returns the current security status of the database (Locked/Encrypted or Unlocked/Plain).
    Only accessible by Admins.
    """
    return {"locked": db_security.is_locked_mode}

@router.post("/db-security/toggle")
def toggle_security_mode(
    payload: SecurityModeSchema,
    db: Session = Depends(get_db),
    current_user: deps.User = Depends(deps.get_current_active_admin)
):
    """
    Toggles the database security mode.
    - If locked=True: Encrypts the database.
    - If locked=False: Decrypts the database (Plain text).
    Only accessible by Admins.
    """
    try:
        db_security.toggle_security_mode(payload.locked)
        action = "LOCK_DB" if payload.locked else "UNLOCK_DB"
        log_security_action(db, current_user, action, f"Database security mode changed to: {'LOCKED' if payload.locked else 'UNLOCKED'}", category="SYSTEM", severity="CRITICAL")
        return {"locked": db_security.is_locked_mode, "message": "Security mode updated successfully."}
    except Exception as e:
        # Log the error locally too
        print(f"Error toggling DB security: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to toggle security mode: {str(e)}")
