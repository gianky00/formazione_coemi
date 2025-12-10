# API Reference Documentation

Documentazione tecnica dettagliata degli endpoint REST esposti dal Backend FastAPI.

**Base URL**: `http://localhost:{port}/api/v1`
**Autenticazione**: Bearer Token (JWT) nell'header `Authorization`.

---

## 1. Authentication (`/auth`)

### `POST /auth/login`
Autentica l'utente e restituisce il Token di accesso.
*   **Request (`OAuth2PasswordRequestForm`)**: `username`, `password`.
*   **Response**:
    ```json
    {
      "access_token": "jwt_token_string",
      "token_type": "bearer",
      "user_info": { "id": 1, "username": "admin", "is_admin": true },
      "read_only": false, // True se DB è bloccato
      "lock_owner": null  // Dettagli processo bloccante se read_only=true
    }
    ```

### `POST /auth/logout`
Invalida la sessione corrente (Blacklist Token) e rilascia il Lock sul DB.

---

## 2. Certificati (`/certificati`)

### `POST /certificati/upload-pdf/`
Analizza un file PDF utilizzando l'AI.
*   **Request**: `file` (Multipart/form-data).
*   **Response**: JSON con entità estratte (Nome, Data, Corso, Scadenza).

### `GET /certificati/`
Recupera la lista dei certificati.
*   **Query Params**:
    *   `skip` (int): Offset paginazione.
    *   `limit` (int): Limite risultati.
    *   `validated` (bool): Filtra per stato (`true`=Validati, `false`=Da Convalidare).
*   **Response**: Lista di `CertificatoSchema`.

### `POST /certificati/`
Crea un nuovo certificato (conferma validazione).
*   **Body (`CertificatoCreazioneSchema`)**:
    *   `nome`, `corso`, `categoria`, `data_rilascio` (Required).
    *   `data_scadenza` (Optional).
*   **Logic**:
    *   Tenta il linking automatico con `Dipendente` via `matcher.py`.
    *   Imposta `stato_validazione = MANUAL`.

### `PUT /certificati/{id}`
Aggiorna un certificato esistente.
*   **Body (`CertificatoAggiornamentoSchema`)**: Tutti i campi opzionali.
*   **Logic**: Ricalcola lo stato (`attivo`/`scaduto`) in base alle nuove date.

### `DELETE /certificati/{id}`
Elimina un certificato (Logico o Fisico, dipendente dall'implementazione).

---

## 3. Dipendenti (`/dipendenti`)

### `GET /dipendenti/`
Lista dipendenti con filtri opzionali.

### `POST /dipendenti/import-csv`
Importa o aggiorna anagrafica da CSV.
*   **Request**: `file` (CSV).
*   **Logic**:
    *   Encoding detection (UTF-8, Latin-1, CP1252).
    *   Upsert (Aggiorna esistenti, crea nuovi).
    *   Trigger "Orphan Linking": Cerca certificati orfani e li associa ai nuovi dipendenti.

---

## 4. Configurazioni (`/app_config`)

### `GET /app_config/config`
Recupera le impostazioni mutabili (`settings.json`).
*   **Auth**: Richiede privilegi Admin.

### `PUT /app_config/config`
Aggiorna le impostazioni.
*   **Body**: JSON parziale con chiavi da aggiornare.
*   **Security**: Oscura automaticamente chiavi sensibili (API Key) prima del salvataggio.

### `GET /app_config/config/updater`
Recupera configurazione per Auto-Update (GitHub Token).
*   **Auth**: Pubblico (per permettere recovery pre-login).

---

## 5. Notifiche (`/notifications`)

### `POST /notifications/send-manual-alert`
Trigger manuale per l'invio delle email di scadenza.
*   **Logic**: Genera report PDF e invia a destinatari configurati.

---

## 6. System & Health (`/health`, `/system`)

### `GET /health`
Endpoint di monitoraggio.
*   **Response**:
    ```json
    {
      "status": "ok" | "maintenance_mode",
      "database": "connected" | "locked" | "missing",
      "version": "1.0.0"
    }
    ```

### `POST /system/db-security/toggle`
Blocca/Sblocca il database (Admin only).
*   **Body**: `{"action": "lock" | "unlock"}`.
