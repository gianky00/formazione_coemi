# System Architecture & Dependency Graph

## High-Level Architecture

The system follows a **Decoupled Client-Server Architecture**.

*   **Server**: A headless Python/FastAPI backend responsible for data persistence, business logic, AI processing, and scheduled tasks.
*   **Client**: A desktop application built with Python/PyQt6, communicating with the server exclusively via HTTP REST APIs.
*   **User Guide**: A dedicated React single-page application embedded within the desktop client.
*   **External Services**:
    *   **Google Gemini API**: For document analysis.
    *   **SMTP Server**: For email notifications (supports SSL and STARTTLS).

```mermaid
graph TD
    subgraph "Desktop Client (PyQt6)"
        UI[User Interface] -->|HTTP Requests| API_Client[API Client Wrapper]
        API_Client -->|REST API| Backend
        UI -->|Embeds| Guide[Modern Guide (React + QWebEngineView)]
    end

    subgraph "Backend Server (FastAPI)"
        Backend[FastAPI Router] --> Services[Service Layer]
        Services -->|ORM| DB[(In-Memory SQLite)]
        Services -->|Serialize/Encrypt| DiskDB[database_documenti.db]
        Services -->|Generate| Gemini[Google Gemini AI]
        Services -->|SMTP| Email[Email Server]
    end
```

## Dependency Graph

### Backend (`app/`)
*   **Entry Point**: `app.main:app` (Lifespan manager, APScheduler init).
*   **Core Dependencies**:
    *   `fastapi`: Web framework.
    *   `sqlalchemy`: ORM for SQLite.
    *   `google-generativeai`: AI Client.
    *   `pydantic`: Data validation.
    *   `apscheduler`: Background task scheduling.
    *   `fpdf2`: PDF Report generation.
    *   `cryptography`: Database encryption (Fernet).

### Frontend (`desktop_app/`)
*   **Entry Point**: `boot_loader.py` -> `launcher.py` -> `desktop_app.main`.
*   **Core Dependencies**:
    *   `PyQt6`: GUI Framework.
    *   `PyQt6-WebEngine`: Browser engine for User Guide.
    *   `requests`: HTTP Client.

### User Guide (`guide_frontend/`)
*   **Framework**: React + Vite.
*   **Styling**: Tailwind CSS v3.
*   **Integration**: Compiled to static HTML/JS/CSS (`dist/`) and loaded via `file://` protocol in `QWebEngineView`.

## Component Interaction

### 1. Data Ingestion (AI Pipeline)
1.  **Client**: Sends PDF bytes to `POST /upload-pdf/`.
2.  **Backend (`ai_extraction.py`)**:
    *   Calls Google Gemini `models/gemini-2.5-pro`.
    *   Prompt enforces "Single-Pass" extraction and classification.
3.  **Response**: JSON with extracted entities.
4.  **Client**: Displays data in "Import View".

### 2. Notification System
1.  **Trigger**: Scheduled job (APScheduler) or Manual API Call (`POST /send-manual-alert`).
2.  **Service (`notification_service.py`)**:
    *   Queries `Certificato` where `data_scadenza_calcolata` is within threshold.
    *   **PDF Generation**: Uses `fpdf2` to create an in-memory PDF report.
    *   **Email Dispatch**: Connects via `smtplib` (auto-detects SSL vs STARTTLS).

### 3. Validation Workflow
1.  **Status**: Certificates start with `stato_validazione='AUTOMATIC'`.
2.  **Client**: Fetches these via `GET /certificati/?validated=false`.
3.  **Action**: User validates -> `PUT /certificati/{id}/valida` -> Status becomes `MANUAL`.
4.  **Visibility**: Only `MANUAL` certificates appear in the main Dashboard.

### 4. Boot Process (Reliability)
1.  **Executable**: Starts `boot_loader.py`.
2.  **Safety Check**: Imports `launcher.py` inside a `try/except` block.
3.  **Failure Handling**: If missing DLLs or imports cause a crash, `boot_loader` catches it and displays a native Windows Message Box with the error, preventing "silent crashes".
