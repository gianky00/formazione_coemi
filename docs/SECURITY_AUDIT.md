Ecco il **SECURITY_AUDIT.md** generato basandosi sull'analisi approfondita del codice sorgente fornito. Il documento è strutturato per essere immediatamente utilizzabile da altri Agenti AI e sviluppatori umani.

***

# SECURITY_AUDIT.md

**Data Audit:** 11/12/2025
**Progetto:** Intelleo
**Versione Analizzata:** 1.0.0 (Nuitka Build)
**Livello di Rischio Complessivo:** 🟠 **MEDIO-ALTO**

---

## 1. Executive Summary

L'analisi del codice sorgente di **Intelleo** rivela un'architettura di sicurezza ibrida con ottime intuizioni difensive (protezione runtime, database in-memory crittografato, audit logging granulare) ma compromessa da vulnerabilità critiche nella gestione dei segreti crittografici.

### Punti di Forza
*   ✅ **Database Security:** Strategia "In-Memory Encrypted" che riduce drasticamente la superficie di attacco a riposo.
*   ✅ **Audit Logging:** Sistema di tracciamento azioni robusto (`AuditLog`) con alert via email per eventi critici.
*   ✅ **Anti-Tampering:** Rilevamento runtime di VM, debugger e tool di analisi (`desktop_app/services/security_service.py`).
*   ✅ **Input Sanitization:** Protezione contro CSV Injection e validazione firme file (Magic Numbers).

### Criticità Maggiori
*   ⛔ **Hardcoded Secrets:** Chiavi crittografiche e API Key sono presenti nel codice sorgente (anche se offuscate).
*   ⛔ **Static Key Derivation:** La chiave di cifratura del database deriva da una stringa statica nel codice.
*   ⛔ **Token Lifecycle:** Durata dei JWT eccessiva (30 giorni) senza meccanismo di refresh/rotazione.

---

## 2. Autenticazione & Autorizzazione

Il sistema utilizza `FastAPI` con `OAuth2PasswordBearer` e `JWT`.

### Meccanismi Attuali
*   **Hashing Password:** Utilizza `bcrypt` (via `passlib`). Implementazione corretta con salt automatico.
*   **Token:** JWT (JSON Web Token) firmati con algoritmo `HS256`.
*   **Session Lock:** Implementazione custom (`LockManager`) per garantire l'accesso esclusivo al DB (single-user write mode).
*   **Logout:** Implementato tramite `BlacklistedToken` su DB.

### Vulnerabilità Identificate
| File | Riga | Descrizione | Rischio |
|------|------|-------------|---------|
| `app/core/config.py` | 13 | `ACCESS_TOKEN_EXPIRE_MINUTES = 43200` (30 giorni). Un token rubato rimane valido per un mese. | **ALTO** |
| `app/api/routers/auth.py` | 64 | `settings.SECRET_KEY` è hardcodato (vedi sez. Secrets). Se compromesso, permette la falsificazione di sessioni. | **CRITICO** |

### Raccomandazioni
1.  **Ridurre TTL Token:** Portare la scadenza a 15-60 minuti e implementare un endpoint `/refresh-token`.
2.  **Rate Limiting:** Sebbene esista un controllo logico (`AuditLog` count), manca un rate limiter a livello di middleware (es. `slowapi`) per prevenire DoS sugli endpoint di login.

---

## 3. Gestione Secrets

Questa è l'area più critica. Nonostante l'uso di `app.core.string_obfuscation`, i segreti sono statici.

