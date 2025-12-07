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

    def acquire(self, owner_metadata: Dict, retries: int = 3, delay: float = 0.5) -> Tuple[bool, Optional[Dict]]:
        """
        Attempts to acquire an exclusive lock on the file with retry logic.
        """
        for attempt in range(retries + 1):
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(self.lock_file_path), exist_ok=True)

                # Open file in Read/Write mode. Create if not exists.
                # We use 'r+b' if exists, 'w+b' if not.
                if not os.path.exists(self.lock_file_path):
                    with open(self.lock_file_path, 'wb') as f:
                        f.write(b'\0') # Initialize with at least one byte

                # Use explicit open() call, managed via try...finally for closure in error cases
                self._lock_handle = open(self.lock_file_path, 'r+b')

                # Try to lock the first byte
                self._lock_byte_0()

                # If we reached here, we have the lock!
                self._is_locked = True
                self.current_metadata = owner_metadata

                # Write our metadata
                self._write_metadata(owner_metadata)

                logger.info(f"Lock acquired on {self.lock_file_path}")
                return True, None

            except (IOError, BlockingIOError, PermissionError):
                # Lock is held by someone else, or file access error (network)
                if attempt < retries:
                    logger.warning(f"Lock acquisition failed (Attempt {attempt+1}/{retries+1}). Retrying in {delay}s...")
                    self._cleanup_handle()
                    time.sleep(delay)
                    continue

                # If retries exhausted:
                logger.info("Database is locked by another process.")
                self._is_locked = False

                # Read metadata to return to caller
                owner_data = {"error": "Unknown (Could not read lock file)"}
                try:
                    if self._lock_handle:
                        # Attempt to read metadata from the handle we failed to lock (since we opened it)
                        # NOTE: Reading from a file locked by another process might fail on Windows if opened exclusively.
                        # However, we opened with 'r+b'. Locking happens on Byte 0.
                        # Reading Byte 1+ might succeed if locking is advisory or partial.
                        # If locking is mandatory/exclusive on whole file, open() itself would have failed.
                        # If we passed open() but failed locking(), we have a handle.
                        owner_data = self._read_metadata()
                except Exception as e:
                    logger.error(f"Failed to read lock metadata: {e}")
                finally:
                     self._cleanup_handle()

                return False, owner_data

            except Exception as e:
                logger.error(f"Unexpected error acquiring lock: {e}")
                self._cleanup_handle()
                return False, {"error": f"Error: {e}"}

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

    def update_heartbeat(self) -> bool:
        """
        Updates the timestamp in the lock file to prove we are still alive.
        """
        if not self._is_locked or not self.current_metadata:
            return False

        try:
            # 1. Read existing metadata to verify identity
            current_on_disk = self._read_metadata()

            # 2. Strict Verification
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

            # 3. Update timestamp and write
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
