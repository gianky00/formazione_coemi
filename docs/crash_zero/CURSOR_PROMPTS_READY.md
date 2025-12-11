# 🤖 CURSOR PROMPTS READY - Progetto Crash Zero

Questo file contiene prompt ottimizzati per Cursor con Claude Opus 4.5, pronti per essere copiati e usati fase per fase.

---

## 📋 Istruzioni per l'Uso

1. **Copia il prompt** della fase corrente
2. **Incolla in Cursor** (chat o composer)
3. **Attendi il completamento** 
4. **Verifica con i test** indicati
5. **Procedi alla fase successiva**

---

## 🎯 PROMPT MASTER (Da Usare All'Inizio)

```
Sei un senior software engineer esperto in PyQt6 e architettura software enterprise.

CONTESTO PROGETTO:
- Applicazione: Intelleo - Gestione certificati sicurezza sul lavoro
- Stack: PyQt6 (desktop) + FastAPI (backend) + React (guide embedded)
- Build: Nuitka
- Problema: Crash sporadici causati da Widget Lifecycle Violations

OBIETTIVO:
Implementare il progetto "Crash Zero" per eliminare completamente ogni possibilità di crash.

PRIORITÀ:
1. Robustezza (Zero crash)
2. Performance 
3. UX/UI
4. Maintainability

REGOLE:
- Leggi SEMPRE i file esistenti prima di modificarli
- Non rompere test esistenti
- Crea test per ogni nuovo componente
- Usa typing hints ovunque
- Commenti in italiano per business logic, inglese per codice tecnico
- Segui PEP 8

DOCUMENTAZIONE DI RIFERIMENTO:
- docs/DESKTOP_CLIENT.md
- docs/SYSTEM_ARCHITECTURE.md
- docs/CONTRIBUTING.md

Conferma di aver compreso il contesto rispondendo "PRONTO PER CRASH ZERO".
```

---

## 📦 FASE 1: Widget Lifecycle Guard

### Prompt 1.1 - Analisi Iniziale
```
FASE 1: Widget Lifecycle Guard - Analisi

Analizza i seguenti file per identificare tutti i pattern di accesso a widget che potrebbero causare crash:

1. desktop_app/views/login_view.py
2. desktop_app/components/animated_widgets.py
3. desktop_app/components/animated_stacked_widget.py
4. desktop_app/main.py

Per ogni file, elenca:
- Metodi che accedono a widget (self.xxx)
- Metodi che creano animazioni
- Metodi chiamati durante transizioni
- Potenziali race condition

Output atteso: Tabella con [File, Metodo, Rischio, Motivo]
```

### Prompt 1.2 - Creazione Widget Guard
```
FASE 1: Widget Lifecycle Guard - Implementazione

Crea il file desktop_app/core/widget_guard.py con:

1. Funzione `is_widget_alive(widget) -> bool`:
   - Verifica che widget non sia None
   - Verifica che l'oggetto C++ sottostante esista
   - Usa try/except per gestire sip.isdeleted() o equivalente PyQt6
   
2. Decorator `@guard_widget_access`:
   - Wrappa metodi che accedono a widget
   - Se widget è distrutto, logga warning e return silenzioso
   - Non deve mai sollevare eccezioni

3. Class `WidgetRef`:
   - Wrapper con weak reference a widget
   - Metodo `get()` che ritorna widget o None
   - Metodo `is_alive()` -> bool

4. Context manager `safe_widget_context(widget)`:
   - Verifica widget all'ingresso
   - Gestisce eccezioni
   - Logga se widget distrutto durante operazione

Includi:
- Type hints completi
- Docstrings in italiano
- Logging appropriato
- Test unitari in tests/desktop_app/core/test_widget_guard.py
```

### Prompt 1.3 - Creazione Safe Widget Mixin
```
FASE 1: Widget Lifecycle Guard - SafeWidgetMixin

Crea il file desktop_app/mixins/safe_widget_mixin.py con:

class SafeWidgetMixin:
    """
    Mixin che aggiunge protezione lifecycle a qualsiasi QWidget.
    Da usare come prima classe base: class MyView(SafeWidgetMixin, QWidget)
    """
    
    Implementa:
    1. `_is_destroying: bool` - Flag per tracciare stato distruzione
    2. `_safe_refs: Dict[str, WidgetRef]` - Riferimenti sicuri a child widget
    
    3. `register_child(name: str, widget: QWidget)`:
       - Registra widget figlio con WidgetRef
       
    4. `get_child(name: str) -> Optional[QWidget]`:
       - Ritorna widget se ancora vivo, None altrimenti
       
    5. `safe_call(method: Callable, *args, **kwargs)`:
       - Esegue metodo solo se widget è ancora vivo
       
    6. Override `deleteLater()`:
       - Setta _is_destroying = True prima di chiamare super()
       
    7. Override `closeEvent(event)`:
       - Cleanup di tutti i riferimenti
       - Cancella animazioni pendenti

Crea test in tests/desktop_app/mixins/test_safe_widget_mixin.py
```

### Prompt 1.4 - Applicazione a Login View
```
FASE 1: Widget Lifecycle Guard - Refactoring Login View

Modifica desktop_app/views/login_view.py:

1. Aggiungi SafeWidgetMixin come prima classe base

2. Nel metodo __init__:
   - Registra tutti i widget importanti con register_child()
   - Es: self.register_child('login_btn', self.login_btn)
   - Es: self.register_child('container', self.container)

3. Nel metodo _animate_success_exit():
   - Usa get_child() invece di accesso diretto
   - Verifica esistenza prima di creare QGraphicsOpacityEffect
   
   PRIMA:
   self.opacity_effect = QGraphicsOpacityEffect(self.container)
   
   DOPO:
   container = self.get_child('container')
   if container:
       self.opacity_effect = QGraphicsOpacityEffect(container)
   else:
       self._transition_without_animation()

4. Nel metodo _on_login_error():
   - Usa safe_call() per operazioni su widget
   
   PRIMA:
   self.login_btn.set_loading(False)
   
   DOPO:
   self.safe_call(lambda: self.get_child('login_btn')?.set_loading(False))

5. Aggiungi metodo _transition_without_animation():
   - Fallback se animazione non possibile
   - Emette segnale di transizione completata

Verifica che pytest tests/desktop_app/views/test_login_view*.py passi alla FASE 2: Animation Manager 
```

---

## 🎬 FASE 2: Animation Manager

### Prompt 2.1 - Analisi Animazioni Esistenti
```
FASE 2: Animation Manager - Analisi

Cerca in tutto il repository desktop_app/ tutti gli usi di:
- QPropertyAnimation
- QSequentialAnimationGroup
- QParallelAnimationGroup
- QGraphicsOpacityEffect
- QTimer (usati per animazioni)

Per ogni occorrenza, documenta:
- File e linea
- Tipo di animazione
- Target widget
- Durata
- Callback di completamento (se presente)

Output: Lista ordinata per file con dettagli di ogni animazione.
```

### Prompt 2.2 - Creazione Animation Manager
```
FASE 2: Animation Manager - Core Implementation

Crea desktop_app/core/animation_manager.py:

```python
"""
AnimationManager - Gestione centralizzata di tutte le animazioni PyQt6.

Responsabilità:
- Registrazione e tracking di tutte le animazioni attive
- Cancellazione sicura per owner (view/widget)
- Timeout automatico per animazioni bloccate
- Cleanup su distruzione widget
"""