### Secrets Esposti
| File | Variabile/Contesto | Stato | Fix Richiesto |
|------|-------------------|-------|---------------|
| `app/core/db_security.py` | `_STATIC_SECRET` | **IN CHIARO** | Spostare su Keyring di sistema o derivare da password utente (PBKDF2). |
| `app/core/config.py` | `SECRET_KEY` | **IN CHIARO** | Generare random all'installazione o usare Env Var. |
| `admin/call_list_IA.py` | `api_key` | **IN CHIARO** | Rimuovere fallback hardcodato Google API Key. |
| `admin/crea_licenze/...` | `LICENSE_SECRET_KEY` | **IN CHIARO** | Rimuovere dal codice distribuito agli admin. |
| `app/core/license_security.py` | `_FERNET_KEY_OBFUSCATED` | **OFFUSCATO** | L'offuscamento XOR è reversibile staticamente. |

### Analisi Offuscamento (`app/core/string_obfuscation.py`)
L'algoritmo XOR con chiave statica `0x7B` protegge solo da `strings` command base. Un attaccante può facilmente deoffuscare le stringhe decompilando il bytecode Python o eseguendo lo script di verifica incluso.

**Codice Vulnerabile:**
```python
# app/core/string_obfuscation.py
_XOR_KEY = 0x7B 
def deobfuscate_string(obfuscated, key=_XOR_KEY): ...
```

---

## 4. Input Validation & Sanitization

Il livello di validazione è generalmente buono.

### Controlli Implementati
*   **File Upload (`app/utils/file_security.py`):**
    *   Verifica Magic Number (`%PDF-`) invece dell'estensione.
    *   Controllo dimensione massima (`MAX_UPLOAD_SIZE`).
*   **CSV Import (`app/api/main.py`):**
    *   Parsing robusto con `csv.DictReader`.
    *   Protezione **CSV Injection** implementata in `app/api/routers/audit.py`:
    ```python
    def sanitize_csv_cell(value):
        if isinstance(value, str) and value.startswith(('=', '@', '+', '-')):
            return "'" + value  # Neutralizza formule Excel
    ```
*   **Path Traversal:**
    *   `app/services/document_locator.py` usa `sanitize_filename` (regex `[<>:"/\\|?*]`).
    *   Tuttavia, l'uso di `os.path.join` con input utente richiede cautela.

### Vulnerabilità Potenziali
*   **ReDoS (Regular Expression Denial of Service):**
    *   In `app/services/ai_extraction.py`: `re.search(r'```json\s*(.*?)```', text, re.DOTALL)` su output AI potenzialmente grande.
    *   **Fix:** Limitare la lunghezza dell'input prima della regex.

---

## 5. Dipendenze

Analisi del file `requirements.txt`.

| Libreria | Versione | Vulnerabilità Note / Rischio |
|----------|----------|------------------------------|
| `fastapi` | `0.121.2` | Aggiornata. Sicura. |
| `sqlalchemy` | `2.0.44` | Aggiornata. Sicura contro SQLi. |
| `pyarmor` | (latest) | Essenziale per la protezione del codice sorgente, ma non infallibile. |
| `gTTS` | `>=2.5.1` | Chiama API esterne Google. Privacy issue potenziale. |
| `wmi` | (latest) | Windows only. Richiede permessi elevati per alcune query. |

---

## 6. OWASP Top 10 Checklist

| OWASP Category | Stato | Note |
|----------------|-------|------|
| **A01: Broken Access Control** | ⚠️ Parziale | `check_write_permission` protegge le scritture, ma la logica `is_admin` è semplice. |
| **A02: Cryptographic Failures** | ❌ **FAIL** | Chiavi hardcodate. Static IV/Salt non visibili ma probabili nella derivazione statica. |
| **A03: Injection** | ✅ Pass | ORM usato ovunque. CSV Injection mitigata. |
| **A04: Insecure Design** | ⚠️ Warning | Il DB In-Memory viene decifrato completamente in RAM. Dump della memoria espone tutto. |
| **A05: Security Misconfiguration** | ⚠️ Warning | `DEBUG` level loggato su file in produzione (`app/utils/logging.py`). |
| **A06: Vulnerable Components** | ✅ Pass | Dipendenze recenti. |
| **A07: Identification Failures** | ⚠️ Warning | Nessun MFA. Password policy debole (default "primoaccesso"). |
| **A08: Software & Data Integrity** | ✅ Pass | Verifica firma file PDF. Controllo integrità moduli (`integrity_service.py`). |
| **A09: Logging Failures** | ✅ Pass | Audit log eccellente e persistente su DB. |
| **A10: SSRF** | ✅ Pass | Nessuna funzionalità di fetch URL arbitrari da parte dell'utente. |

