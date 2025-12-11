# Contribuire a Intelleo

Grazie per l'interesse nel contribuire a Intelleo. Per garantire la stabilità e la sicurezza di questo software critico, tutti i contributi devono aderire ai seguenti protocolli.

## 1. Principi Architetturali

### Zero-Trust Local
*   **Assunto**: L'utente ha accesso fisico alla macchina e può tentare di manipolare file o memoria.
*   **Regola**: MAI salvare dati sensibili (password, token, PII) in chiaro su disco.
*   **Implementazione**: Usa sempre `DBSecurityManager` (Encryption-at-Rest) e `app.core.string_obfuscation` per secret statici.

### In-Memory First
*   Il database vive su disco solo come blob cifrato (AES-128).
*   A runtime, deve essere caricato esclusivamente in RAM (`:memory:`).

## 2. Standard di Codice

### Lingua
*   **Codice**: INGLESE (Variabili, Funzioni, Commenti Interni).
*   **UI (Label, Dialoghi)**: ITALIANO.
*   **Documentazione**: ITALIANO (per Business Logic), INGLESE (per Build/Agent).

### Terminologia Business (UI)
| Codice (Db/Backend) | UI (Frontend/Utente) |
| :--- | :--- |
| `Dipendente` | **DIPENDENTE** |
| `Certificato` | **DOCUMENTO** |
| `Corso` | **TIPO DOCUMENTO** |
| `Data Rilascio` | **DATA EMISSIONE** |

### Style Guide
*   **Python**: PEP 8 standard. Max line length 120.
*   **Naming Convention**:
    *   Classi: `PascalCase` (`LicenseManager`)
    *   Funzioni/Variabili: `snake_case` (`calculate_expiry`)
    *   Costanti: `UPPER_CASE` (`DEFAULT_TIMEOUT`)

## 3. Workflow Git

### Branching Model
*   `main`: Produzione stabile.
*   `feat/nome-feature`: Sviluppo nuove funzionalità.
*   `fix/descrizione-bug`: Correzioni bug.
*   `refactor/descrizione`: Miglioramenti strutturali senza cambio logica.

### Commit Messages
Formato: `type: Subject`
*   `feat`: Nuova funzionalità.
*   `fix`: Correzione bug.
*   `docs`: Aggiornamento documentazione.
*   `refactor`: Refactoring codice.
*   `test`: Aggiunta/Modifica test.
*   `chore`: Aggiornamento dipendenze, build tools.

*Esempio*: `feat: Implement robust retry logic for AI extraction`

## 4. Gestione Errori

*   **No Silent Failures**: Vietato `except Exception: pass`. Logga sempre l'errore.
*   **UI Feedback**: Ogni errore critico deve essere comunicato all'utente in italiano (es. "Errore di connessione al server") e non con stack trace tecnici.

## 5. Testing Policy

Il progetto adotta la **Green Suite Policy**.
*   Esegui `pytest` prima di ogni push.
*   Per la UI, usa `tests/desktop_app/mock_qt.py` per testare la logica senza display.
*   Non committare codice rotto.