class AnimationManager:
    """Singleton per gestione globale animazioni."""
    
    _instance: Optional['AnimationManager'] = None
    
    @classmethod
    def instance(cls) -> 'AnimationManager':
        ...
    
    def register(
        self, 
        animation: QAbstractAnimation,
        owner: QObject,
        name: str = "",
        timeout_ms: int = 5000,
        on_timeout: Optional[Callable] = None
    ) -> str:
        """
        Registra un'animazione.
        
        Args:
            animation: L'animazione da registrare
            owner: Widget proprietario (per cleanup automatico)
            name: Nome identificativo (opzionale)
            timeout_ms: Timeout dopo cui l'animazione viene forzatamente fermata
            on_timeout: Callback da chiamare in caso di timeout
            
        Returns:
            ID univoco dell'animazione registrata
        """
        ...
    
    def cancel_all(self, owner: QObject) -> int:
        """
        Cancella tutte le animazioni di un owner.
        
        Args:
            owner: Widget le cui animazioni vanno cancellate
            
        Returns:
            Numero di animazioni cancellate
        """
        ...
    
    def cancel_by_id(self, animation_id: str) -> bool:
        """Cancella una specifica animazione per ID."""
        ...
    
    def is_animating(self, owner: QObject) -> bool:
        """Verifica se un owner ha animazioni attive."""
        ...
    
    def wait_completion(
        self, 
        owner: QObject, 
        timeout_ms: int = 5000
    ) -> bool:
        """
        Attende il completamento di tutte le animazioni di un owner.
        
        Returns:
            True se completate, False se timeout
        """
        ...

# Singleton globale
animation_manager = AnimationManager.instance()
```

Implementa anche:
- _AnimationEntry dataclass per tracking interno
- Weak references per evitare memory leak
- Logging dettagliato
- Thread safety con QMutex

Test: tests/desktop_app/core/test_animation_manager.py
```

### Prompt 2.3 - Helper per Animazioni Comuni
```
FASE 2: Animation Manager - Animation Helpers

Aggiungi a animation_manager.py funzioni helper:

```python
def fade_out(
    widget: QWidget,
    duration_ms: int = 300,
    on_finished: Optional[Callable] = None
) -> str:
    """
    Animazione fade out di un widget.
    Registra automaticamente l'animazione.
    """
    ...

def fade_in(
    widget: QWidget,
    duration_ms: int = 300,
    on_finished: Optional[Callable] = None
) -> str:
    """Animazione fade in di un widget."""
    ...

def slide_out(
    widget: QWidget,
    direction: Literal['left', 'right', 'up', 'down'] = 'left',
    duration_ms: int = 300,
    on_finished: Optional[Callable] = None
) -> str:
    """Animazione slide out."""
    ...

def slide_in(
    widget: QWidget,
    direction: Literal['left', 'right', 'up', 'down'] = 'right',
    duration_ms: int = 300,
    on_finished: Optional[Callable] = None
) -> str:
    """Animazione slide in."""
    ...

def animate_property(
    target: QObject,
    property_name: bytes,
    start_value: Any,
    end_value: Any,
    duration_ms: int = 300,
    easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
    on_finished: Optional[Callable] = None
) -> str:
    """Helper generico per animare qualsiasi proprietà."""
    ...
```

Ogni helper deve:
1. Verificare che widget sia vivo
2. Registrare l'animazione nell'AnimationManager
3. Gestire cleanup automatico
4. Ritornare animation_id per eventuale cancellazione manuale
```

### Prompt 2.4 - Refactoring Animated Widgets
```
FASE 2: Animation Manager - Refactoring animated_widgets.py

Modifica desktop_app/components/animated_widgets.py per usare AnimationManager:

1. Importa animation_manager
2. Rimuovi gestione locale delle animazioni
3. Usa i nuovi helper per tutte le animazioni

ESEMPIO - AnimatedButton:

PRIMA:
```python
def _start_hover_animation(self):
    self.hover_animation = QPropertyAnimation(self, b"background_color")
    self.hover_animation.setDuration(150)
    ...
    self.hover_animation.start()
```

DOPO:
```python
def _start_hover_animation(self):
    from desktop_app.core.animation_manager import animate_property
    
    self._hover_anim_id = animate_property(
        target=self,
        property_name=b"background_color",
        start_value=self._normal_color,
        end_value=self._hover_color,
        duration_ms=150,
        on_finished=None
    )
```

4. Override closeEvent per cancellare animazioni:
```python
def closeEvent(self, event):
    animation_manager.cancel_all(owner=self)
    super().closeEvent(event)
```

Applica a TUTTI i widget in animated_widgets.py:
- AnimatedButton
- AnimatedLabel
- AnimatedFrame
- (altri se presenti)
```

### Prompt 2.5 - Refactoring Login View Animazioni
```
FASE 2: Animation Manager - Refactoring login_view.py animazioni

Modifica desktop_app/views/login_view.py:

1. Sostituisci TUTTE le animazioni con gli helper di animation_manager

2. Metodo _animate_success_exit():
```python
def _animate_success_exit(self):
    """Animazione di uscita dopo login riuscito."""
    container = self.get_child('container')
    if not container:
        self._emit_transition_complete()
        return
    
    from desktop_app.core.animation_manager import fade_out
    
    fade_out(
        widget=container,
        duration_ms=300,
        on_finished=self._emit_transition_complete
    )
```

3. Aggiungi override closeEvent:
```python
def closeEvent(self, event):
    from desktop_app.core.animation_manager import animation_manager
    animation_manager.cancel_all(owner=self)
    super().closeEvent(event)
```

4. Verifica e refactora OGNI altro metodo che usa animazioni:
   - _animate_error_shake()
   - _animate_loading()
   - _pulse_animation() (se presente)
   - Qualsiasi altro

5. Test: pytest tests/desktop_app/views/test_login_view*.py  passi per procedere alla FASE 3: Signal/Slot Hardening
```

---

## 🔌 FASE 3: Signal/Slot Hardening

### Prompt 3.1 - Analisi Signal/Slot
```
FASE 3: Signal/Slot Hardening - Analisi

Analizza tutti i worker in desktop_app/workers/:
- chat_worker.py
- csv_import_worker.py
- data_worker.py
- file_scanner_worker.py
- worker.py

Per ogni file, identifica:
1. Segnali definiti (pyqtSignal)
2. Dove vengono emessi (emit())
3. Chi si connette a questi segnali
4. Se c'è cleanup (disconnect) alla chiusura

Output: Mappa [Worker] -> [Segnali] -> [Connessioni] -> [Cleanup presente?]
```

### Prompt 3.2 - Signal Guard Implementation
```
FASE 3: Signal/Slot Hardening - Signal Guard

Crea desktop_app/core/signal_guard.py:

```python
"""
SignalGuard - Gestione sicura di signal/slot PyQt6.

Previene:
- Emit su segnali dopo distruzione oggetto
- Memory leak da connessioni non disconnesse
- Race condition su thread multipli
"""

from typing import Any, Callable, Optional, Set
from weakref import WeakSet
from PyQt6.QtCore import QObject, pyqtSignal, QMutex, QMutexLocker


