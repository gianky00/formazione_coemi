# Development Protocols & Standards

## 1. Coding Standards

*   **Style Guide**: Strict adherence to **PEP 8**.
*   **Formatting**: Must respect `.editorconfig`.
*   **Naming Conventions**:
    *   Variables/Functions: `snake_case`
    *   Classes: `PascalCase`
    *   Constants: `UPPER_CASE`
*   **Type Hinting**: Mandatory for all function signatures. Use `typing.Optional`, `typing.List`, etc.

## 2. Error Handling Strategy

The application implements a **Full-Stack Error Handling** pattern.

### Backend Layer
*   **Service Layer**: Raise specific Python exceptions (e.g., `ValueError`, `ConnectionAbortedError`).
*   **API Layer**: Catch service exceptions and re-raise `fastapi.HTTPException`.
    *   *400*: Bad Request (Validation failure).
    *   *404*: Not Found.
    *   *409*: Conflict (Duplicate resources).
    *   *422*: Validation Error (Pydantic).
    *   *500*: Internal Server Error (with detailed message).

### Frontend Layer
*   **API Client**: Catches HTTP errors.
*   **UI**: Checks response status. If error, displays `QMessageBox.critical` with the `detail` message from the API.

## 3. Testing Protocols

*   **Framework**: `pytest`.
*   **Execution**: `python -m pytest`.
*   **Structure**: Parallel directory structure (`tests/app/x` tests `app/x`).

### Mocking Requirements
**CRITICAL**: The test environment does not have access to external secrets or file assets.

1.  **Google Gemini AI**:
    *   **Target**: `app.services.ai_extraction.GeminiClient`
    *   **Action**: Must be patched in `tests/conftest.py` or individual tests.
    *   **Reason**: Prevents `ValueError: GEMINI_API_KEY not configured`.

2.  **PDF Assets (FPDF)**:
    *   **Target**: `fpdf.FPDF.image`
    *   **Action**: Mock this method.
    *   **Reason**: Prevents `FileNotFoundError` for `desktop_app/assets/logo.png`.

3.  **Database**:
    *   Use `db_session` fixture to provide an isolated, in-memory SQLite session.

## 4. Environment & Configuration

*   **Management**: A custom `SettingsManager` in `app/core/config.py` separates immutable from mutable settings.
*   **Source**: Mutable settings are stored in `settings.json` in the user's local application data directory.
*   **Constraint**: Unrecognized settings are ignored.

## 5. Git & Contribution

*   **Commits**: Atomic, descriptive messages.
*   **Branches**: Feature branches required. No direct commits to main.
*   **Documentation**: Update `docs/` if architectural changes occur.

## 🤖 AI Metadata (RAG Context)
```json
{
  "type": "development_standards",
  "domain": "coding_guidelines",
  "languages": ["Python", "JavaScript (React)"],
  "standards": ["PEP 8", "Conventional Commits"],
  "testing_frameworks": ["pytest"],
  "error_handling": "Full-Stack Propagation"
}
```
