import pytest
from app.core.config import SettingsManager
from app.utils.security import reveal_string, obfuscate_string

# No need for file-based fixtures anymore, as settings are mocked globally.

def test_immutable_settings_are_correct():
    """
    Test that critical, unchangeable settings have the correct hardcoded values.
    """
    settings = SettingsManager()
    assert settings.SECRET_KEY == "a_very_strong_and_long_secret_key_that_is_not_easily_guessable_and_is_unique_to_this_application"
    assert settings.ALGORITHM == "HS256"
    assert settings.FIRST_RUN_ADMIN_USERNAME == "admin"

def test_settings_manager_properties_access_mock(mock_mutable_settings):
    """
    Verify that SettingsManager properties correctly access the mocked mutable settings.
    The mock is provided by the autouse fixture in conftest.py.
    """
    settings = SettingsManager()

    # These values come directly from the mock_mutable_settings fixture
    assert settings.SMTP_HOST == "smtp.test.com"
    assert settings.ALERT_THRESHOLD_DAYS == 60
    assert settings.DATABASE_PATH is None

def test_save_mutable_settings_updates_mock(mock_mutable_settings):
    """
    Test that calling save_mutable_settings correctly updates the in-memory mock.
    """
    settings = SettingsManager()
    
    # Verify initial state from mock
    assert settings.SMTP_PORT == 587

    # Update a value
    new_values = {"SMTP_PORT": 9999}
    settings.save_mutable_settings(new_values)

    # Verify the settings manager now returns the new value
    assert settings.SMTP_PORT == 9999

# --- Tests for Security Obfuscation ---

def test_github_token_is_revealed_at_runtime():
    """
    Tests that the hardcoded obfuscated GitHub token is correctly revealed.
    This test does not require mocking because it uses an immutable, hardcoded value.
    """
    settings = SettingsManager()
    
    # The raw value is hardcoded in config.py
    expected_token = "fake_token"
    
    assert settings.LICENSE_GITHUB_TOKEN == expected_token
    assert settings._OBFUSCATED_GITHUB_TOKEN != expected_token
    assert settings._OBFUSCATED_GITHUB_TOKEN.startswith("obf:")

def test_gemini_api_key_is_revealed_at_runtime(mock_mutable_settings):
    """
    Tests that an obfuscated Gemini key from the mocked settings is correctly revealed.
    """
    settings = SettingsManager()
    
    # 1. Define the plain text key we want to test with.
    plain_key = "my-secret-gemini-key"
    
    # 2. Obfuscate it using the actual utility function.
    obfuscated_key = obfuscate_string(plain_key)
    
    # 3. Update the mock settings to use this new obfuscated key.
    settings.save_mutable_settings({"GEMINI_API_KEY": obfuscated_key})
    
    # 4. Assert that the SettingsManager property correctly reveals the original plain key.
    assert settings.GEMINI_API_KEY == plain_key
    
    # 5. (Optional) Verify that the raw value in the mock is still obfuscated.
    assert settings.mutable.get("GEMINI_API_KEY") == obfuscated_key
