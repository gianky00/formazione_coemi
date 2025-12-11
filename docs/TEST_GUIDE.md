# Guida ai Test e QA

Questo documento descrive le strategie di testing, l'architettura della suite di test e le procedure per garantire la qualità del codice ("Green Suite Policy").

## 1. Filosofia di Testing
Il progetto adotta una politica **"Strict Green Suite"**: non sono ammessi test falliti o skippati senza una issue tracciata.

*   **Parallel Structure**: Ogni file sorgente `app/x.py` ha un corrispondente `tests/app/test_x.py`.
*   **Headless First**: I test UI devono girare in ambienti CI/CD senza display fisico (xvfb o mock).
*   **Isolation**: Ogni test deve pulire il proprio stato (Mock DB in-memory, Temp dirs).

## 2. Esecuzione Test

### Unit & Integration Test (Pytest)
Dalla root del progetto:
```bash
python -m pytest
```
*   **Coverage Report**: `python -m pytest --cov=app --cov-report=html`

### End-to-End & Build Verification (Tools)
Per verificare la build compilata (Nuitka) o flussi critici completi:

1.  **Critical Flows (E2E)**:
    ```bash
    python admin/tools/critical_flows_test.py
    ```
    Esegue simulazioni complete di login, importazione file e calcolo scadenze.

2.  **Build Validation**:
    ```bash
    python admin/tools/test_build.py
    ```
    Verifica che l'eseguibile `dist/nuitka/.../Intelleo.exe` si avvii correttamente e carichi le dipendenze.

---

## 3. Strategia di Mocking (Headless Qt)

Poiché `PyQt6` richiede un server grafico (X11/Wayland) per istanziare i widget, utilizziamo una strategia di **Mocking Totale** per i test unitari della logica UI.

### Il Modulo `tests/desktop_app/mock_qt.py`
Questo modulo agisce come un "Virtual Qt". Sostituisce `PyQt6` in `sys.modules` prima che venga importato dal codice di produzione.

**Come Funziona:**
1.  **Intercettazione**: Il test importa `mock_qt`.
2.  **Patching**: `mock_qt` inietta oggetti Fake (`MagicMock` potenziati) in `sys.modules['PyQt6.QtWidgets']`, ecc.
3.  **Simulazione**:
    *   `DummyQWidget`: Simula metodi come `show()`, `hide()`, `setLayout()`.
    *   `DummyQSettings`: Simula persistenza in un `dict` in-memory.
    *   `DummyQTimer`: Permette di eseguire il callback `timeout` manualmente.

---

## 4. Test di Integrazione (Backend)

I test del backend (`tests/app/`) utilizzano `TestClient` di FastAPI e un database SQLite in-memory isolato per ogni funzione di test via `fixture`.

### Database Fixture (`tests/conftest.py`)
*   **`db_session`**: Crea un DB `sqlite:///:memory:` nuovo per ogni test.
*   **`client`**: Client HTTP pre-autenticato (ove necessario).
*   **`mock_ai`**: Simula le risposte di Gemini per evitare costi e latenza.

## 5. Test Critici da Mantenere

Alcuni test coprono flussi vitali e non devono mai essere rimossi o indeboliti:
1.  **`test_db_security.py`**: Verifica che il DB sia cifrato su disco e il Lock funzioni.
2.  **`test_license_manager.py`**: Verifica che una licenza scaduta blocchi l'avvio.
3.  **`test_ai_extraction.py`**: Verifica che il prompt di Gemini contenga le regole di business aggiornate (es. "ATEX", "NOMINA").
4.  **`test_notification_service.py`**: Verifica la generazione del PDF e l'invio Email (con mock SMTP).
