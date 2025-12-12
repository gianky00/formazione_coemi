"""
Application State Machine - Gestione centralizzata degli stati dell'app.

CRASH ZERO FASE 5 - State Machine per Transizioni UI

Implementa una macchina a stati finiti per gestire:
- Transizioni tra schermate (splash → login → main)
- Validazione transizioni
- Coordinamento con animazioni
- Logging e debugging

Uso tipico:
    from desktop_app.core.state_machine import get_state_machine, AppState
    
    sm = get_state_machine()
    sm.state_changed.connect(on_state_changed)
    sm.start()
    
    # Trigger transizione
    sm.trigger(AppTransition.LOGIN_SUCCESS)
"""

from __future__ import annotations

import logging
from enum import Enum, auto
from typing import Optional, Dict, Set
from dataclasses import dataclass
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal

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
    
    Questa implementazione usa una semplice macchina a stati
    basata su dizionario invece di Qt StateMachine per massima
    compatibilità.
    
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
    
    # Singleton
    _instance: Optional['AppStateMachine'] = None
    
    def __init__(self):
        super().__init__()
        
        self._current_state = AppState.INITIALIZING
        self._previous_state: Optional[AppState] = None
        self._is_transitioning = False
        self._is_started = False
        self._transition_history: list = []
        
        logger.info("AppStateMachine initialized")
    
    # === Public API ===
    
    @classmethod
    def instance(cls) -> 'AppStateMachine':
        """Ottiene l'istanza singleton."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Resetta l'istanza singleton (per test)."""
        cls._instance = None
    
    def start(self):
        """Avvia la state machine."""
        logger.info("Starting AppStateMachine")
        self._is_started = True
        self._current_state = AppState.INITIALIZING
    
    def stop(self):
        """Ferma la state machine."""
        logger.info("Stopping AppStateMachine")
        self._is_started = False
    
    def is_running(self) -> bool:
        """Verifica se la state machine è attiva."""
        return self._is_started
    
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
        if not self._is_started:
            logger.warning(f"State machine not started, ignoring {transition.name}")
            return False
        
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
        
        # Determina il nuovo stato
        new_state = self._get_target_state(transition)
        if new_state is None:
            self._is_transitioning = False
            return False
        
        # Esegui transizione
        self._execute_transition(new_state)
        self.transition_completed.emit(transition)
        
        return True
    
    def _get_target_state(self, transition: AppTransition) -> Optional[AppState]:
        """Determina lo stato di destinazione per una transizione."""
        # Transizioni speciali
        if transition == AppTransition.ERROR_OCCURRED:
            return AppState.ERROR
        if transition == AppTransition.SHUTDOWN_REQUEST:
            return AppState.SHUTTING_DOWN
        
        # Transizioni normali
        config = VALID_TRANSITIONS.get(transition)
        if config:
            return config.to_state
        
        return None
    
    def _execute_transition(self, new_state: AppState):
        """Esegue la transizione effettiva."""
        old_state = self._current_state
        
        # Exit dal vecchio stato
        self.state_exited.emit(old_state)
        logger.debug(f"State exited: {old_state.name}")
        
        # Aggiorna stato
        self._previous_state = old_state
        self._current_state = new_state
        self._is_transitioning = False
        
        # Entry nel nuovo stato
        self.state_entered.emit(new_state)
        logger.info(f"State entered: {new_state.name}")
        
        # Emetti state_changed
        self.state_changed.emit(old_state, new_state)
        
        # Registra nella history
        self._record_transition(old_state, new_state)
    
    def _record_transition(self, old_state: AppState, new_state: AppState):
        """Registra una transizione nella history."""
        self._transition_history.append({
            'timestamp': datetime.now().isoformat(),
            'from': old_state.name if old_state else None,
            'to': new_state.name
        })
        
        # Mantieni solo ultimi 100
        if len(self._transition_history) > 100:
            self._transition_history.pop(0)
    
    def can_transition(self, transition: AppTransition) -> bool:
        """
        Verifica se una transizione è valida dallo stato corrente.
        
        Args:
            transition: La transizione da verificare
            
        Returns:
            True se la transizione è permessa
        """
        # Transizioni speciali sempre permesse (tranne da SHUTTING_DOWN)
        if transition == AppTransition.SHUTDOWN_REQUEST:
            return self._current_state != AppState.SHUTTING_DOWN
        
        if transition == AppTransition.ERROR_OCCURRED:
            return self._current_state not in (AppState.ERROR, AppState.SHUTTING_DOWN)
        
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
        if self._current_state not in (AppState.ERROR, AppState.SHUTTING_DOWN):
            valid.add(AppTransition.ERROR_OCCURRED)
        if self._current_state != AppState.SHUTTING_DOWN:
            valid.add(AppTransition.SHUTDOWN_REQUEST)
        
        return valid
    
    def get_history(self) -> list:
        """Ritorna la storia delle transizioni."""
        return self._transition_history.copy()
    
    # === Convenience Methods ===
    
    def trigger_init_complete(self) -> bool:
        """Shortcut: Inizializzazione completata."""
        return self.trigger(AppTransition.INIT_COMPLETE)
    
    def trigger_splash_done(self) -> bool:
        """Shortcut: Splash completato."""
        return self.trigger(AppTransition.SPLASH_DONE)
    
    def trigger_login_submit(self) -> bool:
        """Shortcut: Form login inviato."""
        return self.trigger(AppTransition.LOGIN_SUBMIT)
    
    def trigger_login_success(self) -> bool:
        """Shortcut: Login riuscito."""
        return self.trigger(AppTransition.LOGIN_SUCCESS)
    
    def trigger_login_failed(self) -> bool:
        """Shortcut: Login fallito."""
        return self.trigger(AppTransition.LOGIN_FAILED)
    
    def trigger_transition_complete(self) -> bool:
        """Shortcut: Transizione animata completata."""
        return self.trigger(AppTransition.TRANSITION_COMPLETE)
    
    def trigger_logout(self) -> bool:
        """Shortcut: Richiesta logout."""
        return self.trigger(AppTransition.LOGOUT_REQUEST)
    
    def trigger_error(self) -> bool:
        """Shortcut: Errore critico."""
        return self.trigger(AppTransition.ERROR_OCCURRED)
    
    def trigger_recovery(self) -> bool:
        """Shortcut: Recovery da errore."""
        return self.trigger(AppTransition.ERROR_RECOVERED)
    
    def trigger_shutdown(self) -> bool:
        """Shortcut: Richiesta shutdown."""
        return self.trigger(AppTransition.SHUTDOWN_REQUEST)


# === Singleton Accessor ===

def get_state_machine() -> AppStateMachine:
    """Ottiene l'istanza singleton della state machine."""
    return AppStateMachine.instance()


__all__ = [
    'AppState',
    'AppTransition',
    'AppStateMachine',
    'TransitionConfig',
    'VALID_TRANSITIONS',
    'get_state_machine',
]
