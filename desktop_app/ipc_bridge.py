import logging
from collections.abc import Callable
from typing import Any, Optional

logger = logging.getLogger(__name__)


class IPCBridge:
    """
    Standard bridge for Inter-Process Communication between FastAPI and Desktop UI.
    Uses a simple callback subscription model.
    """

    _instance: Optional["IPCBridge"] = None

    def __init__(self) -> None:
        # Action -> list of callbacks
        self._callbacks: dict[str, list[Callable[[Any], Any]]] = {}

    @classmethod
    def instance(cls) -> "IPCBridge":
        if cls._instance is None:
            cls._instance = IPCBridge()
        return cls._instance

    def subscribe(self, action: str, callback: Callable[[Any], Any]) -> None:
        """Subscribes a UI view/model to an API action."""
        if action not in self._callbacks:
            self._callbacks[action] = []
        self._callbacks[action].append(callback)
        logger.debug(f"Subscribed to action: {action}")

    def emit_action(self, action: str, payload: Any = None) -> None:
        """Dispatches an action to all subscribers."""
        if action in self._callbacks:
            logger.info(f"Emitting action: {action}")
            for callback in self._callbacks[action]:
                try:
                    callback(payload)
                except Exception as e:
                    logger.error(f"Error in IPC callback for {action}: {e}")
        else:
            logger.debug(f"No subscribers for action: {action}")
