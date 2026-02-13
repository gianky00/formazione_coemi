import logging
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.db.models import User
from app.db.session import SessionLocal, get_db
from app.schemas.system import SystemAction
from app.services.file_maintenance import organize_expired_files

router = APIRouter(prefix="/system", tags=["System"])
logger = logging.getLogger(__name__)

# Global flag to prevent concurrent maintenance tasks
MAINTENANCE_RUNNING = False


def run_maintenance_task() -> None:
    """
    Wrapper to run maintenance in a separate thread/session.
    """
    global MAINTENANCE_RUNNING
    if MAINTENANCE_RUNNING:
        logger.info("Maintenance task already running. Skipping.")
        return

    MAINTENANCE_RUNNING = True
    db = SessionLocal()  # Create independent session
    try:
        logger.info("Starting background maintenance task...")
        organize_expired_files(db)
        logger.info("Background maintenance task completed.")
    except Exception as e:
        logger.error(f"Error in background maintenance task: {e}")
    finally:
        db.close()
        MAINTENANCE_RUNNING = False


@router.post("/maintenance/background", dependencies=[Depends(deps.get_current_user)])
def trigger_maintenance(background_tasks: BackgroundTasks) -> Any:
    """
    Triggers the file maintenance task in the background.
    """
    global MAINTENANCE_RUNNING
    if MAINTENANCE_RUNNING:
        return {"status": "skipped", "message": "Maintenance already running"}

    background_tasks.add_task(run_maintenance_task)
    return {"status": "started"}


@router.get("/lock-status", dependencies=[Depends(deps.get_current_user)])
def get_lock_status() -> Any:
    """
    Returns the current lock status (Read-Only mode).
    """
    from app.core.db_security import db_security

    return {"read_only": db_security.is_read_only}


@router.post("/optimize", dependencies=[Depends(deps.get_current_active_admin)])
def optimize_system(
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_active_admin)],
) -> Any:
    """
    Triggers database optimization (VACUUM & ANALYZE) AND Mass File Synchronization.
    """
    from app.core.db_security import db_security

    try:
        # Optimization is fast enough to run sync
        db_security.optimize_database()

        # Bug 8 Fix: Run Mass File Synchronization in background
        background_tasks.add_task(run_maintenance_task)

        return {
            "message": "Ottimizzazione database completata. Sincronizzazione file avviata in background.",
            "status": "background_task_started",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {e}") from e


@router.post("/open-action")
def open_action(action_request: SystemAction) -> Any:
    """
    Endpoint used by external instances (launcher) to send commands to the running instance.
    """
    try:
        from desktop_app.ipc_bridge import IPCBridge

        bridge = IPCBridge.instance()
        bridge.emit_action(action_request.action, action_request.payload)

        return {"status": "success", "message": f"Action {action_request.action} dispatched"}
    except ImportError:
        logger.error("IPCBridge not found. Is desktop_app installed?")
        raise HTTPException(status_code=500, detail="IPC Bridge unavailable")
    except Exception as e:
        logger.error(f"Error dispatching action: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
