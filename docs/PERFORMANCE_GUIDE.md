Ecco il file `PERFORMANCE_GUIDE.md` basato sull'analisi approfondita del codice sorgente fornito.

***

# PERFORMANCE_GUIDE.md - Guida alle Performance Intelleo

## 1. Performance Overview

Intelleo utilizza un'architettura ibrida unica focalizzata sulla sicurezza, che influenza direttamente le prestazioni.

*   **Architettura**: Backend FastAPI + Frontend Tkinter (Desktop) / React (Guida) + Database SQLite In-Memory Cifrato.
*   **Stato Attuale**:
    *   **Lettura Dati**: Estremamente veloce (Microsecondi) grazie a SQLite in RAM (`sqlite3.connect(':memory:')`).
    *   **Scrittura Dati**: Lenta (O(N) rispetto alla dimensione del DB) a causa della crittografia completa del file su disco ad ogni salvataggio.
    *   **Startup**: ~2-5 secondi (dipende dalla decrittazione del DB e Nuitka).
*   **Metriche Chiave**:
    *   **Startup Time**: Target < 5s (Monitorato da `admin/tools/benchmark_builds.py`).
    *   **API Latency**: < 50ms per chiamate locali, < 60s per chiamate AI (Gemini).
    *   **RAM Usage**: Base ~150MB + Dimensione DB decifrato.

---

## 2. Bottleneck Identificati

### A. Serializzazione e Cifratura Database (Critico)
*   **File**: `app/core/db_security.py`
*   **Problema**: Il metodo `save_to_disk` serializza l'intera connessione SQLite in memoria, la cifra con Fernet e la scrive su disco.
*   **Impatto**: Man mano che il database cresce (Audit Logs), il salvataggio diventa progressivamente più lento e blocca l'I/O.
*   **Codice**:
    ```python
    # app/core/db_security.py
    serialized = self.active_connection.serialize()
    final_data = self._HEADER + self.fernet.encrypt(serialized) # Bottleneck CPU
    self._safe_write(final_data) # Bottleneck I/O
    ```

### B. Analisi AI Sincrona/Bloccante
*   **File**: `app/services/ai_extraction.py`
*   **Problema**: Le chiamate a Google Gemini possono impiegare 5-30 secondi. Se non gestite correttamente, bloccano i worker.
*   **Mitigazione Attuale**: Uso di `TaskRunner` nel client desktop (`desktop_app/utils.py`) per non bloccare la UI Tkinter.

### C. Scansione File System
*   **File**: `app/services/sync_service.py` -> `synchronize_all_files`
*   **Problema**: Scansiona ricorsivamente le cartelle per spostare i file. Su file system di rete o con migliaia di PDF, questo è lento.

---

## 3. Ottimizzazioni Codice

### A. Ottimizzazione SQLAlchemy (N+1 Problem)
Il codice attuale gestisce correttamente il problema N+1 usando `selectinload`. **Mantenere questo pattern**.

*   **Pattern Corretto (Presente in `app/api/main.py`)**:
    ```python
    # Eager loading delle relazioni per evitare query multiple nel loop
    query = db.query(Certificato).options(
        selectinload(Certificato.dipendente),
        selectinload(Certificato.corso)
    )
    ```
*   **Da Evitare**: Accedere a `cert.dipendente.nome` all'interno di un loop senza aver fatto `options(selectinload(...))`.

### B. Compilazione Nuitka (LTO)
*   **File**: `admin/offusca/build_nuitka.py`
*   **Ottimizzazione**: Assicurarsi che Link Time Optimization (LTO) sia attivo per le build di produzione.
    ```python
    # Attuale (Corretto):
    f"--lto={'yes' if not fast_mode else 'no'}",
    ```
    *Azione*: Non usare flag `--fast` per le release finali. LTO riduce la dimensione del binario e ottimizza i percorsi di esecuzione del 10-20%.

### C. Gestione Log
*   **File**: `launcher.py`
*   **Ottimizzazione**: I logger "rumorosi" sono già silenziati (`uvicorn`, `urllib3`).
    *   *Fix*: Assicurarsi che `logging.handlers.RotatingFileHandler` sia configurato con `backupCount` basso (es. 3) per evitare I/O inutile su disco.

---

## 4. Caching Strategies

Dato che il DB è in memoria, la cache di livello applicativo è meno critica per i dati DB, ma fondamentale per le risorse esterne.

### A. Hardware ID Caching
*   **File**: `desktop_app/services/hardware_id_service.py`
*   **Stato**: Implementato.
    ```python
    _cached_machine_id = None
    # ... evita chiamate WMI costose ripetute
    ```

### B. GeoIP Database
*   **File**: `app/services/geo_service.py`
*   **Stato**: Implementato singleton.
    ```python
    _reader = None # Il reader viene mantenuto in memoria
    ```

### C. Proposta: Cache Risposte AI (Opzionale)
Se si analizza lo stesso file (stesso hash MD5), restituire il risultato precedente senza chiamare Gemini.
*   **Implementazione**: Tabella `file_cache` nel DB con colonne `file_hash` e `json_result`.

---

## 5. Database Performance

### A. Indici
Verificare che i campi usati per i filtri abbiano indici.
*   **File**: `app/db/models.py`
*   **Analisi**:
    *   `AuditLog.timestamp`: `index=True` (OK - usato per cleanup e filtri).
    *   `Dipendente.matricola`: `unique=True, index=True` (OK).
    *   `Certificato.dipendente_id`: ForeignKey (Crea indice implicito in molti DB, ma esplicito è meglio).

