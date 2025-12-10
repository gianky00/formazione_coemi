# Architettura di Sistema e Grafico delle Dipendenze

Questo documento definisce l'architettura tecnica ad alto livello di **Intelleo**, descrivendo i componenti, le interazioni e i flussi dati critici.

## 1. Architettura High-Level

Il sistema adotta un'architettura **Client-Server Decoppiata Local-Hosted**, dove Frontend e Backend sono processi distinti che comunicano via HTTP su `localhost`, ma sono distribuiti come un unico pacchetto monolitico.

### Componenti Principali
*   **Backend Server (Processo A)**: Applicazione Python/FastAPI "Headless".
    *   **Ruolo**: Gestisce persistenza dati (SQLite In-Memory), logica di business, integrazione AI (Gemini), Scheduling e Sicurezza.
    *   **Porta**: Dinamica (range 8000-8010).
*   **Desktop Client (Processo B)**: Applicazione Python/PyQt6.
    *   **Ruolo**: Interfaccia utente, gestione stato sessione, rendering grafici (Gantt), Bridge React.
*   **Mobile/Guide UI (Embedded)**: Single Page Application (SPA) React + Vite.
    *   **Ruolo**: Manuale utente interattivo e moduli responsive.
    *   **Integrazione**: Renderizzata via `QWebEngineView` e comunicante tramite `QWebChannel`.

```mermaid
graph TD
    subgraph "Host Locale (Windows PC)"
        Launcher[Launcher.py (Process Controller)]

        Launcher -->|Spawns| Backend[Backend Process (FastAPI)]
        Launcher -->|Spawns| Frontend[Frontend Process (PyQt6)]

        Frontend -->|HTTP REST + JWT| Backend

        subgraph "Backend Space"
            API[API Routers]
            Services[Service Layer]
            DB[(In-Memory Encrypted SQLite)]
            AI_Client[Gemini Client]

            Backend --> API
            API --> Services
            Services --> DB
            Services --> AI_Client
        end

        subgraph "Frontend Space"
            Views[PyQt Views]
            React[React App (QWebEngine)]
            Bridge[QWebChannel JS Bridge]

            Views -->|Embeds| React
            React <-->|JSON RPC| Bridge <--> Views
        end
    end

    Cloud[Google Gemini API]
    Github[GitHub License Repo]
    SMTP[SMTP Mail Server]

    AI_Client -->|HTTPS| Cloud
    Services -->|HTTPS| Github
    Services -->|SMTP/S| SMTP
```

## 2. Dettaglio Componenti e Dipendenze

### Backend (`app/`)
*   **Entry Point**: `app.main:app`. Utilizza `lifespan` context manager per inizializzare `DBSecurityManager` (Load DB) e `APScheduler` (Start Jobs).
*   **Stack Tecnologico**:
    *   **Web Framework**: `fastapi`, `uvicorn` (Server ASGI).
    *   **ORM**: `sqlalchemy` (con `StaticPool` per SQLite in-memory).
    *   **AI**: `google-generativeai` (Gemini SDK), `tenacity` (Retry logic).
    *   **Sicurezza**: `cryptography` (Fernet Encryption), `python-jose` (JWT), `bcrypt` (Hashing).
    *   **Utilities**: `fpdf2` (PDF Gen), `apscheduler` (Cron jobs), `geoip2` (Location).

### Frontend Desktop (`desktop_app/`)
*   **Entry Point**: `boot_loader.py` -> `launcher.py` -> `desktop_app.main`.
*   **Stack Tecnologico**:
    *   **GUI**: `PyQt6` (Core, Widgets, Gui).
    *   **Web Engine**: `PyQt6-WebEngine` (Chromium embedding), `PyQt6-WebChannel` (JS Bridge).
    *   **Network**: `requests` (API Client sincrono), `urllib3`.
    *   **System**: `wmi` (Hardware ID Windows), `pywin32` (OS Integration).
    *   **Multimedia**:
        *   `Neural3D`: Engine particellare vettoriale custom (`numpy`) per visualizzazioni 3D.
        *   `SoundManager`: Sintetizzatore audio real-time (WAV generator) e bridge `edge-tts`.