class SafeSignalEmitter:
    """
    Wrapper per emissione sicura di segnali.
    
    Uso:
        class MyWorker(QThread):
            progress = pyqtSignal(int)
            _safe_emitter: SafeSignalEmitter
            
            def __init__(self):
                super().__init__()
                self._safe_emitter = SafeSignalEmitter(self)
            
            def run(self):
                for i in range(100):
                    self._safe_emitter.emit(self.progress, i)
    """
    
    def __init__(self, owner: QObject):
        self._owner = owner
        self._is_alive = True
        self._mutex = QMutex()
        
    def emit(self, signal: pyqtSignal, *args: Any) -> bool:
        """
        Emette un segnale in modo sicuro.
        
        Returns:
            True se emesso, False se owner distrutto
        """
        with QMutexLocker(self._mutex):
            if not self._is_alive:
                return False
            try:
                signal.emit(*args)
                return True
            except RuntimeError:
                self._is_alive = False
                return False
    
    def invalidate(self):
        """Invalida l'emitter (chiamare prima della distruzione)."""
        with QMutexLocker(self._mutex):
            self._is_alive = False


class ConnectionTracker:
    """
    Traccia connessioni signal/slot per cleanup automatico.
    
    Uso:
        tracker = ConnectionTracker()
        tracker.connect(worker.finished, self.on_finished)
        # ... più tardi ...
        tracker.disconnect_all()
    """
    
    def __init__(self):
        self._connections: list[tuple] = []
    
    def connect(
        self, 
        signal: pyqtSignal, 
        slot: Callable,
        connection_type: Qt.ConnectionType = Qt.ConnectionType.AutoConnection
    ):
        """Connette e traccia la connessione."""
        signal.connect(slot, connection_type)
        self._connections.append((signal, slot))
    
    def disconnect_all(self) -> int:
        """
        Disconnette tutte le connessioni tracciate.
        
        Returns:
            Numero di connessioni disconnesse
        """
        count = 0
        for signal, slot in self._connections:
            try:
                signal.disconnect(slot)
                count += 1
            except (TypeError, RuntimeError):
                pass  # Già disconnesso o oggetto distrutto
        self._connections.clear()
        return count


def safe_emit(signal: pyqtSignal, *args: Any) -> bool:
    """
    Funzione helper per emissione sicura one-shot.
    
    Uso:
        safe_emit(self.progress_signal, 50)
    """
    try:
        signal.emit(*args)
        return True
    except RuntimeError:
        return False
```

Test: tests/desktop_app/core/test_signal_guard.py
```

### Prompt 3.3 - Refactoring Workers
```
FASE 3: Signal/Slot Hardening - Refactoring Workers

Applica SafeSignalEmitter a TUTTI i worker in desktop_app/workers/:

1. chat_worker.py:
```python
class ChatWorker(QThread):
    response_chunk = pyqtSignal(str)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)
    
    def __init__(self, ...):
        super().__init__()
        self._safe_emitter = SafeSignalEmitter(self)
    
    def run(self):
        try:
            for chunk in self._stream_response():
                if not self._safe_emitter.emit(self.response_chunk, chunk):
                    break  # Owner distrutto, fermati
            self._safe_emitter.emit(self.finished_signal)
        except Exception as e:
            self._safe_emitter.emit(self.error_signal, str(e))
    
    def stop(self):
        self._safe_emitter.invalidate()
        self.requestInterruption()
```

2. Applica lo stesso pattern a:
   - csv_import_worker.py
   - data_worker.py
   - file_scanner_worker.py
   - worker.py (base class se presente)

3. Nelle view che usano worker, usa ConnectionTracker:
```python
class ImportView(SafeWidgetMixin, QWidget):
    def __init__(self):
        ...
        self._connection_tracker = ConnectionTracker()
    
    def _start_import(self, file_path):
        self.worker = FileScannerWorker(file_path)
        self._connection_tracker.connect(self.worker.finished, self._on_import_done)
        self._connection_tracker.connect(self.worker.error, self._on_import_error)
        self.worker.start()
    
    def closeEvent(self, event):
        self._connection_tracker.disconnect_all()
        if hasattr(self, 'worker'):
            self.worker.stop()
        super().closeEvent(event)
```

Test: pytest tests/desktop_app/workers/ passi per procedere alla FASE 4: Error Boundaries
```

---

## 🛡️ FASE 4: Error Boundaries

### Prompt 4.1 - Error Boundary Core
```
FASE 4: Error Boundaries - Core Implementation

Crea desktop_app/core/error_boundary.py:

```python
"""
Error Boundary System - Gestione errori a livello view.

Ispirato a React Error Boundaries, previene che errori in una view
crashino l'intera applicazione.
"""

import traceback
import logging
from typing import Callable, Optional, Type
from functools import wraps
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import QObject

logger = logging.getLogger(__name__)


class ViewError(Exception):
    """Eccezione base per errori nelle view."""
    pass


class RecoverableError(ViewError):
    """Errore da cui la view può recuperare."""
    pass


class FatalViewError(ViewError):
    """Errore che richiede chiusura della view."""
    pass


class ErrorBoundary:
    """
    Gestisce errori in una view con possibilità di recovery.
    
    Uso:
        class MyView(QWidget):
            def __init__(self):
                self.error_boundary = ErrorBoundary(
                    owner=self,
                    on_error=self._handle_error,
                    on_fatal=self._handle_fatal
                )
            
            @error_boundary.protect
            def risky_method(self):
                ...
    """
    
    def __init__(
        self,
        owner: QWidget,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_fatal: Optional[Callable[[Exception], None]] = None,
        fallback_ui: Optional[Callable[[], QWidget]] = None,
        report_to_sentry: bool = True
    ):
        self._owner = owner
        self._on_error = on_error or self._default_error_handler
        self._on_fatal = on_fatal or self._default_fatal_handler
        self._fallback_ui = fallback_ui
        self._report_to_sentry = report_to_sentry
        self._error_count = 0
        self._max_errors = 3  # Dopo 3 errori, considera fatal
    
    def protect(self, func: Callable) -> Callable:
        """Decorator per proteggere metodi."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RecoverableError as e:
                self._handle_recoverable(e)
            except FatalViewError as e:
                self._handle_fatal_error(e)
            except Exception as e:
                self._handle_unknown(e)
        return wrapper
    
    def _handle_recoverable(self, error: RecoverableError):
        """Gestisce errori recuperabili."""
        logger.warning(f"Recoverable error in {self._owner.__class__.__name__}: {error}")
        self._error_count += 1
        
        if self._error_count >= self._max_errors:
            self._handle_fatal_error(
                FatalViewError(f"Too many errors: {error}")
            )
        else:
            self._on_error(error)
    
    def _handle_fatal_error(self, error: FatalViewError):
        """Gestisce errori fatali."""
        logger.error(f"Fatal error in {self._owner.__class__.__name__}: {error}")
        self._report_error(error)
        self._on_fatal(error)
        
        if self._fallback_ui:
            self._show_fallback()
    
    def _handle_unknown(self, error: Exception):
        """Gestisce errori sconosciuti."""
        logger.exception(f"Unknown error in {self._owner.__class__.__name__}")
        self._report_error(error)
        
        # Errori sconosciuti sono trattati come recuperabili (con cautela)
        self._error_count += 1
        if self._error_count >= self._max_errors:
            self._handle_fatal_error(FatalViewError(str(error)))
        else:
            self._on_error(error)
    
    def _report_error(self, error: Exception):
        """Invia errore a Sentry se configurato."""
        if self._report_to_sentry:
            try:
                import sentry_sdk
                sentry_sdk.capture_exception(error)
            except ImportError:
                pass
    
    def _default_error_handler(self, error: Exception):
        """Handler di default per errori recuperabili."""
        # Mostra toast non intrusivo
        from desktop_app.components.toast import Toast
        Toast.warning(
            self._owner,
            "Si è verificato un errore",
            str(error)
        )
    
    def _default_fatal_handler(self, error: Exception):
        """Handler di default per errori fatali."""
        QMessageBox.critical(
            self._owner,
            "Errore Critico",
            f"Si è verificato un errore critico:\n{error}\n\n"
            "La vista verrà chiusa."
        )


def error_boundary(
    on_error: Optional[Callable] = None,
    recoverable: bool = True
):
    """
    Decorator per metodi singoli (senza bisogno di istanza ErrorBoundary).
    
    Uso:
        @error_boundary(recoverable=True)
        def my_method(self):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logger.exception(f"Error in {func.__name__}")
                if on_error:
                    on_error(e)
                elif not recoverable:
                    raise
        return wrapper
    return decorator
