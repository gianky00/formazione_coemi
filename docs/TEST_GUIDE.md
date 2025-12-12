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

---

## 6. User Simulation Tests (CRASH ZERO)

Il progetto include un framework di test di simulazione utente per verificare la robustezza dell'applicazione sotto interazioni realistiche.

### Location
```
tests/desktop_app/simulation/
├── conftest.py              # Fixtures per simulazione
├── user_actions.py          # Helper UserSimulator
├── test_login_scenarios.py  # Test scenari login
├── test_navigation.py       # Test navigazione
└── test_stress.py           # Stress test
```

### Esecuzione

```bash
# Tutti i test di simulazione (usa forked per isolamento)
pytest tests/desktop_app/simulation/ -v

# Solo test di login
pytest tests/desktop_app/simulation/test_login_scenarios.py -v

# Solo stress test
pytest tests/desktop_app/simulation/test_stress.py -v
```

### UserSimulator

Classe helper per simulare azioni utente:

```python
from tests.desktop_app.simulation.user_actions import UserSimulator

def test_login_flow(qtbot, login_view):
    sim = UserSimulator(qtbot)
    
    # Trova widget
    username_input = login_view.findChild(QLineEdit, "username")
    password_input = login_view.findChild(QLineEdit, "password")
    login_btn = login_view.findChild(QPushButton, "login_btn")
    
    # Simula digitazione
    sim.type_text(username_input, "admin")
    sim.type_text(password_input, "password123")
    
    # Simula click
    sim.click(login_btn)
    
    # Attendi animazione
    sim.wait_for_animation()
    
    # Verifica risultato
    assert not login_view.isVisible()
```

### Metodi UserSimulator

| Metodo | Descrizione |
|--------|-------------|
| `click(widget)` | Click singolo |
| `double_click(widget)` | Doppio click |
| `type_text(widget, text)` | Digitazione testo |
| `press_key(widget, key)` | Pressione tasto |
| `press_enter(widget)` | Pressione Enter |
| `press_escape(widget)` | Pressione Escape |
| `press_tab(widget)` | Pressione Tab |
| `wait_for_visible(widget)` | Attendi widget visibile |
| `wait_for_enabled(widget)` | Attendi widget abilitato |
| `wait_for_animation()` | Attendi fine animazioni |
| `wait(ms)` | Attendi tempo fisso |

### Creare Nuovi Scenari

1. **Crea il file test** in `tests/desktop_app/simulation/`
2. **Usa il marker forked** per isolamento:
   ```python
   pytestmark = pytest.mark.forked
   ```
3. **Definisci fixtures** per i widget necessari
4. **Usa UserSimulator** per le interazioni
5. **Verifica invarianti** (no crash, stato corretto)

### Esempio: Test Stress

```python
class TestStress:
    @pytest.fixture
    def simulator(self, qtbot):
        sim = UserSimulator(qtbot)
        sim._action_delay_ms = 5  # Veloce per stress
        return sim
    
    def test_100_random_clicks(self, widget, simulator):
        buttons = widget.findChildren(QPushButton)
        
        for i in range(100):
            btn = random.choice(buttons)
            simulator.click(btn)
        
        # Non deve crashare
        assert widget.isVisible()
```

### Note Importanti

1. **Forked Execution**: I test usano `pytest-forked` per eseguire ogni test in un subprocess separato, evitando segfault durante cleanup di widget PyQt6.

2. **Mocking**: Usa `patch()` per mockare dipendenze complesse (API, License, etc.) e velocizzare i test.

3. **Timeout**: Alcuni test hanno timeout per evitare hang. Se un test è lento, riduci le iterazioni o aumenta il timeout.

---

## 7. Test Isolation (Desktop App)

### Problema

Alcuni test usano `sys.modules.update(mock_qt_modules())` che può inquinare i moduli per altri test.

### Soluzione

Eseguire i test in due gruppi:

```bash
# Gruppo 1: Test che richiedono Qt reale
pytest tests/desktop_app/core/ tests/desktop_app/mixins/ -v

# Gruppo 2: Test che usano mock Qt
pytest tests/desktop_app/ --ignore=tests/desktop_app/core --ignore=tests/desktop_app/mixins -v
```

### Test Coverage per CRASH ZERO

| Modulo | Test File | # Test |
|--------|-----------|--------|
| `widget_guard.py` | `test_widget_guard.py` | 7 |
| `animation_manager.py` | `test_animation_manager.py` | 38 |
| `signal_guard.py` | `test_signal_guard.py` | 8 |
| `error_boundary.py` | `test_error_boundary.py` | 14 |
| `state_machine.py` | `test_state_machine.py` | 23 |
| `safe_widget_mixin.py` | `test_safe_widget_mixin.py` | 11 |
| Simulazione | `test_*.py` (simulation/) | 35 |
