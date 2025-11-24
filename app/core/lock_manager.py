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

    def acquire(self, owner_metadata: Dict) -> Tuple[bool, Optional[Dict]]:
        """
        Attempts to acquire an exclusive lock on the file.

        Args:
            owner_metadata: Dict containing info about the current process (pid, user, etc.)

        Returns:
            (success, current_owner_info)
            - If success is True: We are the writer. current_owner_info is None (or ours).
            - If success is False: We are a reader. current_owner_info contains the lock holder's data.
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.lock_file_path), exist_ok=True)

            # Open file in Read/Write mode. Create if not exists.
            # We use 'r+b' if exists, 'w+b' if not.
            if not os.path.exists(self.lock_file_path):
                with open(self.lock_file_path, 'wb') as f:
                    f.write(b'\0') # Initialize with at least one byte

            self._lock_handle = open(self.lock_file_path, 'r+b')

            # Try to lock the first byte
            self._lock_byte_0()

            # If we reached here, we have the lock!
            self._is_locked = True

            # Write our metadata
            self._write_metadata(owner_metadata)

            logger.info(f"Lock acquired on {self.lock_file_path}")
            return True, None

        except (IOError, BlockingIOError, PermissionError):
            # Lock is held by someone else
            logger.info("Database is locked by another process.")
            self._is_locked = False

            # Close our handle since we failed to lock (we'll re-open properly if needed or just use this one to read)
            # Actually, we need to read the metadata.
            try:
                if self._lock_handle:
                    owner_data = self._read_metadata()
                    self._lock_handle.close()
                    self._lock_handle = None
                    return False, owner_data
            except Exception as e:
                logger.error(f"Failed to read lock metadata: {e}")
                if self._lock_handle:
                    self._lock_handle.close()
                    self._lock_handle = None
                return False, {"error": "Unknown (Could not read lock file)"}

        except Exception as e:
            logger.error(f"Unexpected error acquiring lock: {e}")
            if self._lock_handle:
                self._lock_handle.close()
                self._lock_handle = None
            return False, {"error": f"Error: {e}"}

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
                logger.info("Lock released.")

    def _lock_byte_0(self):
        """
        Platform-specific locking of the first byte.
        Raises exception if locked.
        """
        if os.name == 'nt':
            import msvcrt
            # Lock 1 byte at offset 0. LK_NBLCK throws IOError if locked.
            self._lock_handle.seek(0)
            msvcrt.locking(self._lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            # Exclusive non-blocking lock
            fcntl.flock(self._lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _write_metadata(self, metadata: Dict):
        """
        Writes metadata starting at byte 1.
        """
        try:
            # Ensure Byte 0 is null/sentinel
            self._lock_handle.seek(0)
            self._lock_handle.write(b'\0')

            # Write JSON at Byte 1
            json_bytes = json.dumps(metadata).encode('utf-8')
            self._lock_handle.seek(1)
            self._lock_handle.write(json_bytes)
            self._lock_handle.truncate() # Remove any old trailing data
            self._lock_handle.flush()
            # Note: Do NOT close handle!
        except Exception as e:
            logger.error(f"Failed to write metadata: {e}")

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