```

Test: tests/desktop_app/core/test_error_boundary.py
```

### Prompt 4.2 - Applicazione Error Boundaries alle View
```
FASE 4: Error Boundaries - Applicazione alle View

Applica ErrorBoundary a TUTTE le view in desktop_app/views/:

1. login_view.py:
```python
class LoginView(SafeWidgetMixin, QWidget):
    def __init__(self, ...):
        super().__init__()
        
        self.error_boundary = ErrorBoundary(
            owner=self,
            on_error=self._on_view_error,
            on_fatal=self._on_view_fatal,
            report_to_sentry=True
        )
        
        self._setup_ui()
    
    def _on_view_error(self, error: Exception):
        """Gestisce errori recuperabili nella login view."""
        # Reset stato UI a default sicuro
        self._reset_ui_state()
        Toast.warning(self, "Errore", str(error))
    
    def _on_view_fatal(self, error: Exception):
        """Gestisce errori fatali - chiudi e riapri login."""
        self.close()
        # Segnala al controller di riaprire login
        self.fatal_error.emit(str(error))
    
    @error_boundary.protect
    def _animate_success_exit(self):
        # ... codice esistente ...
    
    @error_boundary.protect  
    def on_login_success(self, ...):
        # ... codice esistente ...
    
    def _reset_ui_state(self):
        """Resetta UI a stato sicuro."""
        btn = self.get_child('login_btn')
        if btn:
            btn.set_loading(False)
            btn.setEnabled(True)
```

2. Applica lo stesso pattern a:
   - splash_screen.py
   - dashboard_view.py / database_view.py
   - import_view.py
   - validation_view.py
   - config_view.py
   - scadenzario_view.py
   - stats_view.py
   - modern_guide_view.py

3. Per ogni view:
   - Aggiungi ErrorBoundary nel __init__
   - Decora metodi rischiosi con @error_boundary.protect
   - Implementa _on_view_error e _on_view_fatal
   - Implementa _reset_ui_state per recovery

Test: pytest tests/desktop_app/views/ passi per procedere alla FASE 5: State Machine
```

---

## 🔄 FASE 5: State Machine

### Prompt 5.1 - State Machine Core
```
FASE 5: State Machine - Implementazione

Crea desktop_app/core/state_machine.py:

```python
"""
Application State Machine - Gestione transizioni UI con Qt State Machine.

Stati principali:
- INITIALIZING: App in avvio
- SPLASH: Splash screen visibile
- LOGIN: Schermata login
- AUTHENTICATING: Login in corso
- TRANSITIONING: Cambio vista in corso
- MAIN: App principale (dashboard)
- ERROR: Stato di errore

Le transizioni sono SEMPRE gestite dalla state machine,
mai direttamente dalle view.
"""

from enum import Enum, auto
from typing import Optional, Callable, Dict
from PyQt6.QtCore import QObject, QState, QStateMachine, QSignalTransition, pyqtSignal
from PyQt6.QtWidgets import QWidget

import logging
logger = logging.getLogger(__name__)


class AppState(Enum):
    """Stati dell'applicazione."""
    INITIALIZING = auto()
    SPLASH = auto()
    LOGIN = auto()
    AUTHENTICATING = auto()
    TRANSITIONING = auto()
    MAIN = auto()
    ERROR = auto()


class AppStateMachine(QObject):
    """
    State machine per gestire il flusso dell'applicazione.
    
    Uso:
        state_machine = AppStateMachine()
        state_machine.state_changed.connect(self._on_state_changed)
        state_machine.start()
        
        # Triggera transizione
        state_machine.trigger_login_success()
    """
    
    # Segnali per notificare cambi di stato
    state_changed = pyqtSignal(AppState, AppState)  # old_state, new_state
    transition_started = pyqtSignal(str)  # transition_name
    transition_completed = pyqtSignal(str)  # transition_name
    
    # Segnali per trigger transizioni (connessi internamente)
    _splash_done = pyqtSignal()
    _login_success = pyqtSignal()
    _login_failed = pyqtSignal()
    _logout = pyqtSignal()
    _error_occurred = pyqtSignal()
    _error_recovered = pyqtSignal()
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        self._current_state = AppState.INITIALIZING
        self._machine = QStateMachine(self)
        self._states: Dict[AppState, QState] = {}
        self._setup_states()
        self._setup_transitions()
    
    def _setup_states(self):
        """Crea gli stati della macchina."""
        for state_enum in AppState:
            state = QState()
            state.setObjectName(state_enum.name)
            
            # Connetti entry/exit
            state.entered.connect(
                lambda s=state_enum: self._on_state_entered(s)
            )
            state.exited.connect(
                lambda s=state_enum: self._on_state_exited(s)
            )
            
            self._states[state_enum] = state
            self._machine.addState(state)
        
        # Stato iniziale
        self._machine.setInitialState(self._states[AppState.INITIALIZING])
    
    def _setup_transitions(self):
        """Configura le transizioni tra stati."""
        s = self._states
        
        # INITIALIZING -> SPLASH
        self._add_transition(
            s[AppState.INITIALIZING], 
            s[AppState.SPLASH],
            trigger=None,  # Automatico
            name="init_to_splash"
        )
        
        # SPLASH -> LOGIN (dopo animazione splash)
        self._add_transition(
            s[AppState.SPLASH],
            s[AppState.LOGIN],
            trigger=self._splash_done,
            name="splash_to_login"
        )
        
        # LOGIN -> AUTHENTICATING (submit login)
        self._add_transition(
            s[AppState.LOGIN],
            s[AppState.AUTHENTICATING],
            trigger=None,  # Gestito manualmente
            name="login_to_auth"
        )
        
        # AUTHENTICATING -> TRANSITIONING (login success)
        self._add_transition(
            s[AppState.AUTHENTICATING],
            s[AppState.TRANSITIONING],
            trigger=self._login_success,
            name="auth_to_transition"
        )
        
        # AUTHENTICATING -> LOGIN (login failed)
        self._add_transition(
            s[AppState.AUTHENTICATING],
            s[AppState.LOGIN],
            trigger=self._login_failed,
            name="auth_to_login"
        )
        
        # TRANSITIONING -> MAIN
        self._add_transition(
            s[AppState.TRANSITIONING],
            s[AppState.MAIN],
            trigger=None,  # Dopo animazione
            name="transition_to_main"
        )
        
        # MAIN -> LOGIN (logout)
        self._add_transition(
            s[AppState.MAIN],
            s[AppState.LOGIN],
            trigger=self._logout,
            name="main_to_login"
        )
        
        # ANY -> ERROR
        for state_enum in AppState:
            if state_enum != AppState.ERROR:
                self._add_transition(
                    s[state_enum],
                    s[AppState.ERROR],
                    trigger=self._error_occurred,
                    name=f"{state_enum.name}_to_error"
                )
        
        # ERROR -> LOGIN (recovery)
        self._add_transition(
            s[AppState.ERROR],
            s[AppState.LOGIN],
            trigger=self._error_recovered,
            name="error_to_login"
        )
    
    def _add_transition(
        self,
        from_state: QState,
        to_state: QState,
        trigger: Optional[pyqtSignal],
        name: str
    ):
        """Aggiunge una transizione."""
        if trigger:
            transition = from_state.addTransition(trigger, to_state)
        else:
            # Transizione immediata (per stati intermedi)
            from_state.addTransition(to_state)
    
    def _on_state_entered(self, state: AppState):
        """Callback quando si entra in uno stato."""
        old_state = self._current_state
        self._current_state = state
        logger.info(f"State transition: {old_state.name} -> {state.name}")
        self.state_changed.emit(old_state, state)
    
    def _on_state_exited(self, state: AppState):
        """Callback quando si esce da uno stato."""
        pass
    
    # === Public API ===
    
    def start(self):
        """Avvia la state machine."""
        self._machine.start()
    
    def current_state(self) -> AppState:
        """Ritorna lo stato corrente."""
        return self._current_state
    
    def trigger_splash_done(self):
        """Trigger: splash completato."""
        self._splash_done.emit()
    
    def trigger_login_success(self):
        """Trigger: login riuscito."""
        self._login_success.emit()
    
    def trigger_login_failed(self):
        """Trigger: login fallito."""
        self._login_failed.emit()
    
    def trigger_logout(self):
        """Trigger: logout."""
        self._logout.emit()
    
    def trigger_error(self):
        """Trigger: errore critico."""
        self._error_occurred.emit()
    
    def trigger_recovery(self):
        """Trigger: recovery da errore."""
        self._error_recovered.emit()
    
    def can_transition_to(self, target: AppState) -> bool:
        """Verifica se la transizione è permessa."""
        # Implementa logica di validazione
        valid_transitions = {
            AppState.INITIALIZING: [AppState.SPLASH],
            AppState.SPLASH: [AppState.LOGIN],
            AppState.LOGIN: [AppState.AUTHENTICATING],
            AppState.AUTHENTICATING: [AppState.TRANSITIONING, AppState.LOGIN],
            AppState.TRANSITIONING: [AppState.MAIN],
            AppState.MAIN: [AppState.LOGIN],
            AppState.ERROR: [AppState.LOGIN],
        }
        return target in valid_transitions.get(self._current_state, [])


