from PyQt6.QtCore import QObject, pyqtSignal

class IPCBridge(QObject):
    """
    Singleton class to bridge backend IPC (FastAPI) actions to the Frontend (Qt).
    Uses Qt Signals to ensure thread-safe communication.
    """
    _instance = None

    # Signal arguments: action (str), payload (dict)
    action_received = pyqtSignal(str, dict)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = IPCBridge()
        return cls._instance

    def emit_action(self, action: str, payload: dict):
        # print(f"[IPC] Emitting action: {action} with payload: {payload}")
        self.action_received.emit(action, payload)