### Guide Frontend (`guide_frontend/`)
*   **Stack Tecnologico**: `React 18`, `Vite` (Build Tool), `Tailwind CSS 3` (Styling), `Framer Motion` (Animations), `Lucide React` (Icons).
*   **Build Artifact**: File statici (`index.html`, `assets/*.js`, `assets/*.css`) in `guide_frontend/dist/`.

## 3. Flussi di Interazione Critici

### 3.1 Boot Sequence (Reliability & Security)
1.  **Boot Loader**: `boot_loader.py` avvia `launcher.py` in un blocco `try/except` "Pokemon" (Catch-All) per catturare errori di importazione DLL (comuni su Windows).
2.  **License Gatekeeper**: `launcher.py` verifica la validità della licenza e l'integrità del sistema (`integrity_service`).
    *   *Se Fail*: Tenta Auto-Update (Headless). Se fallisce ancora -> Exit.
3.  **Port Discovery**: Scansiona porte 8000-8010 per trovare una porta libera.
4.  **Backend Spawn**: Avvia il backend su thread separato (`uvicorn.run`).
5.  **Health Check**: Polling su `/api/v1/health`.
    *   *Se DB Lock*: Backend parte in "Recovery Mode". Launcher avvia UI ma notifica "Read Only".
    *   *Se DB Missing*: Backend OK, Launcher mostra "Database Recovery Dialog".
6.  **UI Launch**: Avvia `QApplication` e `LoginView`.

### 3.2 AI Data Ingestion Pipeline
1.  **Upload**: Utente trascina PDF -> Frontend invia bytes a `POST /upload-pdf/`.
2.  **Processing (Backend)**:
    *   `ai_extraction.py` costruisce prompt con regole di business (es. "NOMINA" vs "PREPOSTO").
    *   Invia a Gemini 2.5 Pro.
    *   Riceve JSON.
3.  **Normalization**: Backend normalizza date (`DD/MM/YYYY`) e nomi (`Title Case`).
4.  **Presentation**: Frontend riceve JSON e popola `ImportView`.

### 3.3 React-PyQt Bridge (Modern Guide)
1.  **Init**: `ModernGuideView` (PyQt) carica `index.html` da `dist/`.
2.  **Registration**: Backend registra oggetto `GuideBridge` su `QWebChannel`.
3.  **Frontend Hook**: React usa `useEffect` per inizializzare `new QWebChannel(qt.webChannelTransport)`.
4.  **Communication**:
    *   React chiama `bridge.close_guide()` -> PyQt esegue slot `close_guide()`.
    *   PyQt può iniettare JS via `runJavaScript()`.

## 4. Sottosistema di Sicurezza & Licenze
*Per dettagli completi, vedere [System Design Report](SYSTEM_DESIGN_REPORT.md).*

Il sistema impiega un'architettura **"Zero-Trust Local"**:
*   **Storage**: DB sempre cifrato su disco (AES-128). Decifrato solo in RAM.
*   **Licensing**: Bind Hardware (Disk Serial) + Configurazione Cifrata.
*   **Anti-Tamper**: Validazione temporale NTP + SHA256 Manifest Check.
*   **Updates**: Aggiornamento atomico delle licenze via GitHub CDN privato.

## 🤖 AI Metadata (RAG Context)
```json
{
  "type": "architecture_documentation",
  "domain": "system_design",
  "key_components": [
    "FastAPI Backend",
    "PyQt6 Desktop Client",
    "React Mobile UI",
    "In-Memory Database",
    "Gemini AI",
    "QWebChannel Bridge"
  ],
  "architecture_style": "Decoupled Local Client-Server",
  "critical_paths": [
    "Boot Sequence",
    "AI Ingestion",
    "React Bridge",
    "License Gatekeeper"
  ]
}
```
