# Business Logic & Domain Rules

## Certificate Lifecycle

1.  **Ingestion**: A PDF is uploaded via `POST /upload-pdf/` (temporarily) or processed directly in the frontend.
2.  **Extraction**: The AI extracts data (Name, Date, Category).
3.  **Creation (`ValidationStatus.AUTOMATIC`)**:
    *   A certificate is created via `POST /certificati/`.
    *   **Get-or-Create**: The system attempts to link it to an existing `Dipendente` (Employee) using `nome` and `data_nascita`.
    *   **Orphan State**: If no employee matches, `dipendente_id` is `NULL`. The raw name/date are stored in `nome_dipendente_raw`/`data_nascita_raw`.
4.  **Validation (`ValidationStatus.MANUAL`)**:
    *   User reviews the data in "Convalida Dati".
    *   User confirms validity via `PUT /certificati/{id}/valida`.
    *   **Resolution**: If the certificate was an orphan, the user must manually select an employee during this phase.
5.  **Active Lifecycle**: The certificate is now visible in the Dashboard and subject to expiration monitoring.

## Certificate Status Logic (`app/services/certificate_logic.py`)

Status is **calculated dynamically**, not stored in the database.

*   **`attivo` (Active)**: `data_scadenza_calcolata` > Today + Threshold.
*   **`in_scadenza` (Expiring)**: Today <= `data_scadenza_calcolata` <= Today + Threshold.
    *   *Thresholds*: 30 days for "VISITA MEDICA", 60 days for everything else.
*   **`scaduto` (Expired)**: `data_scadenza_calcolata` < Today.
    *   **Orphans**: An orphan certificate is *always* "scaduto" if past its date.
*   **`rinnovato` (Renewed)**:
    *   Condition: The certificate is expired, BUT a *newer* certificate exists for the *same employee* and *same course category*.
    *   *Implication*: "Rinnovato" certificates are historically preserved but don't trigger alerts.

## Course Validity Rules

Validity is defined in `app/db/seeding.py`. Categories with `validita_mesi = 0` have their expiration extracted from the document.

| Category | Validity (Months) | Notes |
| :--- | :--- | :--- |
| **ANTINCENDIO** | 60 | |
| **PRIMO SOCCORSO** | 36 | |
| **PREPOSTO** | 24 | |
| **BLSD** | 12 | |
| **VISITA MEDICA** | 0 | Scadenza from "Da rivedere entro..." |
| **UNILAV** | 0 | Scadenza from "Data Fine" |
| **PATENTE** | 0 | Scadenza from "4b" |
| **CARTA DI IDENTITA** | 0 | Scadenza from "Scadenza" |
| **NOMINE** | 0 | No expiration (Active) |
| **MODULO RECESSO...** | 0 | No expiration |
| **HLO** | 0 | No expiration |
| **TESSERA HLO** | 0 | Scadenza extracted |
| *(Most Others)* | 60 | Default 5 years |

## File System & Organization

The frontend (`ImportView`) enforces a strict directory structure for processed files:

`DOCUMENTI DIPENDENTI / {Cognome Nome} ({Matricola}) / {Categoria} / {Stato} / {Filename}.pdf`

*   **Stato Folders**:
    *   `ATTIVO`: If expiration is in the future or null.
    *   `STORICO`: If expiration is in the past.
*   **Fallback Folders**:
    *   `PDF ANALIZZATI`: (Legacy/Backup)
    *   `NON ANALIZZATI`: Files that failed processing or require manual intervention.

## Homonym Resolution

The system uses `nome`, `cognome`, and `data_nascita` to resolve identities.
*   If two employees have the same name, `data_nascita` is the tie-breaker.
*   If the AI fails to extract `data_nascita`, the system may flag the certificate as an orphan if the name alone is ambiguous.
