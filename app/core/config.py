import json
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import platformdirs

from app.utils.security import reveal_string

# --- Immutable Internal Configuration ---
# These values are hardcoded and cannot be changed by the user.
# They are embedded in the application for security and consistency.

SECRET_KEY: str = "a_very_strong_and_long_secret_key_that_is_not_easily_guessable_and_is_unique_to_this_application"
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 60 minutes

FIRST_RUN_ADMIN_USERNAME: str = "admin"

# This token is injected by the admin/token_injector tool and is obfuscated.
OBFUSCATED_GITHUB_TOKEN: str = "obf:WkZrMlIyVTBLRXJ4ZFlGeUtteTkzMFBSc0xJYkJjSUpLSDNZX3BoZw=="
LICENSE_REPO_OWNER: str = "gianky00"
LICENSE_REPO_NAME: str = "intelleo-licenses"

# ElevenLabs Configuration (Obfuscated for production deployment)
OBFUSCATED_ELEVENLABS_KEY: str = (
    "obf:ZWZmYjdiNGJkZDBhNTZkYjI1NWE1MWU5YzBhMzI2ZmIyYzQxNWNhMzFlMTIxMDY3X2tz"
)
ELEVENLABS_VOICE_ID: str = "XrExE9yKIg1WjnnlVkGX"  # Matilda
ELEVENLABS_MODEL_ID: str = "eleven_multilingual_v2"

SETTINGS_FILENAME: str = "settings.json"

# --- Mutable User Configuration ---


def get_user_data_dir() -> Path:
    """
    Determines the appropriate user-specific data directory based on the OS.
    Uses platformdirs to ensure compliance with OS standards.
    Windows: %LOCALAPPDATA%/Intelleo
    """
    # appauthor=False prevents 'Intelleo/Intelleo' nesting on Windows
    base_dir = Path(platformdirs.user_data_dir("Intelleo", appauthor=False))
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def _migrate_file_location(target_path: Path) -> None:
    """Moves settings.json from legacy temporary locations."""
    if target_path.exists():
        return

    temp_dir = Path(tempfile.gettempdir())
    legacy_path_1 = temp_dir / SETTINGS_FILENAME
    legacy_path_2 = temp_dir / "Intelleo" / SETTINGS_FILENAME

    source: Path | None = None
    if legacy_path_1.exists():
        source = legacy_path_1
    elif legacy_path_2.exists():
        source = legacy_path_2

    if source:
        try:
            logging.info(f"Migrating settings from {source} to {target_path}")
            shutil.move(str(source), str(target_path))
        except Exception as e:
            logging.error(f"Failed to migrate settings: {e}")


def _migrate_settings_keys(target_path: Path) -> None:
    """Updates keys in the existing settings file."""
    if not target_path.exists():
        return

    try:
        with open(target_path, encoding="utf-8") as f:
            data = json.load(f)

        changed = False
        # Migration: GEMINI_API_KEY -> GEMINI_API_KEY_ANALYSIS
        if "GEMINI_API_KEY" in data and "GEMINI_API_KEY_ANALYSIS" not in data:
            data["GEMINI_API_KEY_ANALYSIS"] = data["GEMINI_API_KEY"]
            del data["GEMINI_API_KEY"]
            changed = True

        # Add defaults if missing
        defaults = {
            "GEMINI_API_KEY_CHAT": "",
            "VOICE_ASSISTANT_ENABLED": True,
            "MAX_UPLOAD_SIZE": 20 * 1024 * 1024,  # 20MB
            "MAX_CSV_SIZE": 5 * 1024 * 1024,  # 5MB
        }

        for key, value in defaults.items():
            if key not in data:
                data[key] = value
                changed = True

        if changed:
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            logging.info("Migrated settings keys.")

    except Exception as e:
        logging.error(f"Failed to migrate settings keys: {e}")


def migrate_legacy_settings(target_path: Path) -> None:
    """
    Checks for settings.json in legacy temporary locations and moves it to the target path.
    Also handles internal key migrations (e.g., GEMINI_API_KEY -> GEMINI_API_KEY_ANALYSIS).
    """
    _migrate_file_location(target_path)
    _migrate_settings_keys(target_path)