---

## 7. Crittografia

### Database (`app/core/db_security.py`)
Il database SQLite viene cifrato/decifrato interamente.
*   **Algoritmo:** Fernet (AES-128 in CBC mode con HMAC-SHA256).
*   **Debolezza:** La chiave è derivata da `_STATIC_SECRET`. Chiunque abbia il binario può derivare la chiave e decifrare il DB locale.
*   **Codice:**
    ```python
    def _derive_key(self) -> bytes:
        digest = hashlib.sha256(self._STATIC_SECRET.encode()).digest()
        return base64.urlsafe_b64encode(digest)
    ```

### Licenze (`app/core/license_security.py`)
*   Usa Fernet con chiave offuscata. Sicurezza basata sull'oscurità.

---

## 8. Logging & Monitoring

*   **Sentry:** Integrato con DSN offuscato in `app/main.py`. Configurato per escludere PII (`send_default_pii=False`). Ottimo.
*   **File Log:** `intelleo_debug.log` in rotazione.
    *   *Rischio:* Livello `DEBUG` in produzione potrebbe loggare dati sensibili (es. contenuti PDF parsati, metadati).
    *   *Fix:* Impostare livello `INFO` o `WARNING` per le build di produzione (`sys.frozen`).

---

## 9. Raccomandazioni Prioritarie

### CRITICO (Fix Immediato)
1.  **Rimuovere `SECRET_KEY` hardcoded:** Passare alla generazione di una chiave casuale al primo avvio, salvata nel keyring di sistema o in un file protetto (ACL) locale.
2.  **Key Derivation Database:** Non usare una stringa statica. Derivare la chiave di cifratura del DB dalla **Password dell'Admin** (usando Argon2 o PBKDF2). Questo rende il DB illeggibile se non si conosce la password.
3.  **Sanitize `admin/` scripts:** Rimuovere le API Key di Google dai file di esempio o script admin prima del commit/build.

### ALTO (Fix pre-rilascio)
1.  **Token Expiry:** Ridurre drasticamente la durata dell'Access Token.
2.  **Logging Level:** Forzare `logging.WARNING` se `getattr(sys, 'frozen', False)` è True.
3.  **Secure Overwrite:** Implementare la cancellazione sicura (shredding) dei file temporanei decifrati o dei file PDF quando vengono "spostati" nel cestino.

### MEDIO (Miglioramenti)
1.  **Password Complexity:** Imporre regole di complessità per la password admin.
2.  **User Isolation:** Verificare che `app.core.path_resolver` utilizzi directory con permessi restrittivi (es. 0700 su Linux/Mac).

---

## 10. Compliance Checklist (GDPR)

*   [x] **Diritto all'Oblio:** Funzione di eliminazione dipendente e documenti presente.
*   [x] **Data Minimization:** I log di Audit non sembrano salvare il payload completo dei file.
*   [ ] **Encryption at Rest:** Presente ma debole (chiave statica). **Non conforme** per dati sensibili senza fix della chiave.
*   [x] **Access Control:** Ruoli Admin/User distinti.
*   [x] **Audit Trail:** Tracciamento accessi e modifiche presente.

---

**Conclusione:**
Intelleo ha una solida base funzionale di sicurezza, ma la gestione delle chiavi crittografiche vanifica gran parte degli sforzi. L'implementazione della derivazione della chiave dalla password utente è il passo fondamentale per renderlo un prodotto sicuro.