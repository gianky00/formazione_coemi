from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core.db_security import db_security
from app.db.models import User
from app.db.session import get_db

router = APIRouter(prefix="/system-config", tags=["config"])


@router.post("/move-database")
def move_database(
    new_path: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_active_admin)],
) -> Any:
    """Sposta il database in una nuova posizione (solo admin)."""
    # Logic is implemented in db_security but we need to expose it
    try:
        db_security.move_database(Path(new_path))
        return {"message": "Database spostato con successo."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/security-status")
def get_security_status(
    current_user: Annotated[User, Depends(deps.get_current_active_admin)],
) -> Any:
    """Ritorna lo stato della sicurezza del DB."""
    return {
        "is_locked_mode": db_security.is_locked_mode,
        "has_lock": db_security.has_lock,
        "is_read_only": db_security.is_read_only,
    }


@router.post("/toggle-security")
def toggle_security_mode(
    enable: bool,
    current_user: Annotated[User, Depends(deps.get_current_active_admin)],
) -> Any:
    """Attiva/Disattiva la modalità criptata (solo admin)."""
    db_security.toggle_security_mode(enable)
    return {"status": "ok", "is_locked_mode": db_security.is_locked_mode}
