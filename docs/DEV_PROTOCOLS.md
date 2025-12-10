# Protocolli di Sviluppo (Dev Protocols)

Standard mandatori per contribuire al repository `intelleo`.

## 1. Principi Architetturali

### 1.1 Zero-Trust Local
*   **Assunto**: L'utente ha accesso fisico alla macchina e può tentare di leggere/modificare file.
*   **Regola**: MAI salvare dati sensibili (password, token, PII) in chiaro su disco.
*   **Implementazione**: Usa sempre `DBSecurityManager` per il DB e `Fernet` per i file di configurazione.

### 1.2 In-Memory First
*   Il database deve esistere su disco SOLO come blob cifrato.
*   A runtime, deve vivere SOLO in RAM (`sqlite3.deserialize`).

### 1.3 Separazione di Responsabilità
*   **Backend**: Logica pura, Stato, Sicurezza. Non deve sapere nulla della GUI.
*   **Frontend**: Presentazione. Non deve accedere al DB direttamente (solo via API).

## 2. Standard di Codice

### 2.1 Lingua
*   **Codice (Variabili, Funzioni, Commenti)**: INGLESE (`def get_certificate_status():`).
*   **Interfaccia Utente (Label, Messaggi, Errori)**: ITALIANO (`"Errore di connessione"`).
*   **Terminologia Business**:
    *   `Dipendente` (DB/Code) -> **DIPENDENTE** (UI).
    *   `Certificato` (DB/Code) -> **DOCUMENTO** (UI).
    *   `Corso` (DB/Code) -> **TIPO DOCUMENTO** (UI).

### 2.2 Style Guide
*   **Python**: PEP 8.
    *   Max Line Length: 120 char.
    *   Imports: Raggruppati (Stdlib, Third-party, Local).
*   **Naming**:
    *   Classi: `PascalCase` (`LicenseManager`).
    *   Funzioni/Variabili: `snake_case` (`calculate_expiry`).
    *   Costanti: `UPPER_CASE` (`DEFAULT_TIMEOUT`).

## 3. Workflow Git

### 3.1 Branching
*   `main`: Produzione stabile.
*   `feat/nome-feature`: Sviluppo nuove funzionalità.
*   `fix/descrizione-bug`: Correzioni.

### 3.2 Commit Messages
Formato: `type: Subject`
*   `feat`: Nuova funzionalità.
*   `fix`: Correzione bug.
*   `docs`: Documentazione.
*   `refactor`: Modifiche al codice senza cambio comportamento.
*   `test`: Aggiunta/Modifica test.

*Esempio*: `feat: Add robust CSV encoding detection logic`

## 4. Gestione Errori

*   **Catch-All**: Vietato `except Exception:` nudo senza logging o re-raise, tranne nel `boot_loader` (Pokemon Exception Handling per stabilità).
*   **UI Feedback**: Ogni errore API deve essere mostrato all'utente via `Toast` o `Dialog` in italiano amichevole (es. "Impossibile contattare il server" non "ConnectionRefusedError").

## 5. Asset & Multimedia
*   **Audio**: Evitare file `.mp3` o `.wav` statici pesanti. Usare `SoundManager` per sintesi procedurale (WAV in-memory) o TTS dinamico.
*   **Grafica 3D**: Usare engine vettoriali (`numpy`/`QPainter`) invece di asset 3D pre-renderizzati o video pesanti.

## 6. Analisi Statica & Security
*   **SonarCloud**: Il codice deve passare i gate di qualità (0 Vulnerabilità, Coverage > 80%).
*   **Secrets**: Nessun segreto hardcoded (usa variabili d'ambiente o offuscamento XOR per chiavi statiche).
