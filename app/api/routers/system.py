from fastapi import APIRouter, HTTPException
from app.schemas.system import SystemAction
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

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
