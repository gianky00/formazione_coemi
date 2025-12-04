import os
import shutil
import hashlib
import base64
import time
import logging
import sqlite3
import socket
import threading
import uuid
import psutil
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
        if custom_path_str:
            path_obj = Path(custom_path_str)
            if path_obj.is_dir():
                self.data_dir = path_obj
                self.db_path = self.data_dir / db_name
            elif path_obj.suffix.lower() == ".db":
                # User selected the file directly
                self.db_path = path_obj
                self.data_dir = path_obj.parent
            else:
                # Fallback if configured path is invalid or weird
                self.data_dir = get_user_data_dir()
                self.db_path = self.data_dir / db_name
        else:
            self.data_dir = get_user_data_dir()
            self.db_path = self.data_dir / db_name
        self.lock_path = self.data_dir / f".{db_name}.lock"

        # RECOVERY: Check for Stale Locks (Zombie Processes)
        self._check_and_recover_stale_lock()

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
        self._heartbeat_timer: Optional[threading.Timer] = None
        self._autosave_timer: Optional[threading.Timer] = None

    def _derive_key(self) -> bytes:
        digest = hashlib.sha256(self._STATIC_SECRET.encode()).digest()
        return base64.urlsafe_b64encode(digest)

    def _check_and_recover_stale_lock(self):
        """
        Detects if a lock file exists but belongs to a dead process.
        Strictly checks if PID exists. If dead, deletes lock immediately.
        """
        if not self.lock_path.exists():
            return

        should_remove = False
        reason = ""

        try:
            # We use LockManager to safely read metadata without locking
            # (temp_mgr removed as it was unused)

            with open(self.lock_path, 'rb') as f:
                # Byte 0 is lock byte, Byte 1+ is JSON
                f.seek(1)
                data = f.read()
                if not data: return # Empty file

                import json
                try:
                    metadata = json.loads(data.decode('utf-8'))
                except:
                    # Corrupt JSON -> Force Clean
                    should_remove = True
                    reason = "Corrupt lock file found"
                else:
                    if not should_remove:
                        pid = metadata.get("pid")
                        if not pid:
                            return # No PID to check

                        # CHECK PID EXISTENCE - HARDENED LOGIC
                        # If psutil says PID is gone, we delete the lock. Period.
                        if not psutil.pid_exists(pid):
                            should_remove = True
                            reason = f"PID {pid} is DEAD"
                        else:
                            # PID exists, but is it US or Python/Intelleo?
                            try:
                                proc = psutil.Process(pid)
                                name = proc.name().lower()
                                # If process is definitely NOT related to us (e.g. Chrome, System), kill lock
                                valid_names = ["python", "intelleo", "main", "launcher", "boot_loader"]
                                is_valid = any(v in name for v in valid_names)

                                if not is_valid:
                                    should_remove = True
                                    reason = f"PID {pid} exists ({name}) but is unrelated"
                                else:
                                    logger.info(f"Lock file belongs to active process {pid} ({name}). Respecting lock.")

                            except psutil.NoSuchProcess:
                                 # Process died during check
                                 should_remove = True
                                 reason = f"Process {pid} died during check"

        except Exception as e:
            logger.error(f"Stale Lock Recovery failed: {e}")
            return

        # Perform removal outside the 'with open' block to avoid WinError 32
        if should_remove:
            logger.warning(f"Stale Lock Recovery: {reason}. Removing lock immediately.")
            self._force_remove_lock()

    def _force_remove_lock(self):
        try:
            if self.lock_path.exists():
                os.remove(self.lock_path)
                logger.info("Stale lock file removed successfully.")
        except Exception as e:
            logger.error(f"Failed to remove stale lock: {e}")

    def _start_heartbeat(self):
        """
        Starts the background heartbeat mechanism to maintain the lock.
        """
        self._stop_heartbeat()
        self._heartbeat_failures = 0

        def _tick():
            if self.is_read_only:
                return

            success = self.lock_manager.update_heartbeat()
            if not success:
                self._heartbeat_failures += 1
                logger.warning(f"HEARTBEAT WARNING: Verification failed ({self._heartbeat_failures}/3).")

                # Tolerance: Force Read-Only only after 3 consecutive failures (30 seconds)
                if self._heartbeat_failures >= 3:
                    logger.critical("HEARTBEAT FAILED: Lock lost (Network issue or Split Brain). Forcing Read-Only mode.")
                    self.force_read_only_mode()
                    return
            else:
                self._heartbeat_failures = 0 # Reset counter on success

            # Schedule next tick (10 seconds)
            self._heartbeat_timer = threading.Timer(10.0, _tick)
            self._heartbeat_timer.daemon = True
            self._heartbeat_timer.start()

        # Start immediately
        _tick()

    def _stop_heartbeat(self):
        if self._heartbeat_timer:
            self._heartbeat_timer.cancel()
            self._heartbeat_timer = None

    def _start_autosave(self):
        """
        Starts the periodic auto-save mechanism.
        """
        self._stop_autosave()

        def _save_tick():
            if self.is_read_only:
                return

            logger.info("Auto-save triggered.")
            self.save_to_disk()

            # Schedule next save (e.g., every 5 minutes = 300 seconds)
            self._autosave_timer = threading.Timer(300.0, _save_tick)
            self._autosave_timer.daemon = True
            self._autosave_timer.start()

        # Start timer (first save after 5 mins)
        self._autosave_timer = threading.Timer(300.0, _save_tick)
        self._autosave_timer.daemon = True
        self._autosave_timer.start()

    def _stop_autosave(self):
        if self._autosave_timer:
            self._autosave_timer.cancel()
            self._autosave_timer = None

    def force_read_only_mode(self):
        """
        Emergency method to switch to Read-Only mode if lock is lost.
        """
        self.is_read_only = True
        self._stop_heartbeat()
        self._stop_autosave()
        logger.warning("System switched to READ-ONLY mode due to lock instability.")

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
            "uuid": str(uuid.uuid4()), # Unique Session ID
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
            self._start_heartbeat()
            self._start_autosave()
        else:
            self.is_read_only = True
            self.read_only_info = owner_info
            logger.warning(f"Session lock failed. Read-Only mode enabled. Owner: {owner_info}")

        return success, owner_info

    def release_lock(self):
        """
        Releases the lock via LockManager.
        """
        self._stop_heartbeat()
        self._stop_autosave()
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

        # BACKUP ON STARTUP (Rolling Backup)
        self.create_backup()

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

            # --- SECURITY & PERFORMANCE HARDENING ---
            try:
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=FULL;")
            except Exception as e:
                logger.warning(f"Failed to set PRAGMA security settings: {e}")

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

    def create_backup(self):
        """Creates a timestamped backup of the database file."""
        if not self.db_path.exists():
            return

        backup_dir = self.data_dir / "Backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = time.strftime("%d-%m-%Y_ore_%H-%M")
        backup_name = f"{self.db_path.stem}_{timestamp}.bak"
        backup_path = backup_dir / backup_name

        try:
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
            self.rotate_backups(backup_dir)
        except Exception as e:
            logger.error(f"Backup failed: {e}")

    def rotate_backups(self, backup_dir: Path, keep: int = 5):
        """Keeps only the recent N backups."""
        try:
            # Find all .bak files matching the pattern
            backups = sorted(backup_dir.glob("*.bak"), key=lambda f: f.stat().st_mtime, reverse=True)

            # Remove older ones
            for old_backup in backups[keep:]:
                try:
                    old_backup.unlink()
                    logger.info(f"Deleted old backup: {old_backup.name}")
                except Exception as e:
                    logger.warning(f"Failed to delete old backup {old_backup.name}: {e}")
        except Exception as e:
             logger.error(f"Rotation failed: {e}")

    def verify_integrity(self, file_path: Path = None) -> bool:
        """
        Verifies the integrity of a database file (encrypted or plain).
        If encrypted, it attempts to decrypt first.
        """
        target = file_path or self.db_path
        if not target.exists():
            return False

        try:
            with open(target, "rb") as f:
                content = f.read()

            if content.startswith(self._HEADER):
                # Decrypt
                try:
                    raw_data = self.fernet.decrypt(content[len(self._HEADER):])
                except Exception:
                    logger.warning(f"Integrity Check: Decryption failed for {target.name}")
                    return False
            else:
                raw_data = content

            # Test SQLite Integrity
            conn = sqlite3.connect(':memory:')
            try:
                conn.deserialize(raw_data)
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                conn.close()

                if result and result[0] == "ok":
                    return True
                else:
                    logger.warning(f"Integrity Check Failed for {target.name}: {result}")
                    return False
            except Exception as e:
                logger.warning(f"Integrity Check Exception for {target.name}: {e}")
                conn.close()
                return False

        except Exception as e:
            logger.error(f"Integrity verification error: {e}")
            return False

    def optimize_database(self):
        """Runs VACUUM and ANALYZE on the in-memory database."""
        if not self.active_connection:
            return

        if self.is_read_only:
            logger.warning("Attempted optimization in READ-ONLY mode. Operation ignored.")
            return

        try:
            logger.info("Starting database optimization (VACUUM)...")
            # VACUUM in sqlite usually requires no active transaction.
            # We execute on the raw connection.
            self.active_connection.execute("VACUUM")
            self.active_connection.execute("ANALYZE")
            logger.info("Database optimization completed.")

            # Save the optimized DB to disk
            self.save_to_disk()
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            raise

    def restore_from_backup(self, backup_path: Path):
        """Restores the database from a backup file."""
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        # Backup current state before overwriting (Safety net)
        self.create_backup()

        try:
            shutil.copy2(backup_path, self.db_path)
            logger.info(f"Restored database from {backup_path}")
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise

    def cleanup(self):
        """
        Shutdown handler. Saves state (if writer) and releases lock.
        """
        self.save_to_disk()
        self.release_lock()

    def toggle_security_mode(self, enable_encryption: bool):
        self.is_locked_mode = enable_encryption
        self.save_to_disk()

    def move_database(self, new_dir_or_path: Path):
        """
        Moves the database file to a new directory or specific file path.
        Updates settings and internal paths.
        """
        if self.is_read_only:
            raise PermissionError("Cannot move database in read-only mode.")

        current_path = self.db_path
        target_path = Path(new_dir_or_path)

        # Check if target is a file (ends with .db) or directory
        if target_path.suffix.lower() == ".db":
            new_path = target_path
            new_data_dir = target_path.parent
        else:
            # Assume directory
            new_path = target_path / current_path.name
            new_data_dir = target_path

        if current_path == new_path:
            logger.info("New database path is the same as the current one. No action taken.")
            return

        # Ensure parent dir exists
        new_data_dir.mkdir(parents=True, exist_ok=True)

        # 1. Save current state to disk before moving
        self.save_to_disk()

        # 2. Move the file
        try:
            shutil.move(str(current_path), str(new_path))
            logger.info(f"Successfully moved database from {current_path} to {new_path}")
        except (IOError, OSError) as e:
            logger.error(f"Failed to move database file: {e}")
            raise

        # 3. Update internal state and settings
        self.data_dir = new_data_dir
        self.db_path = new_path
        # Save the full path if it was a file selection, otherwise the dir
        save_val = str(new_path) if target_path.suffix.lower() == ".db" else str(new_data_dir)
        settings.save_mutable_settings({"DATABASE_PATH": save_val})


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