### B. Manutenzione Dati (Vacuum)
Poiché SQLite è in memoria e poi serializzato, la frammentazione interna aumenta la dimensione del blob cifrato.
*   **Soluzione**: `app/core/db_security.py` -> `optimize_database` esegue `VACUUM`.
*   **Raccomandazione**: Eseguire `VACUUM` prima di ogni `save_to_disk` massivo o periodicamente (es. alla chiusura).

---

## 6. Bundle Size (Guide Frontend)

Il frontend React (`guide_frontend`) viene servito staticamente.

*   **Code Splitting**: Vite lo gestisce di default.
*   **Lazy Loading**:
    ```javascript
    // guide_frontend/src/App.jsx
    // Sostituire gli import statici con:
    const DatabaseGuide = React.lazy(() => import('./pages/DatabaseGuide'));
    ```
*   **Assets**: Le immagini BMP in `desktop_app/assets` sono molto pesanti.
    *   *Azione*: Convertire `.bmp` in `.png` o `.webp` per la guida web (risparmio ~80% spazio).

---

## 7. Memory Management

### A. SQLite In-Memory Growth
Il DB risiede interamente in RAM.
*   **Rischio**: `AuditLog` cresce indefinitamente.
*   **Mitigazione**: `app/services/file_maintenance.py` -> `cleanup_audit_logs`.
    *   *Configurazione*: `retention_days=365` e `max_records=100000`.
    *   *Monitoraggio*: Se l'app crasha per OOM (Out Of Memory), ridurre `max_records`.

### B. Gestione File Upload
*   **File**: `app/api/main.py`
*   **Sicurezza**: Lettura a chunk per evitare di caricare file giganti in RAM.
    ```python
    async def _read_file_securely(file: UploadFile, max_size: int) -> bytes:
        # Legge a chunk e controlla la dimensione
    ```
    *Stato*: **Ottimizzato**.

---

## 8. Async/Concurrency

### A. Backend (FastAPI)
*   L'uso di `async def` è limitato ai controller che fanno I/O (es. `upload_pdf`).
*   Le operazioni DB sono sincrone (`SessionLocal`), il che blocca l'event loop se non gestito bene.
*   **Soluzione**: FastAPI esegue le funzioni `def` (non async) in un threadpool separato. **Non cambiare le funzioni DB in `async def`** a meno di non passare a `SQLAlchemy[asyncio]`.

### B. Desktop App (Tkinter)
*   Tkinter non è thread-safe.
*   **Pattern**: Uso di `TaskRunner` (`desktop_app/utils.py`) che usa `threading.Thread` e code per comunicare con la UI.
    *   *Regola*: Mai chiamare `api_client` (rete) nel main thread.

---

## 9. Profiling Guide

### Profiling Backend
Inserire questo middleware in `app/main.py` temporaneamente:

```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Profiling Database Locks
Monitorare i log per:
`WARNING: Lock acquisition failed (Attempt X/Y)`
Se frequente, aumentare il timeout in `app/core/lock_manager.py`.

---

## 10. Monitoring Setup

### Sentry
Già integrato in `app/main.py`.
*   **Campionamento**:
    ```python
    traces_sample_rate=0.5,  # 50% delle transazioni
    profiles_sample_rate=0.1, # 10% profiling
    ```
*   **Filtri**: `before_send_transaction` ignora `/health`, risparmiando quota.

### Log Locali
*   File: `%LOCALAPPDATA%/Intelleo/logs/intelleo.log`
*   Rotazione: 5MB x 3 file (`launcher.py`).

---

## 11. Performance Budget

| Metrica | Target | Azione se superato |
| :--- | :--- | :--- |
| **Startup Time** | < 5 secondi | Verificare dimensione DB, ottimizzare import Python. |
| **Login Time** | < 1 secondo | Verificare latenza decrittazione DB. |
| **PDF Analysis** | < 15 secondi | Verificare connessione internet, retry logic Gemini. |
| **RAM Usage** | < 500 MB | Eseguire pulizia Audit Log, verificare leak immagini Qt. |
| **Installer Size** | < 200 MB | Rimuovere asset inutilizzati, aumentare compressione LZMA. |

---

## 12. Quick Wins (Azioni Immediate)

1.  **Attivare LTO in Nuitka**: Assicurarsi che `build_nuitka.py` venga lanciato senza `--fast` per la produzione.
2.  **Pulizia Audit Log Aggressiva**: Ridurre `max_records` in `app/services/file_maintenance.py` da 100.000 a 50.000 se il DB supera i 50MB.
3.  **Ottimizzazione Immagini**: Convertire le immagini `.bmp` (molto grandi) in `.png` in `desktop_app/assets` e aggiornare i riferimenti nel codice (`prepare_installer_assets.py`).
4.  **Pre-validazione CSV**: Nel client (`desktop_app/api_client.py`), il controllo dimensione file CSV prima dell'upload è già presente. Verificare che il limite (5MB) sia adeguato.

---

### Diagramma Flusso Dati & Performance

```mermaid
graph TD
    User[Utente] -->|Interazione UI| Tkinter[Desktop App]
    Tkinter -->|TaskRunner Thread| APIClient
    APIClient -->|HTTP Request| FastAPI[Backend Server]
    
    subgraph Backend Performance
        FastAPI -->|Auth Check| Security
        FastAPI -->|CRUD| DBSession[DB Session]
        DBSession -->|Read/Write (Fast)| SQLiteRAM[(SQLite In-Memory)]
        
        SQLiteRAM -.->|Serialize & Encrypt (Slow)| SaveDisk[Save to Disk]
        SaveDisk -->|Write File| EncryptedDB[database.db Encrypted]
    end
    
    subgraph External Services
        FastAPI -->|Upload PDF| AIService[AI Extraction]
        AIService -->|Network Call (Slow)| Gemini[Google Gemini API]
    end
```