import os
import sys
import json
import time
import logging
import socket
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)

class LockManager:
    """
    Cross-platform Crash-Safe File Locking.
    Uses OS-level locking (msvcrt on Windows, fcntl on Unix) to ensure
    automatic lock release on process termination (crash/kill).
    """

    def __init__(self, lock_file_path: str):
        self.lock_file_path = lock_file_path
        self._lock_handle = None
        self._is_locked = False
        self.owner_info: Optional[Dict] = None
        self.current_metadata: Optional[Dict] = None

    def _init_lock_file(self):
        """Creates the directory and file if needed."""
        try:
            os.makedirs(os.path.dirname(self.lock_file_path), exist_ok=True)
            if not os.path.exists(self.lock_file_path):
                with open(self.lock_file_path, 'wb') as f:
                    f.write(b'\0')
        except Exception as e:
            logger.error(f"Failed to initialize lock file: {e}")

    def _attempt_lock(self, owner_metadata):
        """Tries to open and lock the file."""
        try:
            self._lock_handle = open(self.lock_file_path, 'r+b')
            self._lock_byte_0()
            self._is_locked = True
            self.current_metadata = owner_metadata
            self._write_metadata(owner_metadata)
            logger.info(f"Lock acquired on {self.lock_file_path}")
            return True, None
        except (IOError, BlockingIOError, PermissionError):
            # Not an error in logic, just couldn't lock
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error acquiring lock: {e}")
            return False, e

    def _handle_lock_failure(self):
        """Reads metadata from the locked file if possible."""
        logger.info("Database is locked by another process.")
        self._is_locked = False
        owner_data = {"error": "Unknown (Could not read lock file)"}
        try:
            if self._lock_handle:
                owner_data = self._read_metadata()
        except Exception as e:
            logger.error(f"Failed to read lock metadata: {e}")
        finally:
             self._cleanup_handle()
        return False, owner_data

    def acquire(self, owner_metadata: Dict, retries: int = 3, delay: float = 0.5) -> Tuple[bool, Optional[Dict]]:
        # S3776: Refactored to reduce complexity
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
                logger.warning(f"Lock acquisition failed (Attempt {attempt+1}/{retries+1}). Retrying in {delay}s...")
                self._cleanup_handle()
                time.sleep(delay)
                continue

            return self._handle_lock_failure()

        return False, {"error": "Retries exhausted"}

    def _cleanup_handle(self):
        """Helper to safely close and clear the lock handle."""
        if self._lock_handle:
            try:
                self._lock_handle.close()
            except Exception as e:
                logger.error(f"Error closing lock handle during cleanup: {e}")
            finally:
                self._lock_handle = None

    def _verify_identity(self, current_on_disk):
        """Verifies if the lock on disk matches our current session."""
        if not isinstance(current_on_disk, dict) or "uuid" not in current_on_disk:
            if isinstance(current_on_disk, dict) and "pid" in current_on_disk:
                 # Check Legacy Identity (PID + Host)
                 if current_on_disk.get("pid") != self.current_metadata.get("pid") or \
                    current_on_disk.get("hostname") != self.current_metadata.get("hostname"):
                     logger.critical("SPLIT BRAIN DETECTED (Legacy Check): Identity mismatch.")
                     return False
            else:
                logger.error(f"Heartbeat Verification Failed: Could not read valid metadata. content: {current_on_disk}")
                return False
        else:
            # Strong Verification (UUID)
            if current_on_disk.get("uuid") != self.current_metadata.get("uuid"):
                 logger.critical(f"SPLIT BRAIN DETECTED: UUID mismatch. Owner: {current_on_disk.get('uuid')}. Me: {self.current_metadata.get('uuid')}.")
                 return False
        return True

    def update_heartbeat(self) -> bool:
        # S3776: Refactored to reduce complexity
        if not self._is_locked or not self.current_metadata:
            return False

        try:
            current_on_disk = self._read_metadata()

            if not self._verify_identity(current_on_disk):
                return False

            self.current_metadata['timestamp'] = time.time()
            self._write_metadata(self.current_metadata)
            return True
        except Exception as e:
            logger.error(f"Heartbeat failed (Exception): {e}")
            return False

    def release(self):
        """
        Explicitly releases the lock by closing the file handle.
        """
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
                    logger.debug(f"Could not remove lock file (likely taken by another process): {e}")

    def __del__(self):
        """Destructor to ensure handle is closed."""
        self.release()

    def _lock_byte_0(self):
        """
        Platform-specific locking of the first byte.
        """
        if os.name == 'nt':
            import msvcrt
            self._lock_handle.seek(0)
            msvcrt.locking(self._lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(self._lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _write_metadata(self, metadata: Dict):
        """
        Writes metadata starting at byte 1.
        """
        try:
            self._lock_handle.seek(0)
            self._lock_handle.write(b'\0')

            json_bytes = json.dumps(metadata).encode('utf-8')
            self._lock_handle.seek(1)
            self._lock_handle.write(json_bytes)
            self._lock_handle.truncate()
            self._lock_handle.flush()
        except Exception as e:
            logger.error(f"Failed to write metadata: {e}")
            raise

    def _read_metadata(self) -> Dict:
        """
        Reads metadata from byte 1 onwards.
        """
        try:
            self._lock_handle.seek(1)
            content = self._lock_handle.read()
            if not content:
                return {"status": "Locked but empty metadata"}
            return json.loads(content.decode('utf-8'))
        except json.JSONDecodeError:
            return {"status": "Locked (Corrupt Metadata)"}
        except Exception as e:
            logger.warning(f"Error reading metadata: {e}")
            return {"status": "Locked (Read Error)"}
