# Critical System Flows

## 1. Certificate Ingestion & Creation
**Goal**: Convert a raw PDF into a persisted, normalized database record.

1.  **User Action**: Drag & Drop PDF in `ImportView`.
2.  **API Call**: `POST /upload-pdf/` with file bytes.
3.  **AI Processing** (`app.services.ai_extraction.extract_entities_with_ai`):
    *   **Model**: Google Gemini 2.5 Pro (Hardcoded).
    *   **Resilience**: Uses `tenacity` for exponential backoff on `ResourceExhausted` (429) errors.
    *   **Logic**: Single-pass extraction + classification.
    *   **Absolute Rules**:
        *   "NOMINA..." -> **NOMINA** (Not PREPOSTO).
        *   "Giudizio di idoneità..." -> **VISITA MEDICA**.
        *   "UNILAV..." -> **UNILAV** (Expiry: "Data Fine").
        *   "Patente..." -> **PATENTE** (Expiry: "4b").
        *   "Carta d'Identità..." -> **CARTA DI IDENTITA** (Expiry: "Scadenza").
        *   "ATEX..." -> **ATEX**.
        *   "HLO" (Course) vs "TESSERA HLO" (Card).
    *   **Output**: JSON with normalized fields.
4.  **Date Normalization**: API converts `DD-MM-YYYY` -> `DD/MM/YYYY`.
5.  **Persistence**: `POST /certificati/`.
    *   **Identity Resolution**: `matcher.find_employee_by_name`.
        *   *Match*: Links to `Dipendente` (checks Name + DOB).
        *   *No Match*: Sets `dipendente_id=NULL`, saves `nome_dipendente_raw`.
    *   **Validation Status**: `AUTOMATIC`.
6.  **File Organization** (Frontend `ImportView`):
    *   Moves file to: `DOCUMENTI DIPENDENTI / {Name} ({Matricola}) / {Category} / {Status} / {File}.pdf`.
    *   *Status Folder*: `ATTIVO` (Future/No expiry) vs `STORICO` (Past).

## 2. License Auto-Update Flow
**Goal**: Automatically renew licenses from a remote source without user intervention.
*See [System Design Report](SYSTEM_DESIGN_REPORT.md) for cryptographic details.*

1.  **Trigger**: Startup Gatekeeper detects `EXPIRED`, `MISSING`, or `TAMPERED` state.
2.  **Config Fetch**: Application retrieves `HardwareID` and GitHub Credentials.
3.  **Manifest Check**:
    *   Downloads `manifest.json` from GitHub (`/licenses/{HWID}/`).
    *   Compares SHA256 hashes with local files.
4.  **Atomic Update**:
    *   Downloads new `pyarmor.rkey` and `config.dat` to `TempDir`.
    *   Verifies SHA256 of downloaded files.
    *   **Atomic Move**: Replaces files in `%LOCALAPPDATA%/Intelleo/Licenza/`.
5.  **Restart**: Application restarts to load the new license.

## 3. Secure Boot & Time Validation
**Goal**: Prevent tampering (e.g., system clock rollback) and ensure environment integrity.

1.  **Gatekeeper**: `launcher.py` starts before UI.
2.  **Time Check** (`time_service.py`):
    *   **Online**: Queries `pool.ntp.org`. if `|Sys - NTP| > 5 min` -> **BLOCK**.
    *   **Offline**: Checks `secure_time.dat` (Encrypted).
        *   If `SysTime < LastExecution` -> **BLOCK (Rollback Detected)**.
        *   If `SysTime > LastOnline + 3 Days` -> **BLOCK (Buffer Expired)**.
3.  **Discovery**:
    *   Scans for License in User Data -> Install Dir.
    *   Scans for Database. If missing -> **Recovery Dialog**.

## 4. Certificate Lifecycle & Status Logic
**Goal**: Dynamically calculate the status of a certificate for the UI and Alerts.
*Logic Location*: `app.services.certificate_logic.get_certificate_status`

| Status | Condition |
| :--- | :--- |
| **attivo** | `data_scadenza` > Today + Threshold |
| **in_scadenza** | Today <= `data_scadenza` <= Today + Threshold |
| **scaduto** | `data_scadenza` < Today |
| **rinnovato** | Expired, BUT a newer certificate exists for same Employee + Category. |

*   **Thresholds**: 30 days (VISITA MEDICA), 60 days (Others).
*   **Orphans**: Cannot be "rinnovato". If expired, they remain "scaduto".

## 5. Notification System Logic
**Goal**: Alert admins about expiring or overdue certificates via Email.

1.  **Trigger**: Daily Schedule (APScheduler, 08:00) or Manual (`POST /send-manual-alert`).
2.  **Data Collection**:
    *   Queries all certificates.
    *   Filters using the Status Logic (above).
3.  **Report Generation**:
    *   `generate_pdf_report_in_memory` (FPDF).
    *   Generates tables for: "In Avvicinamento (Corsi)", "In Avvicinamento (Visite)", "Scaduti non rinnovati".
4.  **Transmission**:
    *   Protocol Auto-detection:
        *   Port **465**: `SMTP_SSL`.
        *   Port **587/25**: `SMTP` + `STARTTLS`.
    *   Sends to `EMAIL_RECIPIENTS_TO`.

## 6. Orphan Re-linking Flow
**Goal**: Assign unlinked certificates to employees after a CSV import.

1.  **Action**: Admin uploads CSV via `POST /dipendenti/import-csv`.
2.  **Upsert**: Updates `Dipendente` table (Key: `matricola`).
3.  **Scan**: Finds all `Certificato` where `dipendente_id IS NULL`.
4.  **Match**:
    *   Uses stored `nome_dipendente_raw`.
    *   If a match is found in the updated registry -> Links `dipendente_id`.
5.  **Result**: Certificates become "Assigned" and visible in the main Dashboard.

## 7. Database Security & Resilience
**Goal**: Ensure encryption-at-rest and robust recovery from locks/crashes.

1.  **Architecture**: **Strict In-Memory**.
    *   Disk File: `database_documenti.db` (Always Encrypted with Fernet).
    *   Runtime: Decrypted into RAM (`sqlite3.deserialize`).
    *   **No plain-text data is ever written to disk** (unless explicitly unlocked by admin).

2.  **Startup Resilience**:
    *   **Lock Check**: Attempts to acquire OS-level lock.
        *   *If Locked*: Starts in **Read-Only Mode**. UI warns user.
    *   **Corruption Check**: If decryption fails, starts in **Recovery Mode**.
    *   **Backend**: Does NOT crash on DB errors; allows UI to load and guide user.

3.  **Persistence**:
    *   **Atomic Write**: `serialize` -> `encrypt` -> `write to temp` -> `replace`.
    *   **Cleanup**: `atexit` handlers ensure lock release on shutdown.

## 8. Lyra RAG & Voice Pipeline
**Goal**: Provide context-aware answers and vocal interaction.

1.  **Input**: User types in Chat Widget.
2.  **Context Retrieval (RAG)**:
    *   System searches `docs/` (Architecture, Flows, Models).
    *   System queries `Database` (Employee stats, Certificate counts).
3.  **Persona Injection**:
    *   Injects `LYRA_PROFILE.md` context (Tone: Professional, Empathetic, Sicilian).
4.  **Generation**: Gemini 2.5 Pro generates text response.
5.  **Voice Synthesis (Edge-TTS)**:
    *   If "Voice" enabled: Text -> `edge-tts` -> MP3.
    *   Audio played immediately in client.

## 🤖 AI Metadata (RAG Context)
```json
{
  "type": "process_documentation",
  "domain": "business_logic",
  "workflows": [
    "Certificate Ingestion",
    "Status Calculation",
    "Notification Dispatch",
    "Identity Resolution",
    "Database Security",
    "Lyra Interaction"
  ],
  "key_mechanisms": [
    "Gemini AI Extraction",
    "Tenacity Retry",
    "In-Memory Database",
    "Edge-TTS",
    "RAG"
  ]
}
```
