# Project Overview & Architecture

## Directory Structure

The repository follows a clear separation of concerns between the backend (FastAPI) and the frontend (PyQt6).

```
.
├── app/                        # FastAPI Backend
│   ├── api/                    # API Endpoints (main.py, notifications.py)
│   ├── core/                   # Configuration (config.py, constants.py)
│   ├── db/                     # Database Layer (models.py, session.py, seeding.py)
│   ├── services/               # Business Logic (ai_extraction.py, certificate_logic.py, notification_service.py)
├── desktop_app/                # PyQt6 Frontend
│   ├── assets/                 # Images and resources (logo.png)
│   ├── icons/                  # SVG icons
│   ├── view_models/            # ViewModels for MVVM pattern (dashboard_view_model.py)
│   ├── views/                  # UI Components (import_view.py, validation_view.py, etc.)
│   ├── api_client.py           # Centralized API Client
│   ├── main.py                 # Application entry point
│   └── main_window_ui.py       # Main Window layout
├── tests/                      # Test Suite (mirrors app/ structure)
├── AGENTS.md                   # Quick start guide for AI agents
├── requirements.txt            # Python dependencies
├── run.sh / avvio.bat          # Launch scripts
```

## Architectural Patterns

### Backend (Layered Architecture)
1.  **API Layer (`app/api/`)**: Handles HTTP requests/responses. Thin layer, delegates logic to services.
    *   **Dependency Injection**: Uses `Depends(get_db)` for session management.
2.  **Service Layer (`app/services/`)**: Contains the core business logic.
    *   `certificate_logic.py`: Domain logic for expirations and status.
    *   `ai_extraction.py`: Integration with Google Gemini.
    *   `notification_service.py`: Email generation and sending.
3.  **Data Access Layer (`app/db/`)**: SQLAlchemy models and session management.
    *   **Pydantic Schemas**: Used for data validation and serialization (DTOs).

### Frontend (MVVM & Event-Driven)
The PyQt6 application is transitioning towards the **Model-View-ViewModel (MVVM)** pattern to improve testability.
*   **Views (`desktop_app/views/`)**: Handle UI rendering and user input. They should ideally contain *no business logic*.
*   **ViewModels (`desktop_app/view_models/`)**: Manage the state of the view, handle API calls via `APIClient`, and expose data to the View.
    *   *Example*: `DashboardViewModel` manages the data for `DashboardView`.
*   **API Client (`desktop_app/api_client.py`)**: A singleton-like client that abstracts all HTTP calls to the backend.
*   **Navigation**: Managed by `QStackedWidget` in `MainWindow`. Views are lazy-loaded or refreshed via the `on_view_change` slot mechanism.

## Key Design Decisions

*   **No Database Migrations**: The project uses `Base.metadata.create_all()`. Schema changes require deleting `scadenzario.db`.
*   **Settings**: Managed via `pydantic-settings` in `app/core/config.py`, loading from `.env`.
*   **AI Integration**: The AI service is stateless. It receives raw bytes and returns extracted data.
*   **File Organization**: The frontend enforces a strict folder structure for processed PDFs (`DOCUMENTI DIPENDENTI/Employee/Category/Status/`).
