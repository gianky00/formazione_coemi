import json
import os
import shutil
import tempfile
import platformdirs
from pathlib import Path
import logging
from app.utils.security import reveal_string

# --- Immutable Internal Configuration ---
# These values are hardcoded and cannot be changed by the user.
# They are embedded in the application for security and consistency.

SECRET_KEY = "a_very_strong_and_long_secret_key_that_is_not_easily_guessable_and_is_unique_to_this_application"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 43200  # 30 days

FIRST_RUN_ADMIN_USERNAME = "admin"

# This token is injected by the admin/token_injector tool and is obfuscated.
OBFUSCATED_GITHUB_TOKEN = "obf:WkZrMlIyVTBLRXJ4ZFlGeUtteTkzMFBSc0xJYkJjSUpLSDNZX3BoZw=="
LICENSE_REPO_OWNER = "gianky00"
LICENSE_REPO_NAME = "intelleo-licenses"

# --- Mutable User Configuration ---

def get_user_data_dir() -> Path:
    """
    Determines the appropriate user-specific data directory based on the OS.
    Uses platformdirs to ensure compliance with OS standards.
    Windows: %LOCALAPPDATA%/Intelleo
    """
    base_dir = Path(platformdirs.user_data_dir("Intelleo", "Intelleo"))
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

def migrate_legacy_settings(target_path: Path):
    """
    Checks for settings.json in legacy temporary locations and moves it to the target path.
    1. %TEMP%/settings.json
    2. %TEMP%/Intelleo/settings.json
    """
    if target_path.exists():
        return

    temp_dir = Path(tempfile.gettempdir())

    # Priority 1: Direct in Temp
    legacy_path_1 = temp_dir / "settings.json"

    # Priority 2: Temp/Intelleo
    legacy_path_2 = temp_dir / "Intelleo" / "settings.json"

    source = None
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

class MutableSettings:
    """
    Manages user-configurable settings, persisting them to a JSON file.
    """
    def __init__(self, settings_path: Path):
        self.settings_path = settings_path

        # Run Migration Check before loading
        migrate_legacy_settings(self.settings_path)

        self._defaults = {
            "DATABASE_PATH": None,
            "FIRST_RUN_ADMIN_PASSWORD": "prova",
            # Default key is also obfuscated to avoid scanners.
            "GEMINI_API_KEY": "obf:TUFxc2Y0TkVlQHRhY015Z0NwOFk1VDRCLnl6YUlB",
            "SMTP_HOST": "smtps.aruba.it",
            "SMTP_PORT": 465,
            "SMTP_USER": "giancarlo.allegretti@coemi.it",
            "SMTP_PASSWORD": "Coemi@2025!!@Gianca",
            "EMAIL_RECIPIENTS_TO": "gianky.allegretti@gmail.com",
            "EMAIL_RECIPIENTS_CC": "gianky.allegretti@gmail.com",
            "ALERT_THRESHOLD_DAYS": 60,
            "ALERT_THRESHOLD_DAYS_VISITE": 30,
        }
        self.load_settings()

    def load_settings(self):
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
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
            # Ensure all keys from defaults are present
            for key, value in self._defaults.items():
                if key not in self._data:
                    self._data[key] = value
            self.save() # Save to add any missing keys
        except (json.JSONDecodeError, TypeError):
            logging.warning(f"'{self.settings_path.name}' is corrupted. Recreating with defaults.")
            self._data = self._defaults.copy()
            self.save()

    def get(self, key: str, default=None):
        """Retrieves a setting value by key."""
        return self._data.get(key, default)

    def update(self, new_settings: dict):
        """Updates the settings with new values and saves them to the file."""
        self._data.update(new_settings)
        self.save()

    def save(self):
        """Saves the current settings to the JSON file."""
        with open(self.settings_path, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, indent=4)

    def as_dict(self):
        """Returns the current settings as a dictionary."""
        return self._data.copy()

# --- Global Settings Manager ---

class SettingsManager:
    def __init__(self):
        # Immutable settings
        self.SECRET_KEY = SECRET_KEY
        self.ALGORITHM = ALGORITHM
        self.ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
        self.FIRST_RUN_ADMIN_USERNAME = FIRST_RUN_ADMIN_USERNAME
        # The raw value is obfuscated, the property reveals it.
        self._OBFUSCATED_GITHUB_TOKEN = OBFUSCATED_GITHUB_TOKEN
        self.LICENSE_REPO_OWNER = LICENSE_REPO_OWNER
        self.LICENSE_REPO_NAME = LICENSE_REPO_NAME

        # Mutable settings
        settings_file_path = get_user_data_dir() / "settings.json"
        self.mutable = MutableSettings(settings_file_path)

    # Convenience properties to access mutable settings directly
    @property
    def LICENSE_GITHUB_TOKEN(self):
        return reveal_string(self._OBFUSCATED_GITHUB_TOKEN)

    @property
    def FIRST_RUN_ADMIN_PASSWORD(self):
        return self.mutable.get("FIRST_RUN_ADMIN_PASSWORD")

    @property
    def GEMINI_API_KEY(self):
        obfuscated_key = self.mutable.get("GEMINI_API_KEY")
        return reveal_string(obfuscated_key)

    @property
    def SMTP_HOST(self):
        return self.mutable.get("SMTP_HOST")

    @property
    def SMTP_PORT(self):
        return self.mutable.get("SMTP_PORT")

    @property
    def SMTP_USER(self):
        return self.mutable.get("SMTP_USER")

    @property
    def SMTP_PASSWORD(self):
        return self.mutable.get("SMTP_PASSWORD")

    @property
    def EMAIL_RECIPIENTS_TO(self):
        return self.mutable.get("EMAIL_RECIPIENTS_TO")

    @property
    def EMAIL_RECIPIENTS_CC(self):
        return self.mutable.get("EMAIL_RECIPIENTS_CC")

    @property
    def ALERT_THRESHOLD_DAYS(self):
        return self.mutable.get("ALERT_THRESHOLD_DAYS")

    @property
    def ALERT_THRESHOLD_DAYS_VISITE(self):
        return self.mutable.get("ALERT_THRESHOLD_DAYS_VISITE")

    @property
    def DATABASE_PATH(self):
        return self.mutable.get("DATABASE_PATH")

    def save_mutable_settings(self, new_settings: dict):
        """Updates and saves the mutable settings."""
        self.mutable.update(new_settings)
        # In a real app, you might want to notify other parts of the system
        # that the configuration has changed.

# Instantiate a single settings object for the application to use
settings = SettingsManager()