# Singleton
_app_state_machine: Optional[AppStateMachine] = None

def get_state_machine() -> AppStateMachine:
    """Ottiene l'istanza singleton della state machine."""
    global _app_state_machine
    if _app_state_machine is None:
        _app_state_machine = AppStateMachine()
    return _app_state_machine
```

Test: tests/desktop_app/core/test_state_machine.py 
```

### Prompt 5.2 - Integrazione State Machine nel Main
```
FASE 5: State Machine - Integrazione in main.py

Modifica desktop_app/main.py per usare AppStateMachine:

1. Importa e inizializza:
```python
from desktop_app.core.state_machine import get_state_machine, AppState

class ApplicationController:
    def __init__(self):
        ...
        self._state_machine = get_state_machine()
        self._state_machine.state_changed.connect(self._on_state_changed)
        self._state_machine.start()
```

2. Gestisci cambi di stato:
```python
def _on_state_changed(self, old_state: AppState, new_state: AppState):
    """Reagisce ai cambi di stato della state machine."""
    logger.info(f"App state: {old_state.name} -> {new_state.name}")
    
    handlers = {
        AppState.SPLASH: self._show_splash,
        AppState.LOGIN: self._show_login,
        AppState.AUTHENTICATING: self._show_authenticating,
        AppState.TRANSITIONING: self._start_transition,
        AppState.MAIN: self._show_main,
        AppState.ERROR: self._show_error,
    }
    
    handler = handlers.get(new_state)
    if handler:
        handler()
```

3. Metodi per ogni stato:
```python
def _show_splash(self):
    self.splash = SplashScreen()
    self.splash.finished.connect(
        self._state_machine.trigger_splash_done
    )
    self.splash.show()

def _show_login(self):
    # Cancella animazioni in corso
    animation_manager.cancel_all(owner=self)
    
    self.login_view = LoginView(...)
    self.login_view.login_success.connect(
        self._state_machine.trigger_login_success
    )
    self.login_view.login_failed.connect(
        self._state_machine.trigger_login_failed
    )
    self._set_current_view(self.login_view)

def _start_transition(self):
    # La transizione è gestita dalla state machine
    # L'animazione quando completa triggera il passaggio a MAIN
    animation_manager.fade_out(
        self.login_view,
        on_finished=self._on_transition_animation_done
    )

def _on_transition_animation_done(self):
    # Safe cleanup della vecchia view
    if hasattr(self, 'login_view'):
        self.login_view.deleteLater()
    # Passa allo stato MAIN (la state machine gestisce)
    ...
```

4. Rimuovi la logica di transizione diretta dalle view

Test: pytest tests/desktop_app/test_main_controller.py  passi per procedere alla FASE 6: Observability
```

---

## 👁️ FASE 6: Observability

### Prompt 6.1 - Rimozione PostHog
```
FASE 6: Observability - Rimozione PostHog

1. Cerca TUTTI i riferimenti a PostHog:
```bash
grep -r "posthog" --include="*.py" -l
```

2. Per ogni file trovato:
   - Rimuovi import posthog
   - Rimuovi inizializzazione PostHog
   - Rimuovi chiamate posthog.capture()
   - Rimuovi posthog.identify()
   - Rimuovi qualsiasi altra chiamata PostHog

3. Rimuovi da requirements.txt:
   - posthog

4. Verifica che non ci siano riferimenti rimasti:
```bash
grep -r "posthog" --include="*.py"
# DEVE essere vuoto
```

5. Esegui test per verificare che nulla sia rotto:
```bash
pytest tests/ -v
```
```

### Prompt 6.2 - Enhanced Sentry Integration
```
FASE 6: Observability - Enhanced Sentry

Crea/modifica app/utils/sentry_integration.py:

```python
"""
Enhanced Sentry Integration con context Qt-aware.

Features:
- Breadcrumbs per azioni UI
- Context con stato applicazione
- Tag per versione e ambiente
- Filtri per errori non critici
"""

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def init_sentry(
    dsn: str,
    environment: str = "production",
    release: Optional[str] = None,
    debug: bool = False
):
    """
    Inizializza Sentry con configurazione ottimizzata per Intelleo.
    """
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        debug=debug,
        
        # Integrations
        integrations=[
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            ),
        ],
        
        # Performance
        traces_sample_rate=0.1,  # 10% delle transazioni
        profiles_sample_rate=0.1,
        
        # Privacy
        send_default_pii=False,
        
        # Filtering
        before_send=_before_send,
        before_breadcrumb=_before_breadcrumb,
    )
    
    logger.info("Sentry initialized")


def _before_send(event: Dict, hint: Dict) -> Optional[Dict]:
    """Filtra eventi prima dell'invio."""
    # Non inviare errori di rete (troppo comuni)
    if 'exc_info' in hint:
        exc_type, exc_value, _ = hint['exc_info']
        if exc_type.__name__ in ('ConnectionError', 'TimeoutError'):
            return None
    
    # Aggiungi context Qt
    event['contexts'] = event.get('contexts', {})
    event['contexts']['qt'] = _get_qt_context()
    
    return event


