import base64
import hashlib
import logging
import os
import shutil
import socket
import sqlite3
import threading
import time
import uuid
from pathlib import Path
from typing import Any

import psutil
from cryptography.fernet import Fernet
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from app.core.config import get_user_data_dir, settings
from app.core.lock_manager import LockManager

logger = logging.getLogger(__name__)


class DBSecurityManager:
    """
    Manages the security of the SQLite database using strict In-Memory handling.
    """

    _STATIC_SECRET_OBF: str = "SU5URUxMRU9fREJfU0VDUkVUX0tFWV9WMV8yMDI0X1NFQ1VSRV9BQ0NFU1M="
    _HEADER: bytes = b"INTELLEO_SEC_V1"

    def __init__(self, db_name: str = "database_documenti.db"):
        self._STATIC_SECRET: str = base64.b64decode(self._STATIC_SECRET_OBF).decode("utf-8")

        custom_path_str = settings.DATABASE_PATH
        if custom_path_str:
            path_obj = Path(custom_path_str)
            if path_obj.is_dir():
                self.data_dir = path_obj
                self.db_path = self.data_dir / db_name
            elif path_obj.suffix.lower() == ".db":
                self.db_path = path_obj
                self.data_dir = path_obj.parent
            else:
                self.data_dir = get_user_data_dir()
                self.db_path = self.data_dir / db_name
        else:
            self.data_dir = get_user_data_dir()
            self.db_path = self.data_dir / db_name

        self.lock_path: Path = self.data_dir / f".{db_name}.lock"

        self._check_and_recover_stale_lock()

        cwd_db = Path.cwd() / db_name
        if cwd_db.exists() and not self.db_path.exists():
            try:
                shutil.copy2(cwd_db, self.db_path)
                logger.info(f"Migrated database from {cwd_db} to {self.db_path}")
            except Exception as e:
                logger.warning(f"Failed to migrate database: {e}")

        self.key: bytes = self._derive_key()
        self.fernet: Fernet = Fernet(self.key)

        self.active_connection: sqlite3.Connection | None = None
        self.initial_bytes: bytes | None = None
        self.is_locked_mode: bool = False
        self.is_read_only: bool = True
        self.read_only_info: dict[str, Any] | None = None

        self.lock_manager: LockManager = LockManager(str(self.lock_path))
        self._heartbeat_timer: threading.Timer | None = None
        self._autosave_timer: threading.Timer | None = None
        self._heartbeat_failures: int = 0

    def _derive_key(self) -> bytes:
        digest = hashlib.sha256(self._STATIC_SECRET.encode()).digest()
        return base64.urlsafe_b64encode(digest)

    def _should_remove_lock(self, metadata: dict[str, Any]) -> tuple[bool, str | None]:
        pid = metadata.get("pid")
        if not pid:
            return False, "No PID"

        if not psutil.pid_exists(pid):
            return True, f"PID {pid} is DEAD"

        try:
            proc = psutil.Process(pid)
            name = proc.name().lower()
            valid_names = ["python", "intelleo", "main", "launcher", "boot_loader", "pytest"]
            if not any(v in name for v in valid_names):
                return True, f"PID {pid} exists ({name}) but is unrelated"
            else:
                logger.info(f"Lock file belongs to active process {pid} ({name}). Respecting lock.")
                return False, None
        except psutil.NoSuchProcess:
            return True, f"Process {pid} died during check"

    def _check_and_recover_stale_lock(self) -> None:
        if not self.lock_path.exists():
            return

        should_remove = False
        reason = ""

        try:
            with open(self.lock_path, "rb") as f:
                f.seek(1)
                data = f.read()
                if not data:
                    return

                import json

                try:
                    metadata = dict(json.loads(data.decode("utf-8")))
                    should_remove, reason_val = self._should_remove_lock(metadata)
                    if reason_val:
                        reason = reason_val
                except json.JSONDecodeError:
                    should_remove = True
                    reason = "Corrupt lock file (invalid JSON)"
                except UnicodeDecodeError:
                    should_remove = True
                    reason = "Corrupt lock file (invalid encoding)"

        except PermissionError as e:
            logger.debug(f"Lock file is actively held by another process: {e}")
            return
        except FileNotFoundError:
            return
        except Exception as e:
            logger.error(f"Stale Lock Recovery failed: {e}")
            return

        if should_remove:
            logger.warning(f"Stale Lock Recovery: {reason}. Removing lock immediately.")
            self._force_remove_lock()

    def _force_remove_lock(self) -> None:
        try:
            if self.lock_path.exists():
                os.remove(self.lock_path)
                logger.info("Stale lock file removed successfully.")
        except Exception as e:
            logger.error(f"Failed to remove stale lock: {e}")

    def _start_heartbeat(self) -> None:
        self._stop_heartbeat()
        self._heartbeat_failures = 0

        def _tick() -> None:
            if self.is_read_only:
                return

            success = self.lock_manager.update_heartbeat()
            if not success:
                self._heartbeat_failures += 1
                logger.warning(
                    f"HEARTBEAT WARNING: Verification failed ({self._heartbeat_failures}/3)."
                )

                if self._heartbeat_failures >= 3:
                    logger.critical("HEARTBEAT FAILED: Lock lost. Forcing Read-Only mode.")
                    self.force_read_only_mode()
                    return
            else:
                self._heartbeat_failures = 0

            self._heartbeat_timer = threading.Timer(10.0, _tick)
            self._heartbeat_timer.daemon = True
            self._heartbeat_timer.start()

        _tick()

    def _stop_heartbeat(self) -> None:
        if self._heartbeat_timer:
            self._heartbeat_timer.cancel()
            self._heartbeat_timer = None

    def _start_autosave(self) -> None:
        self._stop_autosave()

        def _save_tick() -> None:
            if self.is_read_only:
                return

            logger.info("Auto-save triggered.")
            self.save_to_disk()

            self._autosave_timer = threading.Timer(300.0, _save_tick)
            self._autosave_timer.daemon = True
            self._autosave_timer.start()

        self._autosave_timer = threading.Timer(300.0, _save_tick)
        self._autosave_timer.daemon = True
        self._autosave_timer.start()

    def _stop_autosave(self) -> None:
        if self._autosave_timer:
            self._autosave_timer.cancel()
            self._autosave_timer = None

    def force_read_only_mode(self) -> None:
        self.is_read_only = True
        self._stop_heartbeat()
        self._stop_autosave()
        logger.warning("System switched to READ-ONLY mode due to lock instability.")

    def acquire_session_lock(self, user_info: dict[str, Any]) -> tuple[bool, dict[str, Any] | None]:
        metadata = {
            "uuid": str(uuid.uuid4()),
            "pid": os.getpid(),
            "hostname": socket.gethostname(),
            "timestamp": time.time(),
            **user_info,
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

    def release_lock(self) -> None:
        self._stop_heartbeat()
        self._stop_autosave()
        self.lock_manager.release()
        self.is_read_only = True

    def load_memory_db(self) -> None:
        if not self.db_path.exists():
            logger.info("Database missing. Initializing new in-memory DB.")
            self.is_locked_mode = True
            self.initial_bytes = None
            return

        self.create_backup()

        try:
            with open(self.db_path, "rb") as f:
                content = f.read()
        except Exception as e:
            raise RuntimeError(f"Could not read database file: {e}") from e

        if content.startswith(self._HEADER):
            logger.info("Loading ENCRYPTED database into memory.")
            self.is_locked_mode = True
            try:
                self.initial_bytes = self.fernet.decrypt(content[len(self._HEADER) :])
            except Exception as e:
                raise ValueError(f"Failed to decrypt database: {e}") from e
        else:
            logger.info("Loading PLAIN database into memory. Security upgrade enforced.")
            self.is_locked_mode = True
            self.initial_bytes = content

    def get_connection(self) -> sqlite3.Connection:
        if self.active_connection is None:
            conn = sqlite3.connect(":memory:", check_same_thread=False)
            try:
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=FULL;")
            except Exception as e:
                logger.warning(f"Failed to set PRAGMA security settings: {e}")

            if self.initial_bytes:
                try:
                    conn.deserialize(self.initial_bytes)
                except AttributeError:
                    raise RuntimeError("SQLite version does not support 'deserialize'.") from None
                except Exception as e:
                    raise RuntimeError(f"Failed to deserialize database: {e}") from e

            self.active_connection = conn

        return self.active_connection

    @retry(  # type: ignore
        stop=stop_after_attempt(5),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(PermissionError),
    )
    def _safe_write(self, data: bytes) -> None:
        swp_path = self.db_path.with_suffix(".swp")
        with open(swp_path, "wb") as f:
            f.write(data)

        if os.name == "nt" and self.db_path.exists():
            try:
                os.replace(swp_path, self.db_path)
            except PermissionError:
                logger.warning(f"PermissionError replacing DB file {self.db_path}. Retrying...")
                raise
        else:
            os.replace(swp_path, self.db_path)

    def save_to_disk(self) -> bool:
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

    def create_backup(self) -> None:
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

    def rotate_backups(self, backup_dir: Path, keep: int = 5) -> None:
        try:
            backups = sorted(
                backup_dir.glob("*.bak"), key=lambda f: f.stat().st_mtime, reverse=True
            )
            for old_backup in backups[keep:]:
                try:
                    old_backup.unlink()
                    logger.info(f"Deleted old backup: {old_backup.name}")
                except Exception as e:
                    logger.warning(f"Failed to delete old backup {old_backup.name}: {e}")
        except Exception as e:
            logger.error(f"Rotation failed: {e}")

    def verify_integrity(self, file_path: Path | None = None) -> bool:
        target = file_path or self.db_path
        if not target.exists():
            return False

        try:
            with open(target, "rb") as f:
                content = f.read()

            if content.startswith(self._HEADER):
                try:
                    raw_data = self.fernet.decrypt(content[len(self._HEADER) :])
                except Exception:
                    logger.warning(f"Integrity Check: Decryption failed for {target.name}")
                    return False
            else:
                raw_data = content

            conn = sqlite3.connect(":memory:")
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

    def optimize_database(self) -> None:
        if not self.active_connection:
            return

        if self.is_read_only:
            logger.warning("Attempted optimization in READ-ONLY mode. Operation ignored.")
            return

        try:
            logger.info("Starting database optimization (VACUUM)...")
            self.active_connection.execute("VACUUM")
            self.active_connection.execute("ANALYZE")
            logger.info("Database optimization completed.")
            self.save_to_disk()
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            raise

    def restore_from_backup(self, backup_path: Path) -> None:
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        self.create_backup()

        try:
            shutil.copy2(backup_path, self.db_path)
            logger.info(f"Restored database from {backup_path}")
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise

    def cleanup(self) -> None:
        self.save_to_disk()
        self.release_lock()

    def toggle_security_mode(self, enable_encryption: bool) -> None:
        self.is_locked_mode = enable_encryption
        self.save_to_disk()

    def move_database(self, new_dir_or_path: Path) -> None:
        if self.is_read_only:
            raise PermissionError("Cannot move database in read-only mode.")

        current_path = self.db_path
        target_path = Path(new_dir_or_path)

        if target_path.suffix.lower() == ".db":
            new_path = target_path
            new_data_dir = target_path.parent
        else:
            new_path = target_path / current_path.name
            new_data_dir = target_path

        if current_path == new_path:
            logger.info("New database path is the same as the current one. No action taken.")
            return

        new_data_dir.mkdir(parents=True, exist_ok=True)
        self.save_to_disk()

        try:
            shutil.move(str(current_path), str(new_path))
            logger.info(f"Successfully moved database from {current_path} to {new_path}")
        except OSError as e:
            logger.error(f"Failed to move database file: {e}")
            raise

        self.data_dir = new_data_dir
        self.db_path = new_path
        save_val = str(new_path) if target_path.suffix.lower() == ".db" else str(new_data_dir)
        settings.save_mutable_settings({"DATABASE_PATH": save_val})

    def sync_db(self) -> bool:
        return self.save_to_disk()

    def create_lock(self) -> None:
        self.acquire_session_lock({"user": "system"})

    def check_lock_exists(self) -> bool:
        return self.lock_path.exists()

    @property
    def has_lock(self) -> bool:
        return not self.is_read_only


db_security: DBSecurityManager = DBSecurityManager()
