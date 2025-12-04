from unittest.mock import MagicMock, patch
import pytest

@pytest.fixture
def mock_chat_service():
    with patch("app.api.routers.chat.chat_service") as mock:
        mock.get_rag_context.return_value = "Mock Context"
        mock.chat_with_intelleo.return_value = "Mock Reply"
        yield mock

def test_chat_endpoint_success(test_client, mock_chat_service):
    """
    Test valid chat request.
    Using test_client which has authentication overridden.
    """
    payload = {
        "message": "Hello",
        "history": [{"role": "user", "content": "Hi"}]
    }
    
    # test_client base_url is set to /api/v1 in conftest.
    # The router is included with prefix /api/v1/chat in main.py.
    # Inside router: @router.post("/")
    # So full path is /api/v1/chat/
    
    response = test_client.post("/chat/", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"response": "Mock Reply"}
    
    mock_chat_service.get_rag_context.assert_called_once()
    mock_chat_service.chat_with_intelleo.assert_called_once()
    
    # Verify arguments passed to chat service
    args = mock_chat_service.chat_with_intelleo.call_args
    assert args[0][0] == "Hello" # message
    assert args[0][1] == [{"role": "user", "content": "Hi"}] # history (as dicts)
    assert args[0][2] == "Mock Context" # context

def test_chat_endpoint_error(test_client, mock_chat_service):
    mock_chat_service.chat_with_intelleo.side_effect = Exception("AI Error")
    
    payload = {"message": "Hello"}
    response = test_client.post("/chat/", json=payload)
    
    assert response.status_code == 500
    assert "AI Error" in response.json()["detail"]
