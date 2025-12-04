# Project Structure and Test Coverage Analysis

## 1. Backend (`app/`)
The backend is a FastAPI application responsible for business logic, database management, security, and AI services.

### Core Structure
*   **`app/api/`**: Contains the API definitions.
    *   `routers/`: Individual route modules (e.g., `auth.py`, `users.py`, `notifications.py`, `stats.py`).
    *   `deps.py`: Dependency injection (authentication, database session, permissions).
    *   `main.py`: API entry point and router aggregation.
*   **`app/core/`**: Infrastructure and Security.
    *   `config.py`: Configuration management (SettingsManager).
    *   `security.py`: JWT utilities, password hashing.
    *   `db_security.py`: `DBSecurityManager` (In-memory encryption, locking).
    *   `lock_manager.py`: OS-level file locking.
    *   `license_security.py`: License verification logic.
*   **`app/db/`**: Database Layer.
    *   `models.py`: SQLAlchemy ORM models (`User`, `Dipendente`, `Certificato`, `AuditLog`).
    *   `session.py`: Database engine and session factory.
    *   `seeding.py`: Initial data population.
*   **`app/services/`**: Business Logic.
    *   `ai_extraction.py`: Gemini-based document analysis.
    *   `certificate_logic.py`: Expiration calculation, status logic.
    *   `notification_service.py`: Email alerts and report generation.
    *   `document_locator.py`: File system organization and retrieval.
    *   `matcher.py`: Employee name matching (homonym resolution).

### Test Coverage (`tests/app/`)
*   **API Tests** (`tests/app/api/`): Comprehensive coverage of endpoints using `TestClient`.
    *   `routers/`: Specific tests for each router (e.g., `test_auth_router.py`, `test_users_full.py`).
    *   `test_main.py`: General API tests.
*   **Core Tests** (`tests/app/core/`):
    *   `test_db_security*.py`: Extensive testing of encryption, locking, and concurrency.
    *   `test_lock_manager*.py`: OS-level locking verification.
*   **Service Tests** (`tests/app/services/`): Unit tests for business logic (AI, certificates, notifications).

---

## 2. Desktop Application (`desktop_app/`)
The frontend is a PyQt6 application communicating with the backend via REST API.

### Core Structure
*   **`desktop_app/views/`**: UI Components (MVVM-lite).
    *   `login_view.py`: Authentication and License checks.
    *   `dashboard_view.py`: Main data grid (Certificates).
    *   `scadenzario_view.py`: Gantt chart and timeline.
    *   `import_view.py`: Drag & Drop import interface.
    *   `validation_view.py`: Manual validation interface.
    *   `config_view.py`: Settings management.
    *   `modern_guide_view.py`: Embedded React guide integration.
*   **`desktop_app/view_models/`**: Logic separation.
    *   `database_view_model.py`: Handles data fetching and filtering for Dashboard.
*   **`desktop_app/components/`**: Reusable Widgets.
    *   `animated_widgets.py`: Buttons, Loaders.
    *   `custom_dialog.py`: Standardized alerts/confirmations.
*   **`desktop_app/services/`**: Frontend-specific services.
    *   `api_client.py`: HTTP Client with Token management.
    *   `license_manager.py`: Client-side license handling.
    *   `worker.py` / `workers/`: Background threading (QRunnable).
*   **`desktop_app/main.py`**: Application Controller and entry point.

### Test Coverage (`tests/desktop_app/`)
*   **Mocking Strategy**: Heavy reliance on `tests/desktop_app/mock_qt.py` to run headless tests by mocking `PyQt6` modules.
*   **View Tests** (`tests/desktop_app/views/`):
    *   `test_scadenzario_logic.py`: Logic verification for Gantt/Timeline (Fixed Deadlock).
    *   `test_login_view_*.py`: Auth flow and UI state.
    *   `test_import_view_logic.py`: File handling and drag-and-drop.
*   **Integration Tests**:
    *   `test_read_only_sim.py`: Verifies propagation of "Read-Only" state from Backend -> API Client -> UI.
    *   `test_api_client.py`: Headers and Token management.

---

## 3. Conflict Analysis (Backend vs Desktop)

### Authentication & Locking
*   **Mechanism**: Backend (`app/api/routers/auth.py`) attempts to acquire a lock on login. It returns `read_only` (bool) and `lock_owner` (dict) in the Token response.
*   **Desktop Consumption**: `desktop_app/views/login_view.py` reads these fields. `ApplicationController` propagates the `read_only` flag to all views.
*   **Consistency**: Confirmed. `tests/app/core/test_db_security.py` verifies the backend logic, and `tests/desktop_app/test_read_only_sim.py` verifies the frontend reaction.
*   **Minor Note**: Desktop tests mocked `user_info` without `lock_owner`, which is handled safely by `.get()`, but updating the mock data improves realism.

### Licensing
*   **Backend**: `app/core/license_security.py` defines verification logic (crypto).
*   **Desktop**: `desktop_app/services/license_manager.py` implements the client-side check.
*   **Status**: Independent but synchronized via shared config/constants. No conflicts detected.

### Date Handling
*   **Issue Identified**: `DummyQDate` in mocks was causing infinite loops.
*   **Resolution**: Updated `tests/desktop_app/mock_qt.py` to use `datetime.date` and `dateutil.relativedelta` for robust date arithmetic. Tests in `test_scadenzario_logic.py` now pass.
