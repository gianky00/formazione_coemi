import os
import shutil
import hashlib
import base64
import time
import logging
import ctypes
import sqlite3
from pathlib import Path
from cryptography.fernet import Fernet
from app.core.config import settings
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, RetryError

logger = logging.getLogger(__name__)

class DBSecurityManager:
    """
    Manages the security of the SQLite database using strict In-Memory handling.
    - Loads encrypted DB into RAM (sqlite3 deserialize).
    - Saves RAM DB to encrypted disk file (sqlite3 serialize).
    - Enforces single-user access via Lock File (created at Login).
    """

    _STATIC_SECRET = "INTELLEO_DB_SECRET_KEY_V1_2024_SECURE_ACCESS"
    _HEADER = b"INTELLEO_SEC_V1"

    def __init__(self, db_path: str = "database_documenti.db"):
        self.db_path = Path(db_path).resolve()
        self.lock_path = self.db_path.with_name(f".{self.db_path.name}.lock")

        self.key = self._derive_key()
        self.fernet = Fernet(self.key)

        self.active_connection = None
        self.initial_bytes = None
        self.is_locked_mode = False
        self.has_lock = False # Tracks if this session owns the lock

    def _derive_key(self) -> bytes:
        digest = hashlib.sha256(self._STATIC_SECRET.encode()).digest()
        return base64.urlsafe_b64encode(digest)

    def check_lock_exists(self) -> bool:
        return self.lock_path.exists()

    def create_lock(self):
        """
        Attempts to create the lock file. Raises PermissionError if already locked.
        Should be called upon successful login.
        """
        if self.check_lock_exists():
             raise PermissionError("Database is currently locked by another active session.")

        try:
            # Use 'x' mode for atomic exclusive creation
            with open(self.lock_path, "x") as f:
                f.write(f"LOCKED_BY_PID_{os.getpid()}_{time.time()}")
            self.has_lock = True
            logger.info("Session lock acquired.")
        except FileExistsError:
             raise PermissionError("Database was locked by another session just now.")

    def remove_lock(self):
        """
        Releases the lock if held by this session.
        """
        if self.has_lock:
            if self.lock_path.exists():
                try:
                    os.remove(self.lock_path)
                    logger.info("Session lock released.")
                except Exception as e:
                    logger.warning(f"Could not remove lock file: {e}")
            self.has_lock = False

    def load_memory_db(self):
        """
        Reads the DB from disk into memory.
        - If Locked: Raises PermissionError (Stop Startup).
        - If Missing: Initializes empty.
        - If Encrypted: Decrypts.
        - If Plain: Loads Plain (and marks for encryption).
        """
        if self.check_lock_exists():
             raise PermissionError("Database is locked. Cannot start application.")

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
        CRITICAL: Only executes if this session holds the lock.
        """
        if not self.active_connection:
            return True

        if not self.has_lock:
            # We are in Read-Only / Pre-Login mode. Do not overwrite disk.
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
        Shutdown handler. Saves state and releases lock.
        """
        self.save_to_disk()
        self.remove_lock()

    def toggle_security_mode(self, enable_encryption: bool):
        self.is_locked_mode = enable_encryption
        self.save_to_disk()

    # Alias for backward compatibility if needed, or just for main.py
    def sync_db(self):
        return self.save_to_disk()

# Singleton
db_security = DBSecurityManager()