def _before_breadcrumb(crumb: Dict, hint: Dict) -> Optional[Dict]:
    """Filtra breadcrumbs."""
    # Escludi breadcrumbs troppo verbosi
    if crumb.get('category') == 'http' and crumb.get('level') == 'info':
        return None
    return crumb


def _get_qt_context() -> Dict[str, Any]:
    """Raccoglie context relativo a Qt."""
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            return {
                'active_window': app.activeWindow().__class__.__name__ if app.activeWindow() else None,
                'focus_widget': app.focusWidget().__class__.__name__ if app.focusWidget() else None,
            }
    except Exception:
        pass
    return {}


def add_ui_breadcrumb(
    action: str,
    view: str,
    data: Optional[Dict] = None
):
    """
    Aggiunge un breadcrumb per azione UI.
    
    Uso:
        add_ui_breadcrumb("click", "LoginView", {"button": "login_btn"})
    """
    sentry_sdk.add_breadcrumb(
        category="ui",
        message=f"{action} in {view}",
        level="info",
        data=data or {}
    )


def set_user_context(user_id: str, username: str):
    """Imposta context utente (senza PII sensibili)."""
    sentry_sdk.set_user({
        "id": user_id,
        "username": username,
    })


def capture_view_error(
    view_name: str,
    error: Exception,
    extra: Optional[Dict] = None
):
    """Cattura errore con context della view."""
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("view", view_name)
        scope.set_extra("view_data", extra or {})
        sentry_sdk.capture_exception(error)
```

Integra in launcher.py e nelle view. Quando ultimato procederemo alla FASE 7: User Simulation Testing
```

---

## 🧪 FASE 7: User Simulation Testing

### Prompt 7.1 - Framework Simulazione
```
FASE 7: User Simulation - Framework Base

Crea tests/desktop_app/simulation/conftest.py:

```python
"""
Fixtures per test di simulazione utente.
"""

import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
import sys


@pytest.fixture(scope="session")
def qapp():
    """QApplication per tutta la sessione di test."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def qtbot(qapp, qtbot):
    """qtbot con QApplication garantita."""
    return qtbot


@pytest.fixture
def mock_backend():
    """Mock del backend FastAPI per test isolati."""
    from unittest.mock import MagicMock, patch
    
    mock_client = MagicMock()
    mock_client.login.return_value = {
        "access_token": "test_token",
        "user_info": {"id": 1, "username": "admin", "is_admin": True}
    }
    mock_client.get_certificati.return_value = []
    
    with patch('desktop_app.api_client.APIClient', return_value=mock_client):
        yield mock_client


@pytest.fixture
def app_controller(qapp, mock_backend):
    """Controller applicazione per test."""
    from desktop_app.main import ApplicationController
    
    controller = ApplicationController()
    yield controller
    
    # Cleanup
    controller.cleanup()
```

Crea tests/desktop_app/simulation/user_actions.py:

```python
"""
Helper per simulare azioni utente.
"""

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton
from typing import Optional
import time


class UserSimulator:
    """
    Simula interazioni utente realistiche.
    
    Uso:
        sim = UserSimulator(qtbot)
        sim.click(button)
        sim.type_text(input_field, "hello")
        sim.wait_for_animation()
    """
    
    def __init__(self, qtbot):
        self.qtbot = qtbot
        self._action_delay_ms = 50  # Ritardo tra azioni (realismo)
    
    def click(self, widget: QWidget, pos: Optional[QPoint] = None):
        """Simula click su widget."""
        if pos is None:
            pos = widget.rect().center()
        
        QTest.mouseClick(widget, Qt.MouseButton.LeftButton, pos=pos)
        self._wait_for_events()
    
    def double_click(self, widget: QWidget, pos: Optional[QPoint] = None):
        """Simula doppio click."""
        if pos is None:
            pos = widget.rect().center()
        
        QTest.mouseDClick(widget, Qt.MouseButton.LeftButton, pos=pos)
        self._wait_for_events()
    
    def type_text(self, widget: QLineEdit, text: str, clear_first: bool = True):
        """Simula digitazione testo."""
        if clear_first:
            widget.clear()
        
        widget.setFocus()
        QTest.keyClicks(widget, text)
        self._wait_for_events()
    
    def press_key(self, widget: QWidget, key: Qt.Key, modifier: Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier):
        """Simula pressione tasto."""
        QTest.keyClick(widget, key, modifier)
        self._wait_for_events()
    
    def press_enter(self, widget: QWidget):
        """Simula pressione Enter."""
        self.press_key(widget, Qt.Key.Key_Return)
    
    def drag_and_drop(self, source: QWidget, target: QWidget):
        """Simula drag and drop."""
        source_pos = source.rect().center()
        target_pos = target.rect().center()
        
        QTest.mousePress(source, Qt.MouseButton.LeftButton, pos=source_pos)
        QTest.mouseMove(target, pos=target_pos)
        QTest.mouseRelease(target, Qt.MouseButton.LeftButton, pos=target_pos)
        self._wait_for_events()
    
    def wait_for_visible(self, widget: QWidget, timeout_ms: int = 5000):
        """Attende che widget sia visibile."""
        self.qtbot.waitUntil(lambda: widget.isVisible(), timeout=timeout_ms)
    
    def wait_for_enabled(self, widget: QWidget, timeout_ms: int = 5000):
        """Attende che widget sia abilitato."""
        self.qtbot.waitUntil(lambda: widget.isEnabled(), timeout=timeout_ms)
    
    def wait_for_animation(self, timeout_ms: int = 1000):
        """Attende completamento animazioni."""
        from desktop_app.core.animation_manager import animation_manager
        
        start = time.time()
        while time.time() - start < timeout_ms / 1000:
            if not animation_manager._active_animations:
                return True
            QTest.qWait(50)
        return False
    
    def wait_for_condition(self, condition, timeout_ms: int = 5000):
        """Attende una condizione generica."""
        self.qtbot.waitUntil(condition, timeout=timeout_ms)
    
    def _wait_for_events(self):
        """Processa eventi Qt e attende."""
        QTest.qWait(self._action_delay_ms)
```

Test: Verifica che i file siano creati correttamente.
```

### Prompt 7.2 - Test Scenari Login
```
FASE 7: User Simulation - Test Login Scenarios

Crea tests/desktop_app/simulation/test_login_scenarios.py:

```python
"""
Test di simulazione utente per scenari di login.
"""

import pytest
from PyQt6.QtCore import Qt
from .user_actions import UserSimulator


class TestLoginScenarios:
    """Test che simulano l'intero flusso di login."""
    
    @pytest.fixture
    def simulator(self, qtbot):
        return UserSimulator(qtbot)
    
    @pytest.fixture
    def login_view(self, app_controller, qtbot):
        """Ottiene la login view dall'app controller."""
        # Attendi che la login view sia visibile
        qtbot.waitUntil(
            lambda: hasattr(app_controller, 'login_view') and 
                    app_controller.login_view.isVisible(),
            timeout=5000
        )
        return app_controller.login_view
    
    def test_successful_login_flow(self, simulator, login_view, mock_backend, qtbot):
        """
        Scenario: Login riuscito con credenziali valide.
        
        Steps:
        1. Utente vede login form
        2. Inserisce username
        3. Inserisce password
        4. Clicca login
        5. Vede animazione di successo
        6. Viene reindirizzato a dashboard
        """
        # 1. Verifica form visibile
        assert login_view.isVisible()
        
        # 2. Trova e compila username
        username_input = login_view.findChild(QLineEdit, "username_input")
        assert username_input is not None
        simulator.type_text(username_input, "admin")
        
        # 3. Compila password
        password_input = login_view.findChild(QLineEdit, "password_input")
        assert password_input is not None
        simulator.type_text(password_input, "password123")
        
        # 4. Clicca login
        login_btn = login_view.findChild(QPushButton, "login_btn")
        assert login_btn is not None
        simulator.click(login_btn)
        
        # 5. Attendi animazione
        simulator.wait_for_animation(timeout_ms=2000)
        
        # 6. Verifica transizione (login view non più visibile o distrutta)
        qtbot.waitUntil(
            lambda: not login_view.isVisible(),
            timeout=5000
        )
    
    def test_failed_login_shows_error(self, simulator, login_view, mock_backend, qtbot):
        """
        Scenario: Login fallito mostra errore.
        """
        # Configura mock per fallire
        mock_backend.login.side_effect = Exception("Invalid credentials")
        
        username_input = login_view.findChild(QLineEdit, "username_input")
        password_input = login_view.findChild(QLineEdit, "password_input")
        login_btn = login_view.findChild(QPushButton, "login_btn")
        
        simulator.type_text(username_input, "wrong")
        simulator.type_text(password_input, "wrong")
        simulator.click(login_btn)
        
        # Attendi che appaia messaggio errore
        simulator.wait_for_animation()
        
        # Login view deve rimanere visibile
        assert login_view.isVisible()
        
        # Button deve essere riabilitato
        qtbot.waitUntil(lambda: login_btn.isEnabled(), timeout=3000)
    
    def test_rapid_login_clicks_no_crash(self, simulator, login_view, qtbot):
        """
        Scenario: Click multipli rapidi su login non causano crash.
        """
        login_btn = login_view.findChild(QPushButton, "login_btn")
        
        # 10 click rapidi
        for _ in range(10):
            simulator.click(login_btn)
        
        # Attendi che si stabilizzi
        simulator.wait_for_animation(timeout_ms=3000)
        
        # App non deve crashare - verifica che login_view sia ancora valida
        assert login_view is not None
    
    def test_login_during_animation_no_crash(self, simulator, login_view, mock_backend, qtbot):
        """
        Scenario: Tentativo di login durante animazione non causa crash.
        """
        username_input = login_view.findChild(QLineEdit, "username_input")
        password_input = login_view.findChild(QLineEdit, "password_input")
        login_btn = login_view.findChild(QPushButton, "login_btn")
        
        simulator.type_text(username_input, "admin")
        simulator.type_text(password_input, "password")
        
        # Primo click
        simulator.click(login_btn)
        
        # Secondo click immediato (durante animazione/richiesta)
        simulator.click(login_btn)
        
        # Attendi
        simulator.wait_for_animation(timeout_ms=5000)
        
        # No crash
        assert True
    
    def test_enter_key_submits_login(self, simulator, login_view, mock_backend, qtbot):
        """
        Scenario: Pressione Enter nel campo password fa submit.
        """
        username_input = login_view.findChild(QLineEdit, "username_input")
        password_input = login_view.findChild(QLineEdit, "password_input")
        
        simulator.type_text(username_input, "admin")
        simulator.type_text(password_input, "password")
        simulator.press_enter(password_input)
        
        # Verifica che login sia stato chiamato
        simulator.wait_for_animation()
        mock_backend.login.assert_called()
    
    def test_close_during_login_no_crash(self, simulator, login_view, mock_backend, qtbot):
        """
        Scenario: Chiusura finestra durante login non causa crash.
        """
        import time
        from unittest.mock import MagicMock
        
        # Mock login lento
        def slow_login(*args, **kwargs):
            time.sleep(1)
            return {"access_token": "test", "user_info": {}}
        
        mock_backend.login.side_effect = slow_login
        
        login_btn = login_view.findChild(QPushButton, "login_btn")
        simulator.click(login_btn)
        
        # Chiudi immediatamente
        login_view.close()
        
        # Attendi che il thread finisca
        qtbot.wait(2000)
        
        # No crash
        assert True
