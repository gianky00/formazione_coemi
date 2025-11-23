import os
import shutil
import hashlib
import base64
import time
import logging
import ctypes
from pathlib import Path
from cryptography.fernet import Fernet
from app.core.config import settings
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, RetryError

logger = logging.getLogger(__name__)

class DBSecurityManager:
    """
    Manages the security of the SQLite database.
    - Handles Encryption/Decryption using a static key derived from the application secret.
    - Manages a temporary "working copy" of the database to ensure the main file remains protected at rest.
    - Implements a file lock to enforce single-user access.
    """

    # Static secret to ensure all authorized installations can access the DB
    _STATIC_SECRET = "INTELLEO_DB_SECRET_KEY_V1_2024_SECURE_ACCESS"

    # Custom Header to identify encrypted files
    _HEADER = b"INTELLEO_SEC_V1"

    def __init__(self, db_path: str = "database_documenti.db"):
        self.db_path = Path(db_path).resolve()

        # Use User Home for Temp File to isolate it
        # Hidden folder in user's home directory
        self.home_dir = Path.home() / ".intelleo_data"
        self.home_dir.mkdir(parents=True, exist_ok=True)

        # Hide the directory on Windows
        if os.name == 'nt':
            try:
                # FILE_ATTRIBUTE_HIDDEN = 2
                ctypes.windll.kernel32.SetFileAttributesW(str(self.home_dir), 2)
            except Exception:
                pass

        self.temp_path = self.home_dir / f"temp_{self.db_path.name}"

        # Lock file stays with the MAIN DB to ensure visibility for other instances accessing the same DB
        self.lock_path = self.db_path.with_name(f".{self.db_path.name}.lock")

        self.key = self._derive_key()
        self.fernet = Fernet(self.key)
        self.is_locked_mode = False # Tracks if we are operating in Encrypted mode

    def _derive_key(self) -> bytes:
        """Derives a 32-byte URL-safe base64 key from the static secret."""
        digest = hashlib.sha256(self._STATIC_SECRET.encode()).digest()
        return base64.urlsafe_b64encode(digest)

    def is_encrypted(self) -> bool:
        """Checks if the database file is encrypted by inspecting the header."""
        if not self.db_path.exists():
            return False
        try:
            with open(self.db_path, "rb") as f:
                header = f.read(len(self._HEADER))
                return header == self._HEADER
        except Exception:
            return False

    def check_lock(self):
        """
        Checks if the database is locked by another process.
        Raises PermissionError if locked.
        Creates the lock if free.
        """
        if self.lock_path.exists():
            # Check if stale? (Simple version: Assume valid if exists)
            # In a robust system, we'd check the PID inside.
            # For now, strictly enforce single user.
            raise PermissionError(
                f"Il database è bloccato da un'altra istanza. "
                f"Rimuovi il file {self.lock_path.name} se sei sicuro che nessun altro lo stia usando."
            )

        # Create Lock
        with open(self.lock_path, "w") as f:
            f.write(f"LOCKED_BY_PID_{os.getpid()}_{time.time()}")

    def initialize_db(self) -> str:
        """
        Prepares the database for use.
        - Checks Lock.
        - Determines if Encrypted or Plain.
        - If Encrypted: Decrypts to Temp. Returns Temp Path.
        - If Plain: Returns Main Path (or copies to Temp if we want to standardize sync logic).
        """
        self.check_lock()

        # Safety check: If temp file exists, back it up before overwriting
        if self.temp_path.exists():
            try:
                backup_path = self.temp_path.with_suffix(f".bak_{int(time.time())}")
                shutil.move(self.temp_path, backup_path)
                logger.warning(f"Found existing temp DB. Backed up to {backup_path}")
            except Exception as e:
                logger.warning(f"Could not backup existing temp DB: {e}")

        if self.is_encrypted():
            logger.info("Database is ENCRYPTED. Decrypting to temporary workspace.")
            self.is_locked_mode = True
            self._decrypt_to_temp()
        elif self.db_path.exists():
            logger.info("Database is PLAIN. Copying to temporary workspace.")
            shutil.copy2(self.db_path, self.temp_path)

            # AUTO-LOCK: Enforce encryption for the next sync
            # This satisfies the requirement "SEMPRE crittografato"
            logger.info("Enforcing encryption for future syncs.")
            self.is_locked_mode = True
        else:
            # New DB scenario
            logger.info("Database not found. A new one will be created in temporary workspace.")
            # Start encrypted by default
            self.is_locked_mode = True
            pass

        # Return the connection string for SQLAlchemy
        # Use forward slashes for cross-platform compatibility
        return f"sqlite:///{self.temp_path.as_posix()}"

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2), retry=retry_if_exception_type(PermissionError))
    def _safe_replace(self, src: Path, dst: Path):
        """
        Safely replaces the destination file with source, with retries for Windows file locking.
        """
        # On Windows, os.replace might fail if dst is open or has sharing violation
        # We try to force it.
        if os.name == 'nt' and dst.exists():
            try:
                os.replace(src, dst)
            except PermissionError:
                # Wait and retry (handled by tenacity)
                raise
        else:
            os.replace(src, dst)

    def sync_db(self) -> bool:
        """
        Synchronizes the Temp DB back to the Main DB.
        - If locked mode: Encrypt Temp -> Main.
        - If plain mode: Copy Temp -> Main.
        Returns True if success, False if failed (e.g. locked).
        """
        if not self.temp_path.exists():
            return True

        # Write to a .swp file first to prevent corruption during write
        swp_path = self.db_path.with_suffix(".swp")

        try:
            if self.is_locked_mode:
                self._encrypt_from_temp(target=swp_path)
            else:
                shutil.copy2(self.temp_path, swp_path)

            # Atomic rename (on POSIX, and decent on Windows with retry)
            try:
                self._safe_replace(swp_path, self.db_path)
                logger.info("Database synchronized successfully.")
                return True
            except RetryError:
                logger.warning("Could not sync database. The file 'database_documenti.db' is likely open in another program (e.g., DB Browser). Sync will retry later.")
                return False

        except Exception as e:
            logger.error(f"Failed to sync database: {e}")
            if swp_path.exists():
                try:
                    os.remove(swp_path)
                except: pass
            # If it's not a retry error, it might be something else. We log and return False.
            return False

    def cleanup(self):
        """
        Final sync and cleanup of Temp/Lock files.
        """
        sync_success = self.sync_db()

        if sync_success:
            if self.temp_path.exists():
                try:
                    os.remove(self.temp_path)
                except Exception as e:
                    logger.warning(f"Could not delete temp db: {e}")
        else:
            logger.warning("Final sync failed (File Locked?). Temporary database PRESERVED for recovery in .intelleo_data.")

        if self.lock_path.exists():
            try:
                os.remove(self.lock_path)
            except Exception as e:
                logger.warning(f"Could not remove lock file: {e}")

    def toggle_security_mode(self, enable_encryption: bool):
        """
        Switches between Encrypted (Locked) and Plain (Unlocked) storage.
        Triggers an immediate Sync in the new mode.
        """
        self.is_locked_mode = enable_encryption
        self.sync_db()

    def _decrypt_to_temp(self):
        with open(self.db_path, "rb") as f:
            content = f.read()

        if not content.startswith(self._HEADER):
            raise ValueError("Invalid Database Header")

        encrypted_data = content[len(self._HEADER):]
        decrypted_data = self.fernet.decrypt(encrypted_data)

        with open(self.temp_path, "wb") as f:
            f.write(decrypted_data)

    def _encrypt_from_temp(self, target: Path):
        with open(self.temp_path, "rb") as f:
            data = f.read()

        encrypted_data = self.fernet.encrypt(data)

        with open(target, "wb") as f:
            f.write(self._HEADER + encrypted_data)

# Singleton Instance
db_security = DBSecurityManager()
