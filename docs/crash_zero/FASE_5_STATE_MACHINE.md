# 🔄 FASE 5: State Machine per Transizioni UI

## Obiettivo
Implementare una Qt State Machine per gestire le transizioni tra stati dell'applicazione (splash → login → dashboard → logout), garantendo che le transizioni siano sempre valide, atomiche e cancellabili.

---

## 📚 Background Tecnico

### Il Problema
Senza una state machine, le transizioni sono gestite ad-hoc:
- Nessuna validazione: si può passare da qualsiasi stato a qualsiasi altro
- Race condition: transizioni concorrenti possono causare stati inconsistenti
- Difficile debugging: non c'è log centralizzato delle transizioni
- Animazioni non coordinate con cambi di stato

```python
# Problematico: transizioni dirette
def on_login_success(self):
    self.fade_out_login()  # Inizia animazione
    # Se l'utente clicca logout durante l'animazione?
    self.show_dashboard()  # Stato inconsistente!
```

### Soluzione: Qt State Machine
- Stati espliciti con transizioni validate
- Una sola transizione alla volta
- Animazioni legate a transizioni di stato
- Logging e debugging centralizzato

---

## 🏗️ Architettura

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Application State Machine                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────┐    ┌─────────┐    ┌──────────────┐    ┌───────────┐  │
│  │  INIT   │───▶│ SPLASH  │───▶│    LOGIN     │───▶│   MAIN    │  │
│  └─────────┘    └─────────┘    └──────────────┘    └───────────┘  │
│                                       │                   │        │
│                                       │                   │        │
│                                       ▼                   ▼        │
│                              ┌──────────────┐    ┌───────────┐    │
│                              │AUTHENTICATING│    │  LOGOUT   │    │
│                              └──────────────┘    └───────────┘    │
│                                       │                   │        │
│                                       └───────────────────┘        │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                       ERROR STATE                            │   │
│  │  (raggiungibile da qualsiasi stato in caso di errore)       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📁 File da Creare

### 1. `desktop_app/core/app_state_machine.py`