```

Esegui: `pytest tests/desktop_app/simulation/test_login_scenarios.py -v`
```

### Prompt 7.3 - Test Navigazione
```
FASE 7: User Simulation - Test Navigazione

Crea tests/desktop_app/simulation/test_navigation.py:

```python
"""
Test di simulazione per navigazione tra view.
"""

import pytest
from .user_actions import UserSimulator


class TestNavigationScenarios:
    """Test navigazione dell'applicazione."""
    
    @pytest.fixture
    def simulator(self, qtbot):
        return UserSimulator(qtbot)
    
    @pytest.fixture
    def logged_in_app(self, app_controller, mock_backend, qtbot):
        """App con login già effettuato."""
        # Simula login automatico
        app_controller._on_login_success({
            "access_token": "test",
            "user_info": {"id": 1, "username": "admin"}
        })
        
        # Attendi dashboard
        qtbot.waitUntil(
            lambda: hasattr(app_controller, 'main_window') and
                    app_controller.main_window.isVisible(),
            timeout=5000
        )
        
        return app_controller
    
    def test_navigate_all_views(self, simulator, logged_in_app, qtbot):
        """
        Scenario: Navigazione attraverso tutte le view.
        """
        main_window = logged_in_app.main_window
        
        views_to_test = [
            "database_view",
            "scadenzario_view", 
            "import_view",
            "validation_view",
            "config_view",
            "stats_view",
        ]
        
        for view_name in views_to_test:
            # Trova e clicca il menu item
            menu_item = main_window.findChild(QPushButton, f"{view_name}_btn")
            if menu_item:
                simulator.click(menu_item)
                simulator.wait_for_animation()
                
                # Verifica che la view sia caricata
                current_view = main_window.current_view()
                assert current_view is not None, f"View {view_name} not loaded"
    
    def test_rapid_view_switching(self, simulator, logged_in_app, qtbot):
        """
        Scenario: Cambio rapido tra view non causa crash.
        """
        main_window = logged_in_app.main_window
        
        # 20 cambi rapidi
        for i in range(20):
            view_idx = i % 3
            view_btns = ["database_btn", "scadenzario_btn", "import_btn"]
            
            btn = main_window.findChild(QPushButton, view_btns[view_idx])
            if btn:
                simulator.click(btn)
        
        # Attendi stabilizzazione
        simulator.wait_for_animation(timeout_ms=5000)
        
        # No crash
        assert main_window.isVisible()
    
    def test_logout_and_login_cycle(self, simulator, logged_in_app, mock_backend, qtbot):
        """
        Scenario: Ciclo logout/login multiplo.
        """
        for _ in range(3):
            main_window = logged_in_app.main_window
            
            # Trova e clicca logout
            logout_btn = main_window.findChild(QPushButton, "logout_btn")
            if logout_btn:
                simulator.click(logout_btn)
                simulator.wait_for_animation()
            
            # Dovremmo essere tornati al login
            login_view = logged_in_app.login_view
            simulator.wait_for_visible(login_view)
            
            # Ri-login
            username_input = login_view.findChild(QLineEdit, "username_input")
            password_input = login_view.findChild(QLineEdit, "password_input")
            login_btn = login_view.findChild(QPushButton, "login_btn")
            
            simulator.type_text(username_input, "admin")
            simulator.type_text(password_input, "password")
            simulator.click(login_btn)
            
            simulator.wait_for_animation(timeout_ms=3000)
```
```

### Prompt 7.4 - Stress Test
```
FASE 7: User Simulation - Stress Test

Crea tests/desktop_app/simulation/test_stress.py:

```python
"""
Stress test per verificare robustezza sotto carico.
"""

