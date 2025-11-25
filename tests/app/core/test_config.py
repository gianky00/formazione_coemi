import json
import os
from pathlib import Path
import pytest

# Import the new settings manager
from app.core.config import SettingsManager, get_user_data_dir

@pytest.fixture
def test_data_dir(tmp_path: Path) -> Path:
    """Create a temporary data directory for tests."""
    return tmp_path

@pytest.fixture
def settings_file(test_data_dir: Path) -> Path:
    """Provides the path to the settings file in the temp directory."""
    return test_data_dir / "settings.json"

def test_immutable_settings_are_hardcoded(monkeypatch):
    """
    Test that critical, unchangeable settings are hardcoded constants.
    """
    monkeypatch.setattr('app.core.config.get_user_data_dir', lambda: Path("/tmp"))
    settings = SettingsManager()
    assert settings.SECRET_KEY == "a_very_strong_and_long_secret_key_that_is_not_easily_guessable_and_is_unique_to_this_application"
    assert settings.ALGORITHM == "HS256"
    assert settings.FIRST_RUN_ADMIN_USERNAME == "admin"
    assert settings.LICENSE_REPO_OWNER == "gianky00"

def test_mutable_settings_creation_on_first_run(settings_file: Path, monkeypatch):
    """
    Test that if settings.json does not exist, it is created with default values.
    """
    assert not settings_file.exists()

    monkeypatch.setattr('app.core.config.get_user_data_dir', lambda: settings_file.parent)

    settings = SettingsManager()

    assert settings_file.exists()
    with open(settings_file, 'r') as f:
        data = json.load(f)

    assert data["SMTP_HOST"] == "smtps.aruba.it"
    assert data["SMTP_PORT"] == 465
    assert data["FIRST_RUN_ADMIN_PASSWORD"] == "prova"
    assert settings.SMTP_HOST == "smtps.aruba.it"

def test_mutable_settings_loading_from_existing_file(settings_file: Path, monkeypatch):
    """
    Test that settings are correctly loaded from an existing settings.json.
    """
    custom_settings = {
        "SMTP_HOST": "smtp.custom.com",
        "SMTP_PORT": 1234,
        "GEMINI_API_KEY": "custom_api_key"
    }
    with open(settings_file, 'w') as f:
        json.dump(custom_settings, f)

    monkeypatch.setattr('app.core.config.get_user_data_dir', lambda: settings_file.parent)

    settings = SettingsManager()

    assert settings.SMTP_HOST == "smtp.custom.com"
    assert settings.SMTP_PORT == 1234
    assert settings.GEMINI_API_KEY == "custom_api_key"
    assert settings.ALERT_THRESHOLD_DAYS == 60

def test_mutable_settings_update_and_save(settings_file: Path, monkeypatch):
    """
    Test that updating settings saves them correctly to the file.
    """
    monkeypatch.setattr('app.core.config.get_user_data_dir', lambda: settings_file.parent)

    settings = SettingsManager()

    assert settings.SMTP_USER == "giancarlo.allegretti@coemi.it"

    new_values = {"SMTP_USER": "new.user@test.com", "SMTP_PORT": 587}
    settings.save_mutable_settings(new_values)

    assert settings.SMTP_USER == "new.user@test.com"
    assert settings.SMTP_PORT == 587

    with open(settings_file, 'r') as f:
        data = json.load(f)
    assert data["SMTP_USER"] == "new.user@test.com"
    assert data["SMTP_PORT"] == 587

def test_handles_corrupted_settings_file(settings_file: Path, monkeypatch):
    """
    Test that a corrupted JSON file is handled gracefully by creating a new
    one with default values.
    """
    with open(settings_file, 'w') as f:
        f.write("{'this_is_not_valid_json':}")

    monkeypatch.setattr('app.core.config.get_user_data_dir', lambda: settings_file.parent)

    settings = SettingsManager()

    with open(settings_file, 'r') as f:
        data = json.load(f)

    assert data["SMTP_HOST"] == "smtps.aruba.it"
    assert settings.SMTP_HOST == "smtps.aruba.it"