```python
"""
Application State Machine - Gestione centralizzata degli stati dell'app.

Implementa una macchina a stati finiti per gestire:
- Transizioni tra schermate (splash → login → main)
- Validazione transizioni
- Coordinamento con animazioni
- Logging e debugging

Uso tipico:
    from desktop_app.core.app_state_machine import get_state_machine, AppState
    
    sm = get_state_machine()
    sm.state_changed.connect(on_state_changed)
    sm.start()
    
    # Trigger transizione
    sm.trigger(AppTransition.LOGIN_SUCCESS)
"""

from __future__ import annotations

import logging
from enum import Enum, auto
from typing import Optional, Dict, Set, Callable, Any
from dataclasses import dataclass
from datetime import datetime

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtStateMachine import QState, QStateMachine, QSignalTransition

logger = logging.getLogger(__name__)


# === Stati dell'Applicazione ===

class AppState(Enum):
    """
    Stati possibili dell'applicazione.
    
    Il flusso normale è:
    INITIALIZING → SPLASH → LOGIN → AUTHENTICATING → TRANSITIONING → MAIN
    
    Da MAIN si può tornare a LOGIN (logout) o andare in ERROR.
    """
    INITIALIZING = auto()    # App in avvio, caricamento risorse
    SPLASH = auto()          # Splash screen visibile
    LOGIN = auto()           # Schermata login, attesa input utente
    AUTHENTICATING = auto()  # Login in corso, chiamata API
    TRANSITIONING = auto()   # Transizione animata tra view
    MAIN = auto()            # App principale (dashboard)
    ERROR = auto()           # Stato di errore critico
    SHUTTING_DOWN = auto()   # App in chiusura


class AppTransition(Enum):
    """
    Transizioni possibili tra stati.
    
    Ogni transizione ha uno stato sorgente e uno destinazione.
    """
    # Avvio
    INIT_COMPLETE = auto()       # INITIALIZING → SPLASH
    SPLASH_DONE = auto()         # SPLASH → LOGIN
    
    # Autenticazione
    LOGIN_SUBMIT = auto()        # LOGIN → AUTHENTICATING
    LOGIN_SUCCESS = auto()       # AUTHENTICATING → TRANSITIONING
    LOGIN_FAILED = auto()        # AUTHENTICATING → LOGIN
    
    # Transizione
    TRANSITION_COMPLETE = auto() # TRANSITIONING → MAIN
    
    # Logout
    LOGOUT_REQUEST = auto()      # MAIN → LOGIN
    
    # Errori
    ERROR_OCCURRED = auto()      # ANY → ERROR
    ERROR_RECOVERED = auto()     # ERROR → LOGIN
    
    # Shutdown
    SHUTDOWN_REQUEST = auto()    # ANY → SHUTTING_DOWN


# === Configurazione Transizioni ===

@dataclass
class TransitionConfig:
    """Configurazione di una transizione."""
    from_state: AppState
    to_state: AppState
    transition: AppTransition
    requires_animation: bool = False
    animation_duration_ms: int = 300


# Mappa delle transizioni valide
VALID_TRANSITIONS: Dict[AppTransition, TransitionConfig] = {
    AppTransition.INIT_COMPLETE: TransitionConfig(
        AppState.INITIALIZING, AppState.SPLASH, AppTransition.INIT_COMPLETE
    ),
    AppTransition.SPLASH_DONE: TransitionConfig(
        AppState.SPLASH, AppState.LOGIN, AppTransition.SPLASH_DONE,
        requires_animation=True, animation_duration_ms=500
    ),
    AppTransition.LOGIN_SUBMIT: TransitionConfig(
        AppState.LOGIN, AppState.AUTHENTICATING, AppTransition.LOGIN_SUBMIT
    ),
    AppTransition.LOGIN_SUCCESS: TransitionConfig(
        AppState.AUTHENTICATING, AppState.TRANSITIONING, AppTransition.LOGIN_SUCCESS,
        requires_animation=True, animation_duration_ms=300
    ),
    AppTransition.LOGIN_FAILED: TransitionConfig(
        AppState.AUTHENTICATING, AppState.LOGIN, AppTransition.LOGIN_FAILED
    ),
    AppTransition.TRANSITION_COMPLETE: TransitionConfig(
        AppState.TRANSITIONING, AppState.MAIN, AppTransition.TRANSITION_COMPLETE
    ),
    AppTransition.LOGOUT_REQUEST: TransitionConfig(
        AppState.MAIN, AppState.LOGIN, AppTransition.LOGOUT_REQUEST,
        requires_animation=True, animation_duration_ms=300
    ),
    AppTransition.ERROR_RECOVERED: TransitionConfig(
        AppState.ERROR, AppState.LOGIN, AppTransition.ERROR_RECOVERED
    ),
}


# === State Machine ===

class AppStateMachine(QObject):
    """
    State Machine principale dell'applicazione.
    
    Gestisce tutti gli stati e le transizioni dell'app,
    garantendo che solo transizioni valide siano eseguite.
    
    Signals:
        state_changed(AppState, AppState): Emesso quando lo stato cambia (old, new)
        state_entered(AppState): Emesso quando si entra in uno stato
        state_exited(AppState): Emesso quando si esce da uno stato
        transition_started(AppTransition): Emesso all'inizio di una transizione
        transition_completed(AppTransition): Emesso alla fine di una transizione
        transition_failed(AppTransition, str): Emesso se una transizione fallisce
    """
    
    # Signals
    state_changed = pyqtSignal(object, object)  # AppState, AppState
    state_entered = pyqtSignal(object)  # AppState
    state_exited = pyqtSignal(object)  # AppState
    transition_started = pyqtSignal(object)  # AppTransition
    transition_completed = pyqtSignal(object)  # AppTransition
    transition_failed = pyqtSignal(object, str)  # AppTransition, error
    
    # Internal signals per trigger
    _trigger_init_complete = pyqtSignal()
    _trigger_splash_done = pyqtSignal()
    _trigger_login_submit = pyqtSignal()
    _trigger_login_success = pyqtSignal()
    _trigger_login_failed = pyqtSignal()
    _trigger_transition_complete = pyqtSignal()
    _trigger_logout = pyqtSignal()
    _trigger_error = pyqtSignal()
    _trigger_recovery = pyqtSignal()
    _trigger_shutdown = pyqtSignal()
    
    # Singleton
    _instance: Optional['AppStateMachine'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        super().__init__()
        self._initialized = True
        
        self._current_state = AppState.INITIALIZING
        self._previous_state: Optional[AppState] = None
        self._is_transitioning = False
        self._transition_history: list = []
        
        self._machine = QStateMachine(self)
        self._states: Dict[AppState, QState] = {}
        self._trigger_signals: Dict[AppTransition, pyqtSignal] = {}
        
        self._setup_states()
        self._setup_transitions()
        self._setup_trigger_map()
        
        logger.info("AppStateMachine initialized")
    
    def _setup_states(self):
        """Crea gli stati Qt."""
        for app_state in AppState:
            state = QState()
            state.setObjectName(app_state.name)
            
            # Connetti entry/exit
            state.entered.connect(
                lambda checked=False, s=app_state: self._on_state_entered(s)
            )
            state.exited.connect(
                lambda checked=False, s=app_state: self._on_state_exited(s)
            )
            
            self._states[app_state] = state
            self._machine.addState(state)
        
        # Stato iniziale
        self._machine.setInitialState(self._states[AppState.INITIALIZING])
    
    def _setup_transitions(self):
        """Configura le transizioni tra stati."""
        # Mappa transizioni a segnali interni
        transition_signals = {
            AppTransition.INIT_COMPLETE: self._trigger_init_complete,
            AppTransition.SPLASH_DONE: self._trigger_splash_done,
            AppTransition.LOGIN_SUBMIT: self._trigger_login_submit,
            AppTransition.LOGIN_SUCCESS: self._trigger_login_success,
            AppTransition.LOGIN_FAILED: self._trigger_login_failed,
            AppTransition.TRANSITION_COMPLETE: self._trigger_transition_complete,
            AppTransition.LOGOUT_REQUEST: self._trigger_logout,
            AppTransition.ERROR_OCCURRED: self._trigger_error,
            AppTransition.ERROR_RECOVERED: self._trigger_recovery,
            AppTransition.SHUTDOWN_REQUEST: self._trigger_shutdown,
        }
        
        self._trigger_signals = transition_signals
        
        # Aggiungi transizioni configurate
        for trans, config in VALID_TRANSITIONS.items():
            from_state = self._states[config.from_state]
            to_state = self._states[config.to_state]
            signal = transition_signals.get(trans)
            
            if signal:
                from_state.addTransition(signal, to_state)
        
        # ERROR è raggiungibile da tutti gli stati (tranne SHUTTING_DOWN)
        error_state = self._states[AppState.ERROR]
        for app_state in AppState:
            if app_state not in (AppState.ERROR, AppState.SHUTTING_DOWN):
                self._states[app_state].addTransition(
                    self._trigger_error, error_state
                )
        
        # SHUTTING_DOWN è raggiungibile da tutti
        shutdown_state = self._states[AppState.SHUTTING_DOWN]
        for app_state in AppState:
            if app_state != AppState.SHUTTING_DOWN:
                self._states[app_state].addTransition(
                    self._trigger_shutdown, shutdown_state
                )
    
    def _setup_trigger_map(self):
        """Mappa transizioni a metodi trigger."""
        self._trigger_map = {
            AppTransition.INIT_COMPLETE: self._trigger_init_complete.emit,
            AppTransition.SPLASH_DONE: self._trigger_splash_done.emit,
            AppTransition.LOGIN_SUBMIT: self._trigger_login_submit.emit,
            AppTransition.LOGIN_SUCCESS: self._trigger_login_success.emit,
            AppTransition.LOGIN_FAILED: self._trigger_login_failed.emit,
            AppTransition.TRANSITION_COMPLETE: self._trigger_transition_complete.emit,
            AppTransition.LOGOUT_REQUEST: self._trigger_logout.emit,
            AppTransition.ERROR_OCCURRED: self._trigger_error.emit,
            AppTransition.ERROR_RECOVERED: self._trigger_recovery.emit,
            AppTransition.SHUTDOWN_REQUEST: self._trigger_shutdown.emit,
        }
    
    def _on_state_entered(self, state: AppState):
        """Callback quando si entra in uno stato."""
        self._previous_state = self._current_state
        self._current_state = state
        self._is_transitioning = False
        
        logger.info(f"State entered: {state.name}")
        
        self.state_entered.emit(state)
        self.state_changed.emit(self._previous_state, state)
        
        # Registra nella history
        self._transition_history.append({
            'timestamp': datetime.now().isoformat(),
            'from': self._previous_state.name if self._previous_state else None,
            'to': state.name
        })
        
        # Mantieni solo ultimi 100
        if len(self._transition_history) > 100:
            self._transition_history.pop(0)
    
    def _on_state_exited(self, state: AppState):
        """Callback quando si esce da uno stato."""
        logger.debug(f"State exited: {state.name}")
        self.state_exited.emit(state)
    
    # === Public API ===
    
    @classmethod
    def instance(cls) -> 'AppStateMachine':
        """Ottiene l'istanza singleton."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def start(self):
        """Avvia la state machine."""
        logger.info("Starting AppStateMachine")
        self._machine.start()
    
    def stop(self):
        """Ferma la state machine."""
        logger.info("Stopping AppStateMachine")
        self._machine.stop()
    
    def current_state(self) -> AppState:
        """Ritorna lo stato corrente."""
        return self._current_state
    
    def previous_state(self) -> Optional[AppState]:
        """Ritorna lo stato precedente."""
        return self._previous_state
    
    def is_transitioning(self) -> bool:
        """Verifica se una transizione è in corso."""
        return self._is_transitioning
    
    def trigger(self, transition: AppTransition) -> bool:
        """
        Triggera una transizione.
        
        Args:
            transition: La transizione da eseguire
            
        Returns:
            True se la transizione è stata accettata
        """
        # Valida transizione
        if not self.can_transition(transition):
            logger.warning(
                f"Invalid transition {transition.name} from state {self._current_state.name}"
            )
            self.transition_failed.emit(
                transition, 
                f"Cannot transition from {self._current_state.name}"
            )
            return False
        
        # Verifica se già in transizione
        if self._is_transitioning:
            logger.warning(f"Already transitioning, ignoring {transition.name}")
            return False
        
        logger.info(f"Triggering transition: {transition.name}")
        self._is_transitioning = True
        self.transition_started.emit(transition)
        
        # Esegui trigger
        trigger_fn = self._trigger_map.get(transition)
        if trigger_fn:
            trigger_fn()
            self.transition_completed.emit(transition)
            return True
        
        return False
    
    def can_transition(self, transition: AppTransition) -> bool:
        """
        Verifica se una transizione è valida dallo stato corrente.
        
        Args:
            transition: La transizione da verificare
            
        Returns:
            True se la transizione è permessa
        """
        # Transizioni speciali sempre permesse
        if transition in (AppTransition.ERROR_OCCURRED, AppTransition.SHUTDOWN_REQUEST):
            return True
        
        config = VALID_TRANSITIONS.get(transition)
        if not config:
            return False
        
        return config.from_state == self._current_state
    
    def get_valid_transitions(self) -> Set[AppTransition]:
        """Ritorna le transizioni valide dallo stato corrente."""
        valid = set()
        for trans, config in VALID_TRANSITIONS.items():
            if config.from_state == self._current_state:
                valid.add(trans)
        
        # Aggiungi transizioni sempre valide
        valid.add(AppTransition.ERROR_OCCURRED)
        valid.add(AppTransition.SHUTDOWN_REQUEST)
        
        return valid
    
    def get_history(self) -> list:
        """Ritorna la storia delle transizioni."""
        return self._transition_history.copy()
    
    # === Convenience Methods ===
    
    def trigger_init_complete(self):
        """Shortcut: Inizializzazione completata."""
        return self.trigger(AppTransition.INIT_COMPLETE)
    
    def trigger_splash_done(self):
        """Shortcut: Splash completato."""
        return self.trigger(AppTransition.SPLASH_DONE)
    
    def trigger_login_submit(self):
        """Shortcut: Form login inviato."""
        return self.trigger(AppTransition.LOGIN_SUBMIT)
    
    def trigger_login_success(self):
        """Shortcut: Login riuscito."""
        return self.trigger(AppTransition.LOGIN_SUCCESS)
    
    def trigger_login_failed(self):
        """Shortcut: Login fallito."""
        return self.trigger(AppTransition.LOGIN_FAILED)
    
    def trigger_transition_complete(self):
        """Shortcut: Transizione animata completata."""
        return self.trigger(AppTransition.TRANSITION_COMPLETE)
    
    def trigger_logout(self):
        """Shortcut: Richiesta logout."""
        return self.trigger(AppTransition.LOGOUT_REQUEST)
    
    def trigger_error(self):
        """Shortcut: Errore critico."""
        return self.trigger(AppTransition.ERROR_OCCURRED)
    
    def trigger_recovery(self):
        """Shortcut: Recovery da errore."""
        return self.trigger(AppTransition.ERROR_RECOVERED)
    
    def trigger_shutdown(self):
        """Shortcut: Richiesta shutdown."""
        return self.trigger(AppTransition.SHUTDOWN_REQUEST)


# === Singleton Accessor ===

def get_state_machine() -> AppStateMachine:
    """Ottiene l'istanza singleton della state machine."""
    return AppStateMachine.instance()
```

