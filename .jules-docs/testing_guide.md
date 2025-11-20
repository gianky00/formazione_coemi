# Testing Guide

## Test Structure

The test suite mirrors the application structure:

```
tests/
├── app/
│   ├── api/            # Tests for endpoints
│   ├── db/             # Tests for models/schemas
│   └── services/       # Tests for business logic
└── conftest.py         # Global fixtures and mocking
```

## Key Mocking Requirements

### 1. Google Gemini (`GeminiClient`)

The AI service requires an API key, which is not available in the test environment. You **must** mock the `GeminiClient` to prevent it from initializing the real model.

**How to mock:**
In `tests/conftest.py`, or specifically in your test file:

```python
from unittest.mock import MagicMock, patch

@patch('app.services.ai_extraction.GeminiClient')
def test_extraction(mock_client):
    # Mock the singleton instance and its method
    mock_instance = mock_client.return_value
    mock_model = mock_instance.get_model.return_value

    # Mock the response
    mock_response = MagicMock()
    mock_response.text = '{"nome": "Mario Rossi", ...}'
    mock_model.generate_content.return_value = mock_response

    # Run your test...
```

### 2. FPDF (PDF Generation)

Tests involving `app/services/notification_service.py` or PDF generation must handle file system operations and image assets.

*   **Image Assets**: `FPDF.image()` will fail if the logo file is missing. Mock the `image` method.
*   **Byte Output**: Ensure mocked file objects have valid headers (e.g., `b'\x89PNG...'`) if you are testing `MIMEImage` automatic detection.

### 3. Database

Tests use a separate, in-memory or temporary SQLite database. The fixture `db_session` in `tests/conftest.py` handles the creation and teardown of tables for each test.

## Running Tests

Execute tests from the root directory:

```bash
python -m pytest
```

To run a specific test file:

```bash
python -m pytest tests/app/services/test_certificate_logic.py
```
