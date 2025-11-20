
import pytest
from unittest.mock import Mock, patch, mock_open
import os
import requests
from desktop_app.api_client import APIClient

@patch.dict(os.environ, {"API_URL": "http://testserver/api/v1"})
def test_init_custom_url():
    client = APIClient()
    assert client.base_url == "http://testserver/api/v1"

@patch.dict(os.environ, {}, clear=True)
def test_init_default_url():
    client = APIClient()
    assert client.base_url == "http://localhost:8000/api/v1"

@patch('requests.post')
def test_import_dipendenti_csv_success(mock_post):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "Success"}
    mock_post.return_value = mock_response

    client = APIClient()
    file_content = b"some,csv,data"

    with patch("builtins.open", mock_open(read_data=file_content)) as mock_file:
        result = client.import_dipendenti_csv("path/to/file.csv")

        assert result == {"message": "Success"}
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "http://localhost:8000/api/v1/dipendenti/import-csv"
        assert 'files' in kwargs
        assert 'file' in kwargs['files']
        # Verify file tuple structure: (filename, file_obj, content_type)
        assert kwargs['files']['file'][0] == "file.csv"
        assert kwargs['files']['file'][2] == "text/csv"

@patch('requests.post')
def test_import_dipendenti_csv_failure(mock_post):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Server Error")
    mock_post.return_value = mock_response

    client = APIClient()

    with patch("builtins.open", mock_open(read_data=b"data")):
        with pytest.raises(requests.exceptions.HTTPError):
            client.import_dipendenti_csv("path/to/file.csv")
