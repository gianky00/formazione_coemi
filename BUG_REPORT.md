# Critical Bug Report

This report outlines critical issues identified in the codebase that jeopardize system stability, data integrity, and security.

## 1. Race Condition in Certificate Creation
*   **File/Line:** `app/api/main.py` (Lines ~136-158 in `create_certificato`)
*   **Severity:** **High**.
*   **Description:** The system performs a "check-then-act" sequence: it queries the database for an existing certificate and, if none is found, inserts a new one. In a concurrent environment (e.g., rapid parallel uploads), two requests can pass the check simultaneously, causing duplicate certificates to be created. This violates data integrity rules.
*   **Proposed Fix:** Enforce uniqueness at the database level by adding a `UniqueConstraint` on `(dipendente_id, corso_id, data_rilascio)` in the `Certificato` model. Handle `IntegrityError` in the API to return a 409 Conflict.

## 2. Homonym Resolution Failure
*   **File/Line:** `app/services/matcher.py` (Lines ~6-38) and `app/api/main.py`.
*   **Severity:** **Critical**.
*   **Description:** The `find_employee_by_name` function ignores the `data_nascita` field, relying solely on the name. This makes it impossible to distinguish between two employees with the same name (homonyms), leading to incorrect certificate assignment (e.g., assigning a certificate to the wrong "Mario Rossi").
*   **Proposed Fix:** Update the matcher to accept `data_nascita` as a secondary filter. If multiple employees match the name, use the birth date to identify the correct one.

## 3. Fragile CSV Import (Encoding & Integrity)
*   **File/Line:** `app/api/main.py` (Line ~362 in `import_dipendenti_csv`)
*   **Severity:** **High**.
*   **Description:** The code blindly decodes uploaded CSV files as UTF-8. If a user uploads a file encoded in Windows-1252 (common in Italy/Excel), the application will crash or corrupt special characters. Additionally, there is no file size limit, exposing the server to DoS attacks.
*   **Proposed Fix:** Implement robust encoding detection (try UTF-8, fallback to Latin-1/CP1252). Enforce a 5MB file size limit.

## 4. Unbounded PDF Uploads (DoS Risk)
*   **File/Line:** `app/api/main.py` (Line ~30 in `upload_pdf`)
*   **Severity:** **High**.
*   **Description:** The `upload_pdf` endpoint reads the entire file into memory without checking its size. A malicious or accidental upload of a very large file (e.g., hundreds of MBs) can exhaust server memory and crash the application.
*   **Proposed Fix:** Enforce a strict 20MB limit for PDF uploads and reject larger files immediately.

## 5. Fragile Date Parsing in AI Extraction
*   **File/Line:** `app/api/main.py` (Lines ~39-47 in `upload_pdf`)
*   **Severity:** **Medium**.
*   **Description:** If the AI extracts a date in an unexpected format, the system catches the `ValueError` and simply `pass`es, leaving the date empty. This can result in valid certificates being imported without expiration dates, requiring manual correction.
*   **Proposed Fix:** Implement a flexible date parser that attempts to handle multiple common formats (`DD/MM/YYYY`, `YYYY-MM-DD`, `DD-MM-YY`, etc.) before giving up.
