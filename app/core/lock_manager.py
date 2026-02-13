import json
import logging
import os
import time
from typing import Any, BinaryIO

logger = logging.getLogger(__name__)


class LockManager:
    """
    Cross-platform Crash-Safe File Locking.
    Uses OS-level locking (msvcrt on Windows, fcntl on Unix) to ensure
    automatic lock release on process termination (crash/kill).
    """

    def __init__(self, lock_file_path: str):
        self.lock_file_path: str = lock_file_path
        self._lock_handle: BinaryIO | None = None
        self._is_locked: bool = False
        self.owner_info: dict[str, Any] | None = None
        self.current_metadata: dict[str, Any] | None = None

    def _init_lock_file(self) -> None:
        """Creates the directory and file if needed."""
        try:
            os.makedirs(os.path.dirname(self.lock_file_path), exist_ok=True)
            if not os.path.exists(self.lock_file_path):
                with open(self.lock_file_path, "wb") as f:
                    f.write(b"\0")
        except Exception as e:
            logger.error(f"Failed to initialize lock file: {e}")

    def _attempt_lock(self, owner_metadata: dict[str, Any]) -> tuple[bool, Exception | None]:
        """Tries to open and lock the file."""
        try:
            # Open for reading/writing in binary mode
            handle = open(self.lock_file_path, "r+b")
            self._lock_handle = handle
            self._lock_byte_0()
            self._is_locked = True
            self.current_metadata = owner_metadata
            self._write_metadata(owner_metadata)
            logger.info(f"Lock acquired on {self.lock_file_path}")
            return True, None
        except (OSError, BlockingIOError, PermissionError):
            # Not an error in logic, just couldn't lock
            if self._lock_handle:
                self._cleanup_handle()
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error acquiring lock: {e}")
            if self._lock_handle:
                self._cleanup_handle()
            return False, e

    def _handle_lock_failure(self) -> tuple[bool, dict[str, Any]]:
        """Reads metadata from the locked file if possible."""
        logger.info("Database is locked by another process.")
        self._is_locked = False
        owner_data: dict[str, Any] = {"error": "Unknown (Could not read lock file)"}

        # Read metadata BEFORE cleaning up the handle
        try:
            if self._lock_handle and not self._lock_handle.closed:
                owner_data = self._read_metadata()
            else:
                # Handle was already closed or never opened, try to read directly
                owner_data = self._read_metadata_from_file()
        except Exception as e:
            logger.error(f"Failed to read lock metadata: {e}")
        finally:
            self._cleanup_handle()
        return False, owner_data

    def _read_metadata_from_file(self) -> dict[str, Any]:
        """
        Reads metadata directly from the lock file without holding a lock.
        Used as fallback when handle is not available.
        """
        try:
            with open(self.lock_file_path, "rb") as f:
                f.seek(1)
                content = f.read()
                if not content:
                    return {"status": "Locked but empty metadata"}
                return dict(json.loads(content.decode("utf-8")))
        except json.JSONDecodeError:
            return {"status": "Locked (Corrupt Metadata)"}
        except FileNotFoundError:
            return {"status": "Lock file not found"}
        except Exception as e:
            logger.warning(f"Error reading metadata from file: {e}")
            return {"status": f"Locked (Read Error: {e})"}

    def acquire(
        self, owner_metadata: dict[str, Any], retries: int = 3, delay: float = 0.5
    ) -> tuple[bool, dict[str, Any] | None]:
        """Attempts to acquire the lock with retries."""
        for attempt in range(retries + 1):
            self._init_lock_file()

            success, error = self._attempt_lock(owner_metadata)
            if success:
                return True, None

            # If error was not just "locked", handle it
            if error:
                self._cleanup_handle()
                return False, {"error": f"Error: {error}"}

            # Lock held by other process
            if attempt < retries:
                logger.warning(
                    f"Lock acquisition failed (Attempt {attempt + 1}/{retries + 1}). Retrying in {delay}s..."
                )
                self._cleanup_handle()
                time.sleep(delay)
                continue

            # Final attempt failed - handle the lock failure
            return self._handle_lock_failure()

        return False, {"error": "Retries exhausted"}

    def _cleanup_handle(self) -> None:
        """Helper to safely close and clear the lock handle."""
        if self._lock_handle:
            try:
                self._lock_handle.close()
            except Exception as e:
                logger.error(f"Error closing lock handle during cleanup: {e}")
            finally:
                self._lock_handle = None

    def _verify_identity(self, current_on_disk: Any) -> bool:
        """Verifies if the lock on disk matches our current session."""
        if not self.current_metadata:
            return False

        if not isinstance(current_on_disk, dict) or "uuid" not in current_on_disk:
            if isinstance(current_on_disk, dict) and "pid" in current_on_disk:
                # Check Legacy Identity (PID + Host)
                if current_on_disk.get("pid") != self.current_metadata.get(
                    "pid"
                ) or current_on_disk.get("hostname") != self.current_metadata.get("hostname"):
                    logger.critical("SPLIT BRAIN DETECTED (Legacy Check): Identity mismatch.")
                    return False
            else:
                logger.error(
                    f"Heartbeat Verification Failed: Could not read valid metadata. content: {current_on_disk}"
                )
                return False
        else:
            # Strong Verification (UUID)
            if current_on_disk.get("uuid") != self.current_metadata.get("uuid"):
                logger.critical(
                    f"SPLIT BRAIN DETECTED: UUID mismatch. Owner: {current_on_disk.get('uuid')}. Me: {self.current_metadata.get('uuid')}."
                )
                return False
        return True

    def update_heartbeat(self) -> bool:
        """Updates the timestamp in the lock file to signal the process is alive."""
        if not self._is_locked or not self.current_metadata:
            return False

        try:
            current_on_disk = self._read_metadata()

            if not self._verify_identity(current_on_disk):
                return False

            self.current_metadata["timestamp"] = time.time()
            self._write_metadata(self.current_metadata)
            return True
        except Exception as e:
            logger.error(f"Heartbeat failed (Exception): {e}")
            return False

    def release(self) -> None:
        """Explicitly releases the lock by closing the file handle."""
        if self._lock_handle:
            try:
                self._lock_handle.close()
            except Exception as e:
                logger.error(f"Error closing lock handle: {e}")
            finally:
                self._lock_handle = None
                self._is_locked = False
                self.current_metadata = None

                # Attempt to remove the file
                try:
                    if os.path.exists(self.lock_file_path):
                        os.remove(self.lock_file_path)
                        logger.info("Lock file removed.")
                except Exception as e:
                    logger.debug(
                        f"Could not remove lock file (likely taken by another process): {e}"
                    )

    def __del__(self) -> None:
        """Destructor to ensure handle is closed."""
        self.release()

    def _lock_byte_0(self) -> None:
        """Platform-specific locking of the first byte."""
        if not self._lock_handle:
            return

        if os.name == "nt":
            import msvcrt

            self._lock_handle.seek(0)
            # msvcrt.locking(fd, mode, nbytes)
            msvcrt.locking(self._lock_handle.fileno(), 2, 1)  # 2 = LK_NBLCK
        else:
            import fcntl

            # fcntl.flock(fd, operation)
            # LOCK_EX = 2, LOCK_NB = 4. 2|4 = 6
            fcntl.flock(self._lock_handle.fileno(), 6)

    def _write_metadata(self, metadata: dict[str, Any]) -> None:
        """Writes metadata starting at byte 1."""
        if not self._lock_handle:
            return
        try:
            self._lock_handle.seek(0)
            self._lock_handle.write(b"\0")

            json_bytes = json.dumps(metadata).encode("utf-8")
            self._lock_handle.seek(1)
            self._lock_handle.write(json_bytes)
            self._lock_handle.truncate()
            self._lock_handle.flush()
        except Exception as e:
            logger.error(f"Failed to write metadata: {e}")
            raise

    def _read_metadata(self) -> dict[str, Any]:
        """Reads metadata from byte 1 onwards."""
        if not self._lock_handle:
            return {"status": "Error: No handle"}
        try:
            self._lock_handle.seek(1)
            content = self._lock_handle.read()
            if not content:
                return {"status": "Locked but empty metadata"}
            return dict(json.loads(content.decode("utf-8")))
        except json.JSONDecodeError:
            return {"status": "Locked (Corrupt Metadata)"}
        except Exception as e:
            logger.warning(f"Error reading metadata: {e}")
            return {"status": "Locked (Read Error)"}
