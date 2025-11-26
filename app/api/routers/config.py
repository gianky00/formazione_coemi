from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.core.db_security import db_security
from app.utils.audit import log_security_action
from app.db.session import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel

router = APIRouter()

import shutil
from pathlib import Path

class SecurityModeSchema(BaseModel):
    locked: bool

class MoveDatabaseSchema(BaseModel):
    new_path: str

@router.post("/config/move-database", dependencies=[Depends(deps.check_write_permission)])
def move_database(
    payload: MoveDatabaseSchema,
    db: Session = Depends(get_db),
    current_user: deps.User = Depends(deps.get_current_active_admin)
):
    """
    Moves the database file to a new user-specified path.
    """
    new_path = Path(payload.new_path)
    if not new_path.is_dir():
        raise HTTPException(status_code=400, detail="Il percorso specificato non è una cartella valida.")

    try:
        db_security.move_database(new_path)
        log_security_action(db, current_user, "MOVE_DATABASE", f"Database moved to: {new_path}", category="SYSTEM", severity="CRITICAL")
        return {"message": "Database spostato con successo."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impossibile spostare il database: {str(e)}")

@router.get("/db-security/status")
def get_security_status(
    current_user: deps.User = Depends(deps.get_current_active_admin)
):
    """
    Returns the current security status of the database (Locked/Encrypted or Unlocked/Plain).
    Only accessible by Admins.
    """
    return {"locked": db_security.is_locked_mode}

@router.post("/db-security/toggle", dependencies=[Depends(deps.check_write_permission)])
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