import pytest
import random
import time
from .user_actions import UserSimulator
from PyQt6.QtWidgets import QWidget, QPushButton, QLineEdit
from PyQt6.QtCore import Qt


class TestStressScenarios:
    """Stress test dell'applicazione."""
    
    @pytest.fixture
    def simulator(self, qtbot):
        sim = UserSimulator(qtbot)
        sim._action_delay_ms = 10  # Più veloce per stress test
        return sim
    
    def test_1000_random_actions(self, simulator, app_controller, qtbot):
        """
        Stress test: 1000 azioni random senza crash.
        """
        # Setup iniziale - vai a main window
        app_controller._on_login_success({
            "access_token": "test",
            "user_info": {"id": 1, "username": "admin"}
        })
        qtbot.wait(1000)
        
        main_window = app_controller.main_window
        crash_count = 0
        
        for i in range(1000):
            try:
                action = random.choice([
                    "click_random",
                    "key_press",
                    "focus_change",
                    "resize",
                ])
                
                if action == "click_random":
                    self._random_click(simulator, main_window)
                elif action == "key_press":
                    self._random_key(simulator, main_window)
                elif action == "focus_change":
                    self._random_focus(main_window)
                elif action == "resize":
                    self._random_resize(main_window)
                    
            except Exception as e:
                crash_count += 1
                print(f"Action {i} failed: {e}")
        
        # Deve completare con meno del 1% di errori
        assert crash_count < 10, f"Too many crashes: {crash_count}/1000"
    
    def _random_click(self, simulator, window):
        """Click su widget random."""
        widgets = window.findChildren(QWidget)
        clickable = [w for w in widgets if w.isVisible() and w.isEnabled()]
        if clickable:
            widget = random.choice(clickable)
            try:
                simulator.click(widget)
            except:
                pass
    
    def _random_key(self, simulator, window):
        """Pressione tasto random."""
        keys = [Qt.Key.Key_Tab, Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Space]
        key = random.choice(keys)
        try:
            simulator.press_key(window, key)
        except:
            pass
    
    def _random_focus(self, window):
        """Cambia focus random."""
        widgets = window.findChildren(QWidget)
        focusable = [w for w in widgets if w.isVisible() and w.focusPolicy() != Qt.FocusPolicy.NoFocus]
        if focusable:
            random.choice(focusable).setFocus()
    
    def _random_resize(self, window):
        """Resize random della finestra."""
        width = random.randint(800, 1920)
        height = random.randint(600, 1080)
        window.resize(width, height)
    
    def test_memory_stability(self, app_controller, qtbot):
        """
        Test: Memoria non cresce indefinitamente.
        """
        import tracemalloc
        
        tracemalloc.start()
        
        initial_memory = tracemalloc.get_traced_memory()[0]
        
        # 100 cicli di operazioni
        for _ in range(100):
            # Simula operazioni
            app_controller._on_login_success({"access_token": "t", "user_info": {}})
            qtbot.wait(100)
            app_controller._on_logout()
            qtbot.wait(100)
        
        final_memory = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()
        
        # Memoria non deve crescere più del 50%
        growth = (final_memory - initial_memory) / initial_memory
        assert growth < 0.5, f"Memory grew by {growth*100:.1f}%"
    
    def test_concurrent_animations(self, app_controller, qtbot):
        """
        Test: Animazioni concorrenti non causano crash.
        """
        from desktop_app.core.animation_manager import animation_manager, fade_in, fade_out
        
        # Crea 50 widget e animali tutti insieme
        widgets = []
        for i in range(50):
            w = QWidget()
            w.resize(100, 100)
            w.show()
            widgets.append(w)
        
        # Avvia animazioni concorrenti
        for w in widgets:
            fade_in(w, duration_ms=100)
        
        qtbot.wait(200)
        
        for w in widgets:
            fade_out(w, duration_ms=100)
        
        qtbot.wait(200)
        
        # Cleanup
        for w in widgets:
            w.close()
            w.deleteLater()
        
        # Verifica che non ci siano animazioni pendenti
        assert len(animation_manager._active_animations) == 0


@pytest.mark.slow
class TestLongRunningScenarios:
    """Test di lunga durata (marcati come slow)."""
    
    def test_24h_simulation(self, app_controller, qtbot):
        """
        Simula 24h di utilizzo compresso in minuti.
        """
        pytest.skip("Run manually with --runslow")
        
        # ... implementazione ...
```

Esegui: `pytest tests/desktop_app/simulation/test_stress.py -v` quando ultimato e passa procederemo all'ultima fase ovvero FASE 8: Documentation
```

---

## 📝 FASE 8: Documentation

### Prompt 8.1 - Update Documentazione
```
FASE 8: Documentation - Aggiornamento Docs

1. Crea docs/CRASH_ZERO_ARCHITECTURE.md documentando:
   - Widget Lifecycle Guard System
   - AnimationManager
   - Signal/Slot Hardening
   - Error Boundaries
   - State Machine
   - Test di simulazione utente

2. Aggiorna docs/DESKTOP_CLIENT.md:
   - Aggiungi sezione "Robustness Patterns"
   - Documenta nuovi moduli in desktop_app/core/
   - Aggiungi esempi di uso SafeWidgetMixin

3. Aggiorna docs/CONTRIBUTING.md:
   - Aggiungi regole per widget safety
   - Aggiungi regole per animazioni
   - Aggiungi regole per signal/slot

4. Aggiorna docs/TEST_GUIDE.md:
   - Aggiungi sezione "User Simulation Tests"
   - Documenta come creare nuovi scenari
   - Aggiungi esempi con UserSimulator

5. Verifica che tutti i link funzionino:
```bash
# Cerca link rotti
grep -r "\[.*\](.*\.md)" docs/ | while read line; do
    # Verifica che il file linkato esista
    echo "Checking: $line"
done
```
```

quando ultimato, procederemo alla  Checklist Finale.
---

## ✅ Checklist Finale

```
FASE 1: Widget Lifecycle Guard
□ desktop_app/core/widget_guard.py creato
□ desktop_app/mixins/safe_widget_mixin.py creato
□ login_view.py refactored
□ Test passano

FASE 2: Animation Manager
□ desktop_app/core/animation_manager.py creato
□ Helper functions implementate
□ animated_widgets.py refactored
□ login_view.py animazioni migrate
□ Test passano

FASE 3: Signal/Slot Hardening
□ desktop_app/core/signal_guard.py creato
□ Tutti i worker refactored
□ ConnectionTracker usato nelle view
□ Test passano

FASE 4: Error Boundaries
□ desktop_app/core/error_boundary.py creato
□ Tutte le view hanno ErrorBoundary
□ Recovery implementato
□ Test passano

FASE 5: State Machine
□ desktop_app/core/state_machine.py creato
□ main.py integrato con state machine
□ Transizioni gestite centralmente
□ Test passano

FASE 6: Observability
□ PostHog completamente rimosso
□ Sentry enhanced
□ Test passano
□ grep "posthog" vuoto

FASE 7: User Simulation
□ Framework simulazione creato
□ Test login scenarios
□ Test navigation
□ Stress test
□ Tutti i test passano

FASE 8: Documentation
□ CRASH_ZERO_ARCHITECTURE.md creato
□ DESKTOP_CLIENT.md aggiornato
□ CONTRIBUTING.md aggiornato
□ TEST_GUIDE.md aggiornato
```

---

**Fine CURSOR_PROMPTS_READY.md**

*Usa questi prompt in sequenza per guidare Cursor attraverso l'intera migrazione Crash Zero.*
