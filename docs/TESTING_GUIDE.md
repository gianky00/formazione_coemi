Ecco il file `TESTING_GUIDE.md` generato, ottimizzato per Agenti AI e sviluppatori umani, basato sull'analisi approfondita del codice sorgente fornito.

***

# TESTING_GUIDE.md - Guida Completa al Testing per Intelleo

## 1. Strategia di Test

Il progetto **Intelleo** adotta una strategia di testing ibrida per garantire la stabilità sia del backend (FastAPI) che del frontend desktop (Tkinter), con un focus particolare sulla sicurezza e sull'integrità dei dati.

### Piramide dei Test
1.  **Unit Tests (70%)**: Focus sulla logica di business, parser, utility di sicurezza e servizi isolati (es. `certificate_logic.py`, `ai_extraction.py` con mock).
2.  **Integration Tests (20%)**: Test delle API FastAPI tramite `TestClient` con database in-memory (SQLite) e interazioni tra controller desktop e API.
3.  **E2E / Critical Flows (10%)**: Script specifici (`critical_flows_test.py`) che simulano l'avvio dell'eseguibile compilato e flussi utente completi.

### Obiettivi di Copertura
*   **Target**: > 80% Code Coverage globale.
*   **Aree Critiche (100% richiesto)**:
    *   `app/core/db_security.py` (Crittografia e Locking DB).
    *   `app/core/license_security.py` (Gestione licenze).
    *   `app/services/ai_extraction.py` (Parsing dati sensibili).

---

## 2. Setup Ambiente di Test

### Prerequisiti
*   Python 3.12+
*   Virtual Environment attivo

### Installazione Dipendenze
```bash
# Installazione dipendenze di test
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock httpx
```

### Configurazione `pytest.ini`
Il progetto include già un `pytest.ini` configurato per ignorare le directory di build:
```ini
[pytest]
norecursedirs = Lib site-packages Include Scripts dll build dist
```

---

## 3. Struttura Directory Test

La struttura dei test rispecchia quella del codice sorgente (`src` -> `tests`):

```text
tests/
├── app/                        # Test Backend
│   ├── api/                    # Test Endpoints FastAPI
│   │   └── routers/            # Test specifici per router (auth, users, system)
│   ├── core/                   # Test sicurezza, config, path resolution
│   ├── db/                     # Test modelli, seeding, migrazioni
│   └── services/               # Test logica business (AI, notifiche)
├── desktop_app/                # Test Frontend Desktop
│   ├── components/             # Test componenti UI isolati
│   ├── services/               # Test servizi client-side (hardware id, time)
│   ├── view_models/            # Test logica di presentazione
│   ├── views/                  # Test logica delle viste (mockando Tkinter)
│   └── workers/                # Test thread e worker asincroni
├── core/                       # Test librerie condivise (LockManager)
├── tools/                      # Test script di build e manutenzione
└── conftest.py                 # CONFIGURAZIONE GLOBALE E FIXTURES
```

---

## 4. Convenzioni di Test

### Naming Convention
*   **File**: `test_<nome_modulo>.py`
*   **Classi**: `Test<NomeComponente>`
*   **Funzioni**: `test_<scenario>_<risultato_atteso>`

### Struttura AAA (Arrange, Act, Assert)
Ogni test deve seguire rigorosamente questo pattern:

```python
def test_create_certificato_success(test_client, db_session):
    # ARRANGE: Preparazione dati
    payload = {
        "nome": "Mario Rossi",
        "corso": "ANTINCENDIO",
        "categoria": "ANTINCENDIO",
        "data_rilascio": "01/01/2024",
        "data_scadenza": "01/01/2029"
    }

    # ACT: Esecuzione azione
    response = test_client.post("/api/v1/certificati/", json=payload)

    # ASSERT: Verifica risultati
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Rossi Mario" # Verifica normalizzazione nome
```

---

## 5. Fixtures Comuni (`tests/conftest.py`)

Il file `conftest.py` è il cuore dell'infrastruttura di test. Contiene mock globali per isolare i test dall'hardware e dalla rete.

### Fixtures Principali

| Fixture | Scope | Descrizione |
| :--- | :--- | :--- |
| `test_client` | Function | Client FastAPI (`httpx`) pre-configurato con override delle dipendenze DB e Auth. |
| `db_session` | Function | Sessione SQLAlchemy isolata su DB SQLite in-memory. Reset automatico dopo ogni test. |
| `mock_settings` | Session | Configurazione applicativa patchata per usare directory temporanee (`tmp_path`). |
| `admin_token_headers` | Session | Header di autenticazione per utente Admin simulato. |
| `test_dirs` | Session | Directory temporanea per simulare il filesystem (database, log, licenze). |

### Global Kill Switch (Mocking Preventivo)
Per evitare crash durante i test (es. chiamate WMI su Linux o thread appesi), `conftest.py` applica patch globali a livello di `sys.modules` prima di importare l'app:

```python
# Esempio dal conftest.py
mock_wmi = MagicMock()
sys.modules["wmi"] = mock_wmi # Disabilita chiamate hardware reali

mock_sentry = MagicMock()
sys.modules["sentry_sdk"] = mock_sentry # Disabilita invio errori reali
```

---

## 6. Scenari Critici da Testare

### 1. Sicurezza Database (Core)
Verificare che il database non venga mai scritto su disco in chiaro.
*   **Test**: `tests/app/core/test_db_security.py`
*   **Verifica**: `save_to_disk()` deve produrre un file con header custom e contenuto non leggibile come SQLite.

### 2. Importazione AI e Parsing
Verificare la resilienza del parser AI.
*   **Test**: `tests/app/services/test_ai_extraction_robustness.py`
*   **Scenario**: JSON malformato, categorie sconosciute, date ambigue.

### 3. Concorrenza e Locking
Verificare che due istanze non corrompano i dati.
*   **Test**: `tests/app/core/test_lock_manager_full.py`
*   **Scenario**: Acquisizione lock su file esistente, heartbeat, recupero "stale lock" (processo morto).

### 4. Flusso Aggiornamento Licenza
Verificare il meccanismo di auto-update.
*   **Test**: `tests/desktop_app/services/test_license_updater_coverage.py`
*   **Scenario**: Verifica checksum SHA256 dei file scaricati.

---

## 7. Mocking Guidelines

### Cosa Mockare (SEMPRE)
1.  **Google Gemini (GenAI)**: Mai chiamare API reali.
    ```python
    @patch("app.services.ai_extraction.get_gemini_model")
    def test_ai(mock_get_model):
        mock_model = MagicMock()
        mock_model.generate_content.return_value.text = '{"nome": "Test"}'
        mock_get_model.return_value = mock_model
        # ...
    ```
2.  **File System (Parzialmente)**: Usare `tmp_path` fixture di pytest per file temporanei. Mockare `shutil.move` se si testano permessi.
3.  **SMTP**: Mockare `smtplib.SMTP` per evitare invio email.
4.  **Hardware ID**: Mockare `wmi` e `subprocess` per identificatori hardware.

### Cosa NON Mockare
1.  **SQLAlchemy Session**: Usare la fixture `db_session` con SQLite in-memory per testare query reali e vincoli di integrità.
2.  **Pydantic Models**: Lasciare che la validazione avvenga realmente.

---

## 8. Comandi di Test

### Esecuzione Standard
```bash
# Esegue tutti i test
python -m pytest

# Esegue test specifici per il backend
python -m pytest tests/app

# Esegue test con output dettagliato
python -m pytest -v
```

### Analisi Copertura
```bash
# Genera report coverage nel terminale
python -m pytest --cov=. --cov-report=term-missing

# Genera report XML (per SonarCloud/CI)
python -m pytest --cov=. --cov-report=xml
```

### Test "Critical Flows" (E2E su Build)
Da eseguire *dopo* aver compilato con Nuitka:
```bash
python admin/tools/critical_flows_test.py
```

---

## 9. CI/CD Testing Pipeline

La pipeline ideale per questo progetto (GitHub Actions) dovrebbe seguire questi step:

1.  **Linting**: `flake8 .`
2.  **Unit & Integration Tests**:
    ```yaml
    - name: Run Pytest
      run: |
        pip install -r requirements.txt
        python -m pytest --cov=. --cov-report=xml:coverage.xml
    ```
3.  **SonarCloud Analysis**: Upload di `coverage.xml`.
4.  **Build Nuitka**: Solo se i test passano.
5.  **Post-Build Verification**: Esecuzione di `admin/tools/test_build.py` sull'eseguibile generato.

---

## 10. Performance Testing

Per un'applicazione desktop locale con DB in-memory, le performance critiche sono:

1.  **Tempo di Avvio (Startup)**:
    *   Monitorato da `admin/tools/benchmark_builds.py`.
    *   Target: < 5 secondi per "Backend Ready".

2.  **AI Extraction Latency**:
    *   Poiché dipende da API esterne, i test devono verificare il timeout e la gestione dei retry (`tenacity`).
    *   Vedi `tests/app/services/test_ai_extraction_robustness.py`.

---

## Diagramma di Flusso dei Test

```mermaid
graph TD
    A[Sviluppatore Commit] --> B{Unit Tests Passano?}
    B -- No --> C[Fix Code]
    B -- Yes --> D{Integration Tests Passano?}
    D -- No --> C
    D -- Yes --> E[Build Nuitka]
    E --> F[Critical Flows Test (E2E)]
    F -- Fail --> G[Investiga Build]
    F -- Pass --> H[Release]
```