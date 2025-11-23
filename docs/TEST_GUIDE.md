# Comprehensive Testing Guide

This document outlines the testing protocols for the Intelleo codebase, covering Unit Tests, Frontend Verification, and Distribution checks.

## 1. Automated Unit & Integration Tests (`pytest`)

The project maintains a comprehensive test suite using `pytest`. These tests cover the API, Database Logic, AI Service (mocked), and Desktop Utilities.

### Prerequisites
*   Virtual Environment activated.
*   Dependencies installed (`pip install -r requirements.txt`).

### Running the Tests
Execute the following command from the repository root:

```bash
python -m pytest
```

### Test Structure
*   `tests/app/`: Backend tests (API endpoints, DB models, Services).
*   `tests/desktop_app/`: Frontend logic tests (View Models, Utils, Import Logic).
    *   *Note*: UI components (`QWidget`) are tested in headless mode using `mock_qt.py` to simulate the PyQt6 environment without a display.

### Critical Considerations
*   **Mocking**: External services (Google Gemini, SMTP) are **always mocked**. Do not require real API keys to run tests.
*   **Database**: Tests use an isolated in-memory SQLite database (`:memory:`), separate from the development `database_documenti.db`.

## 2. Frontend User Guide Verification (React)

The "Modern Software Guide" (`guide_frontend/`) is a standard React + Vite application.

### Verification Steps
1.  Navigate to the directory:
    ```bash
    cd guide_frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server to verify UI rendering:
    ```bash
    npm run dev
    ```
4.  Build verification:
    ```bash
    npm run build
    ```
    Ensure the `dist/` folder is generated without errors.

## 3. Distribution & License Verification (Manual)

After building the application (see `BUILD_INSTRUCTIONS.md`), perform these manual checks on the generated executable.

### Location
`dist/Intelleo/Intelleo.exe`

### Test 1: Hardware ID (HWID)
Verify the application can read the machine's fingerprint.
```bash
Intelleo.exe --hwid
```
*Expected*: Prints an alphanumeric string. MUST NOT print "N/A" or crash.

### Test 2: License Validation
1.  Generate a license using `admin_license_gui.py`.
2.  Place `pyarmor.rkey` and `dettagli_licenza.txt` in the `Licenza` subfolder.
3.  Launch `Intelleo.exe`.
*Expected*: App launches, skips the "License Expired" warning, and shows the Dashboard.
*Failure*: If app closes immediately or shows errors, check `debug_hwid.log` (if enabled) or run via console.

### Test 3: API/Backend Startup
Launch the app and check the log files or console output.
*Expected*: "FastAPI startup complete", "Database loaded in memory".
