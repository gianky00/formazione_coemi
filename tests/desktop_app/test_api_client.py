import sys
import os
import pytest
from unittest.mock import MagicMock, patch, mock_open
import requests

# Force mock mode (must be before mock_qt import)

# Setup Mocks - use mock_qt_modules() which is safe if real PyQt6 is loaded
from tests.desktop_app.mock_qt import mock_qt_modules
sys.modules.update(mock_qt_modules())

# Mark tests to run in forked subprocess
pytestmark = pytest.mark.forked

from desktop_app.api_client import APIClient

@pytest.fixture
def api_client():
    with patch.dict("os.environ", {"API_URL": "http://test-api"}):
        client = APIClient()
        return client

def test_login_success(api_client):
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "fake_token",
            "token_type": "bearer",
            "read_only": False,
            "lock_owner": None,
            "user_id": 1,
            "username": "user",
            "account_name": "Test User",
            "is_admin": False
        }
        mock_post.return_value = mock_response
        
        result = api_client.login("user", "pass")
        
        # Verify result is the json dict
        assert result["access_token"] == "fake_token"
        
        # Verify internal state isn't set yet (login view does that via set_token usually)
        # Wait, api_client.login just returns data. LoginView calls set_token.
        assert api_client.access_token is None 

def test_set_token(api_client):
    token_data = {
        "access_token": "token123",
        "user_id": 1,
        "username": "user",
        "read_only": True
    }
    api_client.set_token(token_data)
    assert api_client.access_token == "token123"
    assert api_client.user_info["read_only"] is True

def test_logout(api_client):
    api_client.access_token = "token"
    with patch("requests.post") as mock_post:
        api_client.logout()
        mock_post.assert_called_once()
    assert api_client.access_token is None

def test_get_request(api_client):
    api_client.access_token = "fake_token"
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response
        
        data = api_client.get("endpoint")
        
        assert data == {"data": "test"}
        # Check header contains Auth
        args, kwargs = mock_get.call_args
        assert kwargs['headers']['Authorization'] == "Bearer fake_token"

def test_create_dipendente(api_client):
    api_client.access_token = "fake_token"
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 1}
        mock_post.return_value = mock_response
        
        data = api_client.create_dipendente({"nome": "test"})
        
        assert data == {"id": 1}
        args, kwargs = mock_post.call_args
        assert kwargs['json'] == {"nome": "test"}

def test_handle_connection_error(api_client):
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError("Failed")):
        with pytest.raises(ConnectionError) as exc:
            api_client.get("any")
        assert "Offline" in str(exc.value)

def test_import_dipendenti_csv(api_client):
    api_client.access_token = "fake"
    
    # Mock os.path.getsize to return small size
    with patch("os.path.getsize", return_value=1024):
        # Mock open
        m = mock_open(read_data=b"content")
        with patch("builtins.open", m):
            with patch("requests.post") as mock_post:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"status": "ok"}
                mock_post.return_value = mock_response
                
                result = api_client.import_dipendenti_csv("dummy.csv")
                
                assert result["status"] == "ok"
                args, kwargs = mock_post.call_args
                assert 'files' in kwargs