---

### 2. `tests/desktop_app/core/test_state_machine.py`

```python
"""
Test per AppStateMachine.
"""

import pytest
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication
import sys


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def state_machine(qapp):
    """Crea una nuova istanza per ogni test."""
    from desktop_app.core.app_state_machine import AppStateMachine
    
    # Reset singleton per test isolation
    AppStateMachine._instance = None
    sm = AppStateMachine()
    sm.start()
    
    yield sm
    
    sm.stop()
    AppStateMachine._instance = None


class TestAppStateMachine:
    """Test per la state machine."""
    
    def test_initial_state(self, state_machine):
        """Test stato iniziale."""
        from desktop_app.core.app_state_machine import AppState
        
        assert state_machine.current_state() == AppState.INITIALIZING
    
    def test_valid_transition(self, state_machine, qtbot):
        """Test transizione valida."""
        from desktop_app.core.app_state_machine import AppState, AppTransition
        
        # INITIALIZING → SPLASH
        result = state_machine.trigger(AppTransition.INIT_COMPLETE)
        qtbot.wait(100)  # Processa eventi
        
        assert result is True
        assert state_machine.current_state() == AppState.SPLASH
    
    def test_invalid_transition(self, state_machine, qtbot):
        """Test transizione non valida."""
        from desktop_app.core.app_state_machine import AppTransition
        
        # Da INITIALIZING non si può andare direttamente a LOGIN_SUCCESS
        result = state_machine.trigger(AppTransition.LOGIN_SUCCESS)
        
        assert result is False
    
    def test_full_login_flow(self, state_machine, qtbot):
        """Test flusso completo di login."""
        from desktop_app.core.app_state_machine import AppState, AppTransition
        
        transitions = [
            (AppTransition.INIT_COMPLETE, AppState.SPLASH),
            (AppTransition.SPLASH_DONE, AppState.LOGIN),
            (AppTransition.LOGIN_SUBMIT, AppState.AUTHENTICATING),
            (AppTransition.LOGIN_SUCCESS, AppState.TRANSITIONING),
            (AppTransition.TRANSITION_COMPLETE, AppState.MAIN),
        ]
        
        for trans, expected_state in transitions:
            state_machine.trigger(trans)
            qtbot.wait(50)
            assert state_machine.current_state() == expected_state, \
                f"After {trans.name}, expected {expected_state.name}, got {state_machine.current_state().name}"
    
    def test_error_from_any_state(self, state_machine, qtbot):
        """Test che ERROR sia raggiungibile da qualsiasi stato."""
        from desktop_app.core.app_state_machine import AppState, AppTransition
        
        # Vai a LOGIN
        state_machine.trigger(AppTransition.INIT_COMPLETE)
        state_machine.trigger(AppTransition.SPLASH_DONE)
        qtbot.wait(100)
        
        assert state_machine.current_state() == AppState.LOGIN
        
        # Trigger errore
        result = state_machine.trigger(AppTransition.ERROR_OCCURRED)
        qtbot.wait(50)
        
        assert result is True
        assert state_machine.current_state() == AppState.ERROR
    
    def test_history(self, state_machine, qtbot):
        """Test registrazione storia transizioni."""
        from desktop_app.core.app_state_machine import AppTransition
        
        state_machine.trigger(AppTransition.INIT_COMPLETE)
        state_machine.trigger(AppTransition.SPLASH_DONE)
        qtbot.wait(100)
        
        history = state_machine.get_history()
        
        assert len(history) >= 2
        assert history[-1]['to'] == 'LOGIN'
    
    def test_state_changed_signal(self, state_machine, qtbot):
        """Test emissione segnale state_changed."""
        from desktop_app.core.app_state_machine import AppTransition
        
        callback = MagicMock()
        state_machine.state_changed.connect(callback)
        
        state_machine.trigger(AppTransition.INIT_COMPLETE)
        qtbot.wait(100)
        
        assert callback.called
    
    def test_can_transition(self, state_machine, qtbot):
        """Test verifica transizioni valide."""
        from desktop_app.core.app_state_machine import AppTransition
        
        # Da INITIALIZING
        assert state_machine.can_transition(AppTransition.INIT_COMPLETE) is True
        assert state_machine.can_transition(AppTransition.LOGIN_SUCCESS) is False
        
        # ERROR sempre valido
        assert state_machine.can_transition(AppTransition.ERROR_OCCURRED) is True
```

