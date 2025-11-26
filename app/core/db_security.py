import os
import shutil
import hashlib
import base64
import time
import logging
import sqlite3
import socket
from typing import Dict, Optional, Tuple
from pathlib import Path
from cryptography.fernet import Fernet
from app.core.config import settings, get_user_data_dir
from app.core.lock_manager import LockManager
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, RetryError

logger = logging.getLogger(__name__)

class DBSecurityManager:
    """
    Manages the security of the SQLite database using strict In-Memory handling.
    - Loads encrypted DB into RAM (sqlite3 deserialize).
    - Saves RAM DB to encrypted disk file (sqlite3 serialize).
    - Enforces single-user access via Crash-Safe LockManager.
    """

    _STATIC_SECRET = "INTELLEO_DB_SECRET_KEY_V1_2024_SECURE_ACCESS"
    _HEADER = b"INTELLEO_SEC_V1"

    def __init__(self, db_name: str = "database_documenti.db"):
        # Resolve DB path using the custom path from settings if available
        custom_path_str = settings.DATABASE_PATH
        if custom_path_str and Path(custom_path_str).is_dir():
            self.data_dir = Path(custom_path_str)
        else:
            self.data_dir = get_user_data_dir()

        self.db_path = self.data_dir / db_name
        self.lock_path = self.data_dir / f".{db_name}.lock"

        # Migration: If DB exists in CWD (Install Dir) but not in Data Dir, copy it.
        # This handles the case where a DB is shipped with the installer or upgraded.
        cwd_db = Path.cwd() / db_name
        if cwd_db.exists() and not self.db_path.exists():
            try:
                shutil.copy2(cwd_db, self.db_path)
                logger.info(f"Migrated database from {cwd_db} to {self.db_path}")
            except Exception as e:
                logger.warning(f"Failed to migrate database: {e}")

        self.key = self._derive_key()
        self.fernet = Fernet(self.key)

        self.active_connection = None
        self.initial_bytes = None
        self.is_locked_mode = False # Controls encryption on save
        self.is_read_only = True    # Controls permission to save (Default: Read-Only until lock acquired)
        self.read_only_info: Optional[Dict] = None # Stores owner info if read-only

        # Initialize LockManager
        self.lock_manager = LockManager(str(self.lock_path))

    def _derive_key(self) -> bytes:
        digest = hashlib.sha256(self._STATIC_SECRET.encode()).digest()
        return base64.urlsafe_b64encode(digest)

    def acquire_session_lock(self, user_info: Dict) -> Tuple[bool, Optional[Dict]]:
        """
        Attempts to acquire the session lock using LockManager.
        If successful, this session becomes the Writer.
        If failed, this session becomes Read-Only.

        Args:
            user_info: Dict containing context about the user (e.g., username).

        Returns:
            (success, owner_info)
        """
        # Add system info to user_info
        metadata = {
            "pid": os.getpid(),
            "hostname": socket.gethostname(),
            "timestamp": time.time(),
            **user_info
        }

        success, owner_info = self.lock_manager.acquire(metadata)

        if success:
            self.is_read_only = False
            self.read_only_info = None
            logger.info("Session lock acquired. Write access enabled.")
        else:
            self.is_read_only = True
            self.read_only_info = owner_info
            logger.warning(f"Session lock failed. Read-Only mode enabled. Owner: {owner_info}")

        return success, owner_info

    def release_lock(self):
        """
        Releases the lock via LockManager.
        """
        self.lock_manager.release()
        self.is_read_only = False # Reset state, though usually app is closing.

    def load_memory_db(self):
        """
        Reads the DB from disk into memory.
        Crucially, this NO LONGER fails if the lock exists.
        It simply loads the current state of the disk file (Snapshot).
        """
        if not self.db_path.exists():
            logger.info("Database missing. Initializing new in-memory DB.")
            self.is_locked_mode = True
            self.initial_bytes = None # Will create empty in get_connection
            return

        try:
            with open(self.db_path, "rb") as f:
                content = f.read()
        except Exception as e:
            raise RuntimeError(f"Could not read database file: {e}")

        if content.startswith(self._HEADER):
            logger.info("Loading ENCRYPTED database into memory.")
            self.is_locked_mode = True
            try:
                self.initial_bytes = self.fernet.decrypt(content[len(self._HEADER):])
            except Exception as e:
                raise ValueError(f"Failed to decrypt database: {e}")
        else:
            logger.info("Loading PLAIN database into memory. Security upgrade enforced.")
            self.is_locked_mode = True
            self.initial_bytes = content

    def get_connection(self):
        """
        Factory for SQLAlchemy to create the connection.
        Deserializes the initial bytes into the new connection's memory.
        """
        if self.active_connection is None:
            # Create fresh memory connection
            conn = sqlite3.connect(':memory:', check_same_thread=False)

            if self.initial_bytes:
                try:
                    conn.deserialize(self.initial_bytes)
                except AttributeError:
                    raise RuntimeError("Your Python/SQLite version does not support 'deserialize'. Upgrade required.")
                except Exception as e:
                    raise RuntimeError(f"Failed to deserialize database: {e}")

            self.active_connection = conn

        return self.active_connection

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2), retry=retry_if_exception_type(PermissionError))
    def _safe_write(self, data: bytes):
        swp_path = self.db_path.with_suffix(".swp")
        with open(swp_path, "wb") as f:
            f.write(data)

        if os.name == 'nt' and self.db_path.exists():
            try:
                os.replace(swp_path, self.db_path)
            except PermissionError:
                raise
        else:
            os.replace(swp_path, self.db_path)

    def save_to_disk(self) -> bool:
        """
        Serializes the memory DB, Encrypts it, and writes to disk.
        CRITICAL: Only executes if this session holds the lock (is NOT Read-Only).
        """
        if not self.active_connection:
            return True

        if self.is_read_only:
            logger.warning("Attempted to save in READ-ONLY mode. Operation ignored.")
            return False

        try:
            try:
                serialized = self.active_connection.serialize()
            except AttributeError:
                logger.error("SQLite serialize not supported.")
                return False

            if self.is_locked_mode:
                final_data = self._HEADER + self.fernet.encrypt(serialized)
            else:
                final_data = serialized

            self._safe_write(final_data)
            logger.info("Database state saved to disk.")
            return True
        except Exception as e:
            logger.error(f"Failed to save database: {e}")
            return False

    def cleanup(self):
        """
        Shutdown handler. Saves state (if writer) and releases lock.
        """
        self.save_to_disk()
        self.release_lock()

    def toggle_security_mode(self, enable_encryption: bool):
        self.is_locked_mode = enable_encryption
        self.save_to_disk()

    # Alias for backward compatibility if needed, or just for main.py
    def sync_db(self):
        return self.save_to_disk()

    # Deprecated/Legacy method to satisfy old tests if any call it directly
    # Can be removed if we update all callsites.
    def create_lock(self):
        # Fallback implementation
        self.acquire_session_lock({"user": "system"})

    def check_lock_exists(self) -> bool:
        # Legacy compatibility
        return os.path.exists(self.lock_path)

    @property
    def has_lock(self) -> bool:
        # Compatibility property
        return not self.is_read_only and self.lock_manager._is_locked

# Singleton
db_security = DBSecurityManager()
