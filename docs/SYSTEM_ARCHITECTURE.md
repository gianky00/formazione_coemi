# System Architecture & Dependency Graph

## High-Level Architecture

The system follows a **Decoupled Client-Server Architecture** with a **Dual-API** design to separate core business logic from the conversational AI capabilities.

*   **Server**: A headless Python/FastAPI backend responsible for data persistence, business logic, AI processing, and scheduled tasks.
    *   **Core API**: Standard REST endpoints for Certificate/Employee management.
    *   **Chat/RAG API**: Dedicated endpoints for the AI Persona "Lyra" and RAG operations.
*   **Client**: A desktop application built with Python/PyQt6.
*   **Mobile/Web UI**: The `guide_frontend` (React + Vite) serves as both the user manual and the mobile-responsive interface for specific workflows.
*   **External Services**:
    *   **Google Gemini API**: For document analysis and Chat/RAG generation.
    *   **SMTP Server**: For email notifications.
    *   **Edge-TTS**: For high-quality text-to-speech synthesis (Voice Assistant).

```mermaid
graph TD
    subgraph "Desktop Client (PyQt6)"
        UI[User Interface] -->|HTTP Requests| API_Client[API Client Wrapper]
        API_Client -->|REST API| Backend
        UI -->|Embeds| Guide[Mobile UI / Guide (React + QWebEngineView)]
    end

    subgraph "Backend Server (FastAPI)"
        Backend[FastAPI Router]
        Backend --> CoreAPI[Core API Router]
        Backend --> ChatAPI[Chat/RAG API Router]

        CoreAPI --> Services[Service Layer]
        ChatAPI --> RAG[RAG & Persona Engine]

        Services -->|ORM| DB[(In-Memory SQLite)]
        Services -->|Serialize/Encrypt| DiskDB[database_documenti.db]

        RAG --> Gemini[Google Gemini AI]
        RAG --> TTS[Edge-TTS Service]

        Services -->|SMTP| Email[Email Server]
    end
```

## Dependency Graph

### Backend (`app/`)
*   **Entry Point**: `app.main:app` (Lifespan manager, APScheduler init).
*   **Core Dependencies**:
    *   `fastapi`: Web framework (Dual-Router setup).
    *   `sqlalchemy`: ORM for SQLite.
    *   `google-generativeai`: AI Client (Analysis & Chat).
    *   `edge-tts`: Text-to-Speech generation.
    *   `tenacity`: Resilience & Retries.
    *   `pydantic`: Data validation.
    *   `apscheduler`: Background task scheduling.
    *   `fpdf2`: PDF Report generation.
    *   `cryptography`: Database encryption (Fernet).

### Frontend (`desktop_app/`)
*   **Entry Point**: `boot_loader.py` -> `launcher.py` -> `desktop_app.main`.
*   **Core Dependencies**:
    *   `PyQt6`: GUI Framework.
    *   `PyQt6-WebEngine`: Browser engine for `guide_frontend`.
    *   `requests`: HTTP Client.

### Mobile UI / User Guide (`guide_frontend/`)
*   **Framework**: React + Vite.
*   **Styling**: Tailwind CSS v3.
*   **Role**: Provides the "Modern Guide" and responsive mobile views.
*   **Integration**: Compiled to static HTML/JS/CSS (`dist/`) and loaded via `file://` protocol.

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

### 3. Lyra Interaction (Chat & Voice)
1.  **User**: Sends text query via Desktop Chat Widget.
2.  **Chat API**: Receives request at `/api/v1/chat/`.
3.  **RAG Engine**: Retrieves context from `docs/` and Database.
4.  **Generation**: Gemini generates response as "Lyra".
5.  **Voice (Optional)**: If enabled, response text is sent to `edge-tts`. Audio bytes are returned to Client.

### 4. Boot Process (Reliability)
1.  **Executable**: Starts `boot_loader.py`.
2.  **Safety Check**: Imports `launcher.py` inside a `try/except` block.
3.  **Health Check**: The launcher calls `/api/v1/health`.
    *   **Resilience**: If DB is locked or corrupted, Backend enters "Recovery Mode" (non-fatal).
    *   **UI**: Displays appropriate warnings/recovery options instead of crashing.
4.  **Failure Handling**: `boot_loader` catches hard crashes (DLLs) and shows a native Windows Message Box.

## 🤖 AI Metadata (RAG Context)
```json
{
  "type": "architecture_documentation",
  "domain": "system_design",
  "key_components": [
    "FastAPI Backend",
    "PyQt6 Desktop Client",
    "React Mobile UI",
    "Dual-API (Core + Chat)",
    "In-Memory Database",
    "Google Gemini",
    "Edge-TTS"
  ],
  "architecture_style": "Decoupled Client-Server",
  "critical_paths": [
    "Data Ingestion",
    "Notification Dispatch",
    "Lyra RAG/Voice Pipeline",
    "Secure Boot"
  ]
}
```