---

## 📝 Istruzioni di Implementazione

### Step 1: Crea app_state_machine.py
Copia il codice in `desktop_app/core/app_state_machine.py`.

### Step 2: Integra nel Main Controller
Modifica `desktop_app/main.py`:

```python
from desktop_app.core.app_state_machine import (
    get_state_machine, AppState, AppTransition
)

class ApplicationController:
    def __init__(self):
        # ... altro codice ...
        
        # Setup State Machine
        self._state_machine = get_state_machine()
        self._state_machine.state_changed.connect(self._on_state_changed)
        self._state_machine.start()
    
    def _on_state_changed(self, old_state: AppState, new_state: AppState):
        """Gestisce i cambi di stato."""
        logger.info(f"App state: {old_state.name} → {new_state.name}")
        
        handlers = {
            AppState.SPLASH: self._enter_splash,
            AppState.LOGIN: self._enter_login,
            AppState.AUTHENTICATING: self._enter_authenticating,
            AppState.TRANSITIONING: self._enter_transitioning,
            AppState.MAIN: self._enter_main,
            AppState.ERROR: self._enter_error,
            AppState.SHUTTING_DOWN: self._enter_shutdown,
        }
        
        handler = handlers.get(new_state)
        if handler:
            handler()
    
    def _enter_splash(self):
        self._show_splash_screen()
    
    def _enter_login(self):
        # Cancella animazioni precedenti
        animation_manager.cancel_all(owner=self)
        self._show_login_view()
    
    def _enter_authenticating(self):
        # Mostra loading nella login view
        if hasattr(self, 'login_view'):
            self.login_view.show_loading()
    
    def _enter_transitioning(self):
        # Animazione di transizione
        fade_out(
            self.login_view,
            on_finished=self._state_machine.trigger_transition_complete
        )
    
    def _enter_main(self):
        # Pulisci vecchia view
        if hasattr(self, 'login_view'):
            self.login_view.deleteLater()
        
        self._show_main_window()
    
    def _enter_error(self):
        self._show_error_dialog()
    
    def _enter_shutdown(self):
        self._cleanup_and_exit()
```

