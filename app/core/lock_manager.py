import json
import logging
import os
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Cross-platform file locking
try:
    import fcntl
except ImportError:
    fcntl = None  # type: ignore

try:
    import msvcrt
except ImportError:
    msvcrt = None  # type: ignore


class LockManager:
    """
    Manages file-based locking with heartbeats.
    Compatible with Windows and Unix.
    """

    def __init__(self, lock_path: str):
        self.lock_path = Path(lock_path)
        self._lock_handle: Any = None

    def acquire(self, metadata: dict[str, Any]) -> tuple[bool, dict[str, Any] | None]:
        """Attempts to acquire the lock and write metadata."""
        try:
            self.lock_path.parent.mkdir(parents=True, exist_ok=True)

            # Open file
            self._lock_handle = open(self.lock_path, "wb+")

            # Apply OS-level lock (Non-blocking)
            if fcntl:
                try:
                    fcntl.flock(self._lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError:
                    return False, self._read_existing_metadata()
            elif msvcrt:
                try:
                    # On Windows, we lock the first byte
                    msvcrt.locking(self._lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
                except OSError:
                    return False, self._read_existing_metadata()

            # Successfully locked, write metadata
            metadata_json = json.dumps(metadata).encode("utf-8")
            self._lock_handle.seek(0)
            self._lock_handle.write(b"\x01")  # First byte is lock indicator
            self._lock_handle.write(metadata_json)
            self._lock_handle.truncate()
            self._lock_handle.flush()

            return True, None

        except Exception as e:
            logger.error(f"Lock acquisition error: {e}")
            self.release()
            return False, None

    def _read_existing_metadata(self) -> dict[str, Any] | None:
        """Reads metadata from an existing lock file without holding the lock."""
        try:
            if not self.lock_path.exists():
                return None
            with open(self.lock_path, "rb") as f:
                f.seek(1)
                data = f.read()
                if data:
                    return dict(json.loads(data.decode("utf-8")))
        except Exception:
            pass
        return None

    def update_heartbeat(self) -> bool:
        """Updates the timestamp in the lock metadata."""
        if not self._lock_handle:
            return False

        try:
            metadata = self._read_existing_metadata() or {}
            metadata["timestamp"] = time.time()
            metadata_json = json.dumps(metadata).encode("utf-8")

            self._lock_handle.seek(1)
            self._lock_handle.write(metadata_json)
            self._lock_handle.truncate()
            self._lock_handle.flush()
            return True
        except Exception as e:
            logger.error(f"Heartbeat update failed: {e}")
            return False

    def release(self) -> None:
        """Releases the lock and closes the file."""
        if self._lock_handle:
            try:
                if fcntl:
                    fcntl.flock(self._lock_handle.fileno(), fcntl.LOCK_UN)
                elif msvcrt:
                    self._lock_handle.seek(0)
                    msvcrt.locking(self._lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
                self._lock_handle.close()
            except Exception:
                pass
            self._lock_handle = None

        if self.lock_path.exists():
            try:
                os.remove(self.lock_path)
            except Exception:
                pass