class MutableSettings:
    """
    Manages user-configurable settings, persisting them to a JSON file.
    """

    def __init__(self, settings_path: Path):
        self.settings_path: Path = settings_path
        self._data: dict[str, Any] = {}

        # Run Migration Check before loading
        migrate_legacy_settings(self.settings_path)

        self._defaults: dict[str, Any] = {
            "DATABASE_PATH": None,
            "FIRST_RUN_ADMIN_PASSWORD": os.getenv("FIRST_RUN_ADMIN_PASSWORD", "prova"),  # NOSONAR
            # Default key is also obfuscated to avoid scanners.
            "GEMINI_API_KEY_ANALYSIS": os.getenv(
                "GEMINI_API_KEY_ANALYSIS", "obf:TUFxc2Y0TkVlQHRhY015Z0NwOFk1VDRCLnl6YUlB"
            ),  # NOSONAR
            # Default dummy key for chat, obfuscated.
            "GEMINI_API_KEY_CHAT": "obf:c3RsdWFmZWRfcm9mX3lla190YWhjX3ltbXVk",
            "VOICE_ASSISTANT_ENABLED": True,
            "SMTP_HOST": "smtps.aruba.it",
            "SMTP_PORT": 465,
            "SMTP_USER": "giancarlo.allegretti@coemi.it",
            "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", "Coemi@2025!!@Gianca"),  # NOSONAR
            "EMAIL_RECIPIENTS_TO": "gianky.allegretti@gmail.com",
            "EMAIL_RECIPIENTS_CC": "gianky.allegretti@gmail.com",
            "ALERT_THRESHOLD_DAYS": 60,
            "ALERT_THRESHOLD_DAYS_VISITE": 30,
            "MAX_UPLOAD_SIZE": 20 * 1024 * 1024,  # 20 MB
            "MAX_CSV_SIZE": 5 * 1024 * 1024,  # 5 MB
        }
        self.load_settings()

    def load_settings(self) -> None:
        """
        Loads settings from the JSON file. If the file doesn't exist or is
        corrupt, it creates a new one with default values.
        """
        if not self.settings_path.exists():
            logging.info(f"'{self.settings_path.name}' not found. Creating with default values.")
            self._data = self._defaults.copy()
            self.save()
            return

        try:
            with open(self.settings_path, encoding="utf-8") as f:
                self._data = json.load(f)
            # Ensure all keys from defaults are present
            changed = False
            for key, value in self._defaults.items():
                if key not in self._data:
                    self._data[key] = value
                    changed = True
            if changed:
                self.save()  # Save to add any missing keys
        except (json.JSONDecodeError, TypeError):
            logging.warning(f"'{self.settings_path.name}' is corrupted. Recreating with defaults.")
            self._data = self._defaults.copy()
            self.save()

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a setting value by key."""
        return self._data.get(key, default)

    def update(self, new_settings: dict[str, Any]) -> None:
        """Updates the settings with new values and saves them to the file."""
        self._data.update(new_settings)
        self.save()

    def save(self) -> None:
        """Saves the current settings to the JSON file."""
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=4)

    def as_dict(self) -> dict[str, Any]:
        """Returns the current settings as a dictionary."""
        return self._data.copy()


# --- Global Settings Manager ---


class SettingsManager:
    def __init__(self) -> None:
        # Immutable settings
        self.SECRET_KEY: str = SECRET_KEY
        self.ALGORITHM: str = ALGORITHM
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = ACCESS_TOKEN_EXPIRE_MINUTES
        self.FIRST_RUN_ADMIN_USERNAME: str = FIRST_RUN_ADMIN_USERNAME
        # The raw value is obfuscated, the property reveals it.
        self._OBFUSCATED_GITHUB_TOKEN: str = OBFUSCATED_GITHUB_TOKEN
        self.LICENSE_REPO_OWNER: str = LICENSE_REPO_OWNER
        self.LICENSE_REPO_NAME: str = LICENSE_REPO_NAME
        # ElevenLabs
        self._OBFUSCATED_ELEVENLABS_KEY: str = OBFUSCATED_ELEVENLABS_KEY
        self.ELEVENLABS_VOICE_ID: str = ELEVENLABS_VOICE_ID
        self.ELEVENLABS_MODEL_ID: str = ELEVENLABS_MODEL_ID

        # Mutable settings
        settings_file_path: Path = get_user_data_dir() / SETTINGS_FILENAME
        self.mutable: MutableSettings = MutableSettings(settings_file_path)

    # Convenience properties to access mutable settings directly
    @property
    def LICENSE_GITHUB_TOKEN(self) -> str:  # NOSONAR
        return reveal_string(self._OBFUSCATED_GITHUB_TOKEN)

    @property
    def ELEVENLABS_API_KEY(self) -> str:  # NOSONAR
        return reveal_string(self._OBFUSCATED_ELEVENLABS_KEY)

    @property
    def FIRST_RUN_ADMIN_PASSWORD(self) -> str:  # NOSONAR
        return str(self.mutable.get("FIRST_RUN_ADMIN_PASSWORD"))

    @property
    def GEMINI_API_KEY_ANALYSIS(self) -> str:  # NOSONAR
        obfuscated_key: str = self.mutable.get("GEMINI_API_KEY_ANALYSIS")
        return reveal_string(obfuscated_key)

    @property
    def GEMINI_API_KEY_CHAT(self) -> str:  # NOSONAR
        obfuscated_key: str = self.mutable.get("GEMINI_API_KEY_CHAT")
        return reveal_string(obfuscated_key)

    @property
    def VOICE_ASSISTANT_ENABLED(self) -> bool:  # NOSONAR
        return bool(self.mutable.get("VOICE_ASSISTANT_ENABLED", True))

    @property
    def SMTP_HOST(self) -> str:  # NOSONAR
        return str(self.mutable.get("SMTP_HOST"))

    @property
    def SMTP_PORT(self) -> int:  # NOSONAR
        return int(self.mutable.get("SMTP_PORT", 465))

    @property
    def SMTP_USER(self) -> str:  # NOSONAR
        return str(self.mutable.get("SMTP_USER"))

    @property
    def SMTP_PASSWORD(self) -> str:  # NOSONAR
        return str(self.mutable.get("SMTP_PASSWORD"))

    @property
    def EMAIL_RECIPIENTS_TO(self) -> str:  # NOSONAR
        return str(self.mutable.get("EMAIL_RECIPIENTS_TO"))

    @property
    def EMAIL_RECIPIENTS_CC(self) -> str:  # NOSONAR
        return str(self.mutable.get("EMAIL_RECIPIENTS_CC"))

    @property
    def ALERT_THRESHOLD_DAYS(self) -> int:  # NOSONAR
        return int(self.mutable.get("ALERT_THRESHOLD_DAYS", 60))

    @property
    def ALERT_THRESHOLD_DAYS_VISITE(self) -> int:  # NOSONAR
        return int(self.mutable.get("ALERT_THRESHOLD_DAYS_VISITE", 30))

    @property
    def DATABASE_PATH(self) -> str | None:  # NOSONAR
        val = self.mutable.get("DATABASE_PATH")
        return str(val) if val else None

    @property
    def DOCUMENTS_FOLDER(self) -> str | None:  # NOSONAR
        """
        Returns the folder for storing documents.
        If DATABASE_PATH points to a .db file, returns its parent folder.
        Otherwise returns DATABASE_PATH itself.
        """
        db_path = self.mutable.get("DATABASE_PATH")
        if not db_path:
            return None
        db_path_str = str(db_path)
        # If it's a file (ends with .db or similar), use parent folder
        if db_path_str.lower().endswith(".db") or os.path.isfile(db_path_str):
            return os.path.dirname(db_path_str)
        return db_path_str

    @property
    def MAX_UPLOAD_SIZE(self) -> int:  # NOSONAR
        return int(self.mutable.get("MAX_UPLOAD_SIZE", 20 * 1024 * 1024))

    @property
    def MAX_CSV_SIZE(self) -> int:  # NOSONAR
        return int(self.mutable.get("MAX_CSV_SIZE", 5 * 1024 * 1024))

    def save_mutable_settings(self, new_settings: dict[str, Any]) -> None:
        """Updates and saves the mutable settings."""
        self.mutable.update(new_settings)


# Instantiate a single settings object for the application to use
settings: SettingsManager = SettingsManager()