### Step 3: Modifica Login View
La login view non gestisce più le transizioni direttamente:

```python
class LoginView(SafeWidgetMixin, ErrorBoundaryMixin, QWidget):
    # Segnali per comunicare con il controller
    login_requested = pyqtSignal(str, str)  # username, password
    
    def _on_login_click(self):
        username = self.get_child('username_input').text()
        password = self.get_child('password_input').text()
        
        # Emetti segnale, il controller gestirà la state machine
        self.login_requested.emit(username, password)
    
    # NON più:
    # def _on_login_success(self):
    #     self._animate_exit()  # ❌ La view non deve gestire transizioni
```

### Step 4: Test
```bash
pytest tests/desktop_app/core/test_state_machine.py -v
```

---

## ✅ Checklist di Completamento

- [ ] `desktop_app/core/app_state_machine.py` creato
- [ ] Test passano
- [ ] `main.py` integrato con state machine
- [ ] Login view usa segnali invece di transizioni dirette
- [ ] Splash screen triggera `SPLASH_DONE`
- [ ] Animazioni coordinate con transizioni
- [ ] Logging delle transizioni funziona

---

## ⏭️ Prossimo Step

Completata questa fase, procedi con **FASE 6: Observability** (`FASE_6_OBSERVABILITY.md`).
