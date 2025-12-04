import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the project root to the Python path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Mock PyQt classes before importing the view
from tests.desktop_app.mock_qt import QtWidgets, QtCore

@pytest.fixture
def mock_api_client():
    """Fixture to create a mock APIClient."""
    client = MagicMock()
    client.user_info = {"is_admin": True}
    # Simulate the data returned by the GET /config endpoint
    client.get_mutable_config.return_value = {
        "GEMINI_API_KEY_ANALYSIS": "test_analysis_key",
        "GEMINI_API_KEY_CHAT": "test_chat_key",
        "VOICE_ASSISTANT_ENABLED": True,
        "SMTP_HOST": "smtp.test.com",
        "SMTP_PORT": 587,
        "SMTP_USER": "test@user.com",
        "SMTP_PASSWORD": "password",
        "EMAIL_RECIPIENTS_TO": "test@to.com",
        "EMAIL_RECIPIENTS_CC": "test@cc.com",
        "ALERT_THRESHOLD_DAYS": 45,
        "ALERT_THRESHOLD_DAYS_VISITE": 15,
    }
    return client

@patch('desktop_app.views.config_view.APIClient')
def test_config_view_loads_settings_from_api(MockAPIClient, mock_api_client):
    """
    Test that the ConfigView calls the API to load settings and populates the UI fields.
    """
    MockAPIClient.return_value = mock_api_client

    from desktop_app.views.config_view import ConfigView

    view = ConfigView(mock_api_client)

    # Trigger the load_config method
    view.load_config()

    # Assert that the API was called
    mock_api_client.get_mutable_config.assert_called_once()

    # Assert that UI fields are populated with the mock data
    # Updated: access fields via specific tabs
    gs = view.general_settings
    api = view.api_settings
    email = view.email_settings

    assert api.gemini_analysis_key_input.text() == "test_analysis_key"
    assert api.gemini_chat_key_input.text() == "test_chat_key"
    assert api.voice_assistant_check.isChecked() == True
    assert email.smtp_host_input.text() == "smtp.test.com"
    assert email.smtp_port_input.text() == "587"
    assert gs.alert_threshold_input.text() == "45"

@patch('desktop_app.views.config_view.APIClient')
def test_config_view_saves_settings_via_api(MockAPIClient, mock_api_client):
    """
    Test that the ConfigView calls the API to save settings when the button is clicked.
    """
    MockAPIClient.return_value = mock_api_client

    from desktop_app.views.config_view import ConfigView

    view = ConfigView(mock_api_client)
    view.load_config() # Load initial state

    # Simulate user changing a value
    view.email_settings.smtp_host_input.setText("smtp.new.com")
    view.general_settings.alert_threshold_input.setText("90")
    view.api_settings.voice_assistant_check.setChecked(False)

    # Simulate clicking the save button
    view.save_config()

    # Assert that the update method was called on the API client
    mock_api_client.update_mutable_config.assert_called_once()

    # Check the payload that was sent
    sent_payload = mock_api_client.update_mutable_config.call_args[0][0]
    assert sent_payload["SMTP_HOST"] == "smtp.new.com"
    assert sent_payload["ALERT_THRESHOLD_DAYS"] == 90
    assert sent_payload["VOICE_ASSISTANT_ENABLED"] == False
    
    # Verify that an unchanged value is NOT in the payload
    assert "GEMINI_API_KEY_ANALYSIS" not in sent_payload
