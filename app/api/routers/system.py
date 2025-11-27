from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from app.schemas.system import SystemAction
from app.db.session import SessionLocal
from app.services.file_maintenance import organize_expired_files
from app.api import deps
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Global flag to prevent concurrent maintenance tasks
MAINTENANCE_RUNNING = False

def run_maintenance_task():
    """
    Wrapper to run maintenance in a separate thread/session.
    """
    global MAINTENANCE_RUNNING
    if MAINTENANCE_RUNNING:
        logger.info("Maintenance task already running. Skipping.")
        return

    MAINTENANCE_RUNNING = True
    try:
        db = SessionLocal()
        logger.info("Starting background maintenance task...")
        organize_expired_files(db)
        logger.info("Background maintenance task completed.")
    except Exception as e:
        logger.error(f"Error in background maintenance task: {e}")
    finally:
        db.close()
        MAINTENANCE_RUNNING = False

@router.post("/maintenance/background", dependencies=[Depends(deps.get_current_user)])
def trigger_maintenance(background_tasks: BackgroundTasks):
    """
    Triggers the file maintenance task in the background.
    """
    global MAINTENANCE_RUNNING
    if MAINTENANCE_RUNNING:
        return {"status": "skipped", "message": "Maintenance already running"}

    background_tasks.add_task(run_maintenance_task)
    return {"status": "started"}

@router.get("/lock-status", dependencies=[Depends(deps.get_current_user)])
def get_lock_status():
    """
    Returns the current lock status (Read-Only mode).
    Used by the frontend to detect split-brain or network lock loss.
    """
    from app.core.db_security import db_security
    return {"read_only": db_security.is_read_only}

@router.post("/open-action")
def open_action(action_request: SystemAction):
    """
    Endpoint used by external instances (launcher) to send commands to the running instance.
    """
    try:
        # Import inside the function to avoid strict startup dependency if desktop_app is missing (unlikely)
        # and to avoid circular import issues at module level if any.
        from desktop_app.ipc_bridge import IPCBridge

        bridge = IPCBridge.instance()
        bridge.emit_action(action_request.action, action_request.payload)

        return {"status": "success", "message": f"Action {action_request.action} dispatched"}
    except ImportError:
        logger.error("IPCBridge not found. Is desktop_app installed?")
        raise HTTPException(status_code=500, detail="IPC Bridge unavailable")
    except Exception as e:
        logger.error(f"Error dispatching action: {e}")
        raise HTTPException(status_code=500, detail=str(e))
