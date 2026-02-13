import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class IPCBridge:
    """
    Singleton class to handle communication between the API server and the Desktop UI.
    This replaces the obfuscated version to ensure project maintainability.
    """

    _instance = None

    def __init__(self):
        if IPCBridge._instance is not None:
            raise Exception("This class is a singleton!")
        self._callbacks: dict[str, list[Callable]] = {}
        IPCBridge._instance = self

    @classmethod
    def instance(cls) -> "IPCBridge":
        """Returns the singleton instance."""
        if cls._instance is None:
            cls._instance = IPCBridge()
        return cls._instance

    def subscribe(self, action: str, callback: Callable):
        """Subscribe to a specific action."""
        if action not in self._callbacks:
            self._callbacks[action] = []
        self._callbacks[action].append(callback)
        logger.debug(f"Subscribed to action: {action}")

    def emit_action(self, action: str, payload: Any = None):
        """Emits an action to all subscribers."""
        logger.info(f"Emitting action: {action} with payload: {payload}")
        if action in self._callbacks:
            for callback in self._callbacks[action]:
                try:
                    callback(payload)
                except Exception as e:
                    logger.error(f"Error executing callback for {action}: {e}")
        else:
            logger.warning(f"No subscribers for action: {action}")
