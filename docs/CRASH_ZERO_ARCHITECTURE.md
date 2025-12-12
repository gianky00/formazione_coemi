# CRASH ZERO Architecture

Questo documento descrive l'architettura di robustezza implementata nel progetto "Crash Zero", un'iniziativa per eliminare i crash dell'applicazione desktop PyQt6 causati da race condition, widget distrutti e gestione errata del ciclo di vita.

## Panoramica

L'architettura Crash Zero si compone di 7 sistemi interconnessi:

1. **Widget Lifecycle Guard** - Protezione accesso widget distrutti
2. **Animation Manager** - Gestione centralizzata animazioni
3. **Signal/Slot Hardening** - Disconnessione sicura segnali
4. **Error Boundaries** - Contenimento errori per view
5. **State Machine** - Gestione centralizzata transizioni UI
6. **Observability** - Monitoraggio e diagnostica (Sentry)
7. **User Simulation** - Test di robustezza automatizzati

---

## 1. Widget Lifecycle Guard System

### Problema Risolto
I crash più comuni in PyQt6 derivano dall'accesso a widget già distrutti dal garbage collector C++, causando `RuntimeError: wrapped C/C++ object has been deleted`.

### Moduli

#### `desktop_app/core/widget_guard.py`

```python
from desktop_app.core.widget_guard import is_widget_alive, guard_widget_access, WidgetRef

# Verifica se un widget è ancora valido
if is_widget_alive(my_widget):
    my_widget.setText("Safe!")

# Decorator per metodi che accedono a widget
class MyView(QWidget):
    @guard_widget_access
    def update_ui(self):
        self.label.setText("Updated")  # Sicuro!

# Riferimento debole con controllo automatico
ref = WidgetRef(my_widget)
if ref:
    ref.get().show()
```

#### `desktop_app/mixins/safe_widget_mixin.py`

Mixin che fornisce metodi sicuri per gestire widget figli:

```python
from desktop_app.mixins.safe_widget_mixin import SafeWidgetMixin

class LoginView(QWidget, SafeWidgetMixin):
    def __init__(self):
        super().__init__()
        SafeWidgetMixin.__init__(self)
        
        self.btn = QPushButton("Login")
        self.register_child("login_btn", self.btn)
    
    def update_button(self):
        # Accesso sicuro tramite nome
        btn = self.get_child("login_btn")
        if btn:
            btn.setText("Loading...")
    
    def safe_operation(self):
        # Operazione con fallback
        self.safe_call(
            lambda: self.label.setText("Done"),
            fallback=None
        )
```

### Pattern di Utilizzo

1. **Sempre** usare `@guard_widget_access` su metodi slot
2. **Mai** accedere direttamente a widget in callback async
3. **Usare** `WidgetRef` per riferimenti a lungo termine
4. **Verificare** `is_widget_alive()` prima di operazioni UI

---

## 2. Animation Manager

### Problema Risolto
Animazioni concorrenti sullo stesso widget causavano comportamenti imprevedibili e crash durante la distruzione del widget.

### Modulo: `desktop_app/core/animation_manager.py`

```python
from desktop_app.core.animation_manager import (
    animation_manager,
    fade_in, fade_out,
    slide_in, slide_out,
    scale_bounce,
    AnimationConfig
)

# Animazioni semplici con helper functions
fade_in(widget, duration_ms=300)
fade_out(widget, duration_ms=200, on_complete=lambda: widget.hide())

# Slide con direzione
slide_in(widget, direction="left", distance=100)

# Bounce effect
scale_bounce(widget, scale_factor=1.1)

# Configurazione avanzata
config = AnimationConfig(
    duration_ms=500,
    easing=QEasingCurve.Type.OutElastic,
    on_complete=my_callback
)
animation_manager.animate_property(
    widget, "geometry", 
    widget.geometry(), 
    target_geometry,
    config
)

# Cancellazione sicura (importante nel cleanup!)
animation_manager.cancel_all(owner=self)
```

### Caratteristiche

- **Thread-safe**: Usa `QMutex` per operazioni concorrenti
- **Auto-cleanup**: Rimuove animazioni quando il widget viene distrutto
- **Owner tracking**: Ogni animazione è associata a un owner per cleanup gruppato
- **Singleton**: Una sola istanza gestisce tutte le animazioni

### Best Practices

1. **Sempre** cancellare animazioni in `closeEvent`:
   ```python
   def closeEvent(self, event):
       animation_manager.cancel_all(self)
       super().closeEvent(event)
   ```

2. **Usare** helper functions invece di creare animazioni manuali

3. **Non** animare widget durante la distruzione

---

## 3. Signal/Slot Hardening

### Problema Risolto
Connessioni signal/slot orfane causavano crash quando il ricevente veniva distrutto prima della disconnessione.

### Modulo: `desktop_app/core/signal_guard.py`

```python
from desktop_app.core.signal_guard import (
    safe_connect, safe_disconnect, 
    disconnect_all, ConnectionTracker
)

# Connessione sicura (non fallisce se già connesso)
safe_connect(button.clicked, self.on_click)

# Disconnessione sicura (non fallisce se già disconnesso)
safe_disconnect(button.clicked, self.on_click)

# Tracking automatico delle connessioni
class MyView(QWidget):
    def __init__(self):
        super().__init__()
        self._tracker = ConnectionTracker()
        
        # Registra connessione
        self._tracker.connect(button.clicked, self.on_click)
        self._tracker.connect(worker.finished, self.on_done)
    
    def closeEvent(self, event):
        # Disconnette TUTTO in un colpo
        self._tracker.disconnect_all()
        super().closeEvent(event)
```

### Regole

1. **Mai** usare `signal.connect()` diretto in view complesse
2. **Sempre** disconnettere in `closeEvent`
3. **Usare** `ConnectionTracker` per view con molte connessioni
4. **Verificare** connessione unica con `Qt.ConnectionType.UniqueConnection`

---

## 4. Error Boundaries

### Problema Risolto
Un errore in una view causava il crash dell'intera applicazione.

### Modulo: `desktop_app/core/error_boundary.py`

```python
from desktop_app.core.error_boundary import (
    ErrorBoundary, ErrorContext, UIStateRecovery
)

class DatabaseView(QWidget):
    def __init__(self):
        super().__init__()
        self._error_boundary = ErrorBoundary(
            view_name="DatabaseView",
            on_error=self._handle_error,
            max_retries=3
        )
    
    def load_data(self):
        with self._error_boundary.protect():
            # Codice che potrebbe fallire
            data = self.api.get_certificati()
            self.table.setData(data)
    
    def _handle_error(self, error: Exception, context: ErrorContext):
        if context.retry_count < 3:
            # Mostra toast e riprova
            self.show_error_toast("Errore, riprovo...")
            context.should_retry = True
        else:
            # Fallback: mostra stato vuoto
            self.show_empty_state()
```

### UIStateRecovery

Salva e ripristina lo stato UI in caso di errore:

```python
recovery = UIStateRecovery()

# Salva stato corrente
recovery.save_state("table_scroll", self.table.verticalScrollBar().value())
recovery.save_state("selected_row", self.table.currentRow())

# Dopo recovery da errore, ripristina
scroll_pos = recovery.get_state("table_scroll", default=0)
self.table.verticalScrollBar().setValue(scroll_pos)
```

---

## 5. State Machine

### Problema Risolto
Le transizioni UI erano gestite ad-hoc, causando stati inconsistenti e race condition durante navigazione rapida.

### Modulo: `desktop_app/core/state_machine.py`

```python
from desktop_app.core.state_machine import (
    AppStateMachine, AppState, AppTransition
)

# Stati definiti
class AppState(Enum):
    INITIALIZING = auto()
    LOGIN = auto()
    LOADING = auto()
    MAIN = auto()
    ERROR = auto()
    SHUTDOWN = auto()

# Singleton state machine
state_machine = AppStateMachine.instance()

# Trigger transizione
state_machine.trigger(AppTransition.LOGIN_SUCCESS)

# Reagire a cambi di stato
state_machine.state_changed.connect(self._on_state_changed)

def _on_state_changed(self, old_state: AppState, new_state: AppState):
    if new_state == AppState.MAIN:
        self.show_dashboard()
    elif new_state == AppState.ERROR:
        self.show_error_view()
```

### Transizioni Valide

| Da | Trigger | A |
|---|---|---|
| INITIALIZING | INIT_COMPLETE | LOGIN |
| LOGIN | LOGIN_SUCCESS | LOADING |
| LOGIN | LOGIN_FAILED | ERROR |
| LOADING | LOAD_COMPLETE | MAIN |
| MAIN | LOGOUT | LOGIN |
| * | SHUTDOWN | SHUTDOWN |

### Vantaggi

- **Prevedibilità**: Solo transizioni valide sono permesse
- **Debugging**: Log di tutte le transizioni
- **Testing**: Facile simulare stati specifici

---

## 6. Observability (Sentry Integration)

### Modulo: `app/utils/sentry_integration.py`

```python
from app.utils.sentry_integration import (
    init_sentry,
    add_ui_breadcrumb,
    set_user_context,
    capture_view_error,
    add_state_breadcrumb
)

# Inizializzazione (in launcher.py)
init_sentry(
    dsn="https://xxx@sentry.io/xxx",
    environment="production",
    release="1.2.3"
)

# Breadcrumb per azioni UI
add_ui_breadcrumb("click", "LoginView", {"button": "login_btn"})

# Context utente (post-login)
set_user_context(user_id="123", username="admin")

# Cattura errore con context view
try:
    self.load_data()
except Exception as e:
    capture_view_error("DatabaseView", e, {"filter": self.current_filter})
```

### Filtri Automatici

- **Esclusi**: `ConnectionError`, `TimeoutError` (troppo comuni)
- **Context Qt**: Active window, focus widget automaticamente inclusi
- **Breadcrumbs**: Azioni UI e transizioni di stato tracciate

---

## 7. User Simulation Testing

### Location: `tests/desktop_app/simulation/`

Framework per testare la robustezza dell'applicazione simulando interazioni utente realistiche.

### UserSimulator

```python
from tests.desktop_app.simulation.user_actions import UserSimulator

def test_rapid_clicks(qtbot, login_view):
    sim = UserSimulator(qtbot)
    
    # Simula digitazione
    sim.type_text(username_input, "admin")
    sim.type_text(password_input, "password")
    
    # Simula click rapidi (stress test)
    for _ in range(10):
        sim.click(login_btn)
    
    # Attendi stabilizzazione
    sim.wait_for_animation()
    
    # Verifica no crash
    assert login_view.isVisible()
```

### Scenari di Test

1. **Login Scenarios**: Credenziali valide/invalide, click rapidi
2. **Navigation**: Cambio view rapido, keyboard navigation
3. **Stress Tests**: 100+ azioni random, resize continuo
4. **Animation Stress**: Animazioni concorrenti, chiusura durante animazione

### Esecuzione

```bash
# Tutti i test di simulazione
pytest tests/desktop_app/simulation/ -v --forked

# Solo stress test
pytest tests/desktop_app/simulation/test_stress.py -v --forked
```

---

## Checklist per Nuove View

Quando crei una nuova view, assicurati di:

- [ ] Estendere `SafeWidgetMixin`
- [ ] Usare `@guard_widget_access` su tutti gli slot
- [ ] Creare `ErrorBoundary` nel costruttore
- [ ] Usare `ConnectionTracker` per le connessioni
- [ ] Cancellare animazioni in `closeEvent`
- [ ] Aggiungere breadcrumb Sentry per azioni chiave
- [ ] Scrivere test di simulazione utente

---

## File Structure

```
desktop_app/
├── core/
│   ├── animation_manager.py    # Gestione animazioni
│   ├── error_boundary.py       # Error boundaries
│   ├── signal_guard.py         # Signal/slot safety
│   ├── state_machine.py        # App state machine
│   └── widget_guard.py         # Widget lifecycle
├── mixins/
│   └── safe_widget_mixin.py    # Mixin per widget sicuri
└── views/
    └── *.py                    # View refactored

tests/desktop_app/
├── core/
│   ├── test_animation_manager.py
│   ├── test_error_boundary.py
│   ├── test_signal_guard.py
│   ├── test_state_machine.py
│   └── test_widget_guard.py
├── mixins/
│   └── test_safe_widget_mixin.py
└── simulation/
    ├── conftest.py
    ├── user_actions.py
    ├── test_login_scenarios.py
    ├── test_navigation.py
    └── test_stress.py
```

---

## Riferimenti

- [FASE 0: Overview](crash_zero/FASE_0_OVERVIEW.md)
- [FASE 1: Widget Lifecycle](crash_zero/FASE_1_WIDGET_LIFECYCLE.md)
- [FASE 2: Animation Manager](crash_zero/FASE_2_ANIMATION_MANAGER.md)
- [FASE 3: Signal/Slot](crash_zero/FASE_3_SIGNAL_SLOT.md)
- [FASE 4: Error Boundaries](crash_zero/FASE_4_ERROR_BOUNDARIES.md)
- [FASE 5: State Machine](crash_zero/FASE_5_STATE_MACHINE.md)
- [FASE 6: Observability](crash_zero/FASE_6_OBSERVABILITY.md)
- [FASE 7: User Simulation](crash_zero/FASE_7_USER_SIMULATION.md)
