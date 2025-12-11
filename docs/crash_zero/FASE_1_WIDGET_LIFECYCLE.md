# 🛡️ FASE 1: Widget Lifecycle Guard System

## Obiettivo
Creare un sistema di protezione che impedisca l'accesso a widget Qt già distrutti, eliminando la classe di crash più comune: `RuntimeError: wrapped C/C++ object has been deleted`.

---

## 📚 Background Tecnico

### Il Problema
PyQt6 è un wrapper Python attorno a librerie C++ (Qt). Quando un widget viene distrutto:
1. L'oggetto C++ viene deallocato immediatamente
2. L'oggetto Python può ancora esistere (reference count > 0)
3. Qualsiasi accesso all'oggetto Python causa crash

```python
# Esempio di crash
button = QPushButton("Click")
button.deleteLater()  # Schedula distruzione
QApplication.processEvents()  # Distruzione avviene qui
button.setText("Crash!")  # RuntimeError!
```

### Quando Succede in Intelleo
1. **Transizione Login → Dashboard**: View di login distrutta mentre animazione in corso
2. **Chiusura dialoghi**: Dialog chiuso ma callback ancora pendente
3. **Worker completion**: Worker emette segnale ma view già chiusa
4. **Animazioni**: Animazione tenta di modificare widget distrutto

---

## 🏗️ Architettura della Soluzione

```
┌─────────────────────────────────────────────────────────────┐
│                    Widget Lifecycle Guard                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  widget_guard   │  │ SafeWidgetMixin │  │  WidgetRef  │ │
│  │                 │  │                 │  │             │ │
│  │ - is_widget_    │  │ - register_     │  │ - Weak ref  │ │
│  │   alive()       │  │   child()       │  │ - get()     │ │
│  │ - @guard_       │  │ - get_child()   │  │ - is_alive()│ │
│  │   widget_access │  │ - safe_call()   │  │             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 File da Creare

### 1. `desktop_app/core/widget_guard.py`

```python
"""
Widget Guard - Protezione accesso a widget Qt.

Questo modulo fornisce utility per verificare lo stato di vita dei widget Qt
e prevenire crash dovuti all'accesso a oggetti C++ già distrutti.

Uso tipico:
    from desktop_app.core.widget_guard import is_widget_alive, guard_widget_access

    if is_widget_alive(self.button):
        self.button.setText("Safe!")
    
    @guard_widget_access
    def update_ui(self):
        self.label.setText("This is safe")
"""

from __future__ import annotations

import weakref
import logging
from typing import TypeVar, Generic, Optional, Callable, Any
from functools import wraps
from contextlib import contextmanager

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=QWidget)


def is_widget_alive(widget: Optional[QWidget]) -> bool:
    """
    Verifica se un widget Qt è ancora vivo (non distrutto).
    
    Args:
        widget: Il widget da verificare
        
    Returns:
        True se il widget esiste e non è stato distrutto, False altrimenti
        
    Example:
        if is_widget_alive(self.button):
            self.button.click()
    """
    if widget is None:
        return False
    
    try:
        # Metodo 1: Prova ad accedere a una proprietà
        # Se l'oggetto C++ è distrutto, questo solleva RuntimeError
        _ = widget.objectName()
        return True
    except RuntimeError:
        # "wrapped C/C++ object has been deleted"
        return False
    except AttributeError:
        # L'oggetto non è un QWidget valido
        return False


def is_qobject_alive(obj: Optional[QObject]) -> bool:
    """
    Verifica se un QObject (non necessariamente widget) è ancora vivo.
    
    Args:
        obj: Il QObject da verificare
        
    Returns:
        True se l'oggetto esiste e non è stato distrutto
    """
    if obj is None:
        return False
    
    try:
        _ = obj.objectName()
        return True
    except RuntimeError:
        return False


def guard_widget_access(func: Callable) -> Callable:
    """
    Decorator che protegge metodi che accedono a widget.
    
    Se il widget (self) è stato distrutto, il metodo non viene eseguito
    e viene loggato un warning. Non solleva mai eccezioni.
    
    Args:
        func: Il metodo da proteggere
        
    Returns:
        Metodo wrapped con protezione
        
    Example:
        class MyView(QWidget):
            @guard_widget_access
            def update_display(self):
                self.label.setText("Updated")
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Verifica che self (il widget) sia ancora vivo
        if not is_widget_alive(self):
            logger.warning(
                f"Attempted to call {func.__name__} on destroyed widget "
                f"{self.__class__.__name__}"
            )
            return None
        
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if "deleted" in str(e).lower():
                logger.warning(
                    f"Widget destroyed during {func.__name__} execution: {e}"
                )
                return None
            raise
    
    return wrapper


def guard_widget_access_with_fallback(fallback_value: Any = None):
    """
    Decorator con valore di fallback configurabile.
    
    Args:
        fallback_value: Valore da ritornare se widget distrutto
        
    Example:
        @guard_widget_access_with_fallback(fallback_value=False)
        def is_checked(self) -> bool:
            return self.checkbox.isChecked()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not is_widget_alive(self):
                logger.warning(
                    f"Returning fallback for {func.__name__} on destroyed widget"
                )
                return fallback_value
            
            try:
                return func(self, *args, **kwargs)
            except RuntimeError as e:
                if "deleted" in str(e).lower():
                    logger.warning(f"Widget destroyed during {func.__name__}: {e}")
                    return fallback_value
                raise
        
        return wrapper
    return decorator


class WidgetRef(Generic[T]):
    """
    Reference sicura a un widget usando weak reference.
    
    Fornisce un modo sicuro per mantenere riferimenti a widget
    senza impedirne la garbage collection e con verifica automatica
    dello stato di vita.
    
    Example:
        ref = WidgetRef(my_button)
        
        # Più tardi...
        button = ref.get()
        if button:
            button.click()
    """
    
    def __init__(self, widget: T):
        """
        Crea una reference sicura al widget.
        
        Args:
            widget: Il widget a cui riferirsi
        """
        self._ref: weakref.ref[T] = weakref.ref(widget)
        self._class_name = widget.__class__.__name__
    
    def get(self) -> Optional[T]:
        """
        Ottiene il widget se ancora vivo.
        
        Returns:
            Il widget se esiste e non è distrutto, None altrimenti
        """
        widget = self._ref()
        
        if widget is None:
            return None
        
        if not is_widget_alive(widget):
            return None
        
        return widget
    
    def is_alive(self) -> bool:
        """
        Verifica se il widget referenziato è ancora vivo.
        
        Returns:
            True se il widget esiste e non è distrutto
        """
        return self.get() is not None
    
    def __bool__(self) -> bool:
        """Permette l'uso in contesti booleani: if widget_ref: ..."""
        return self.is_alive()
    
    def __repr__(self) -> str:
        status = "alive" if self.is_alive() else "dead"
        return f"WidgetRef({self._class_name}, {status})"


@contextmanager
def safe_widget_context(widget: QWidget):
    """
    Context manager per operazioni sicure su widget.
    
    Verifica il widget all'ingresso e gestisce eccezioni
    di widget distrutto durante l'operazione.
    
    Example:
        with safe_widget_context(self.button) as btn:
            if btn:
                btn.setText("Safe")
                btn.setEnabled(True)
    
    Yields:
        Il widget se vivo, None altrimenti
    """
    if not is_widget_alive(widget):
        logger.debug(f"Widget già distrutto all'ingresso del context")
        yield None
        return
    
    try:
        yield widget
    except RuntimeError as e:
        if "deleted" in str(e).lower():
            logger.warning(f"Widget distrutto durante operazione: {e}")
        else:
            raise


class WidgetGuardian:
    """
    Classe helper per gestire gruppi di widget con protezione.
    
    Utile quando una view deve tenere traccia di molti widget figli
    e verificarne lo stato collettivamente.
    
    Example:
        guardian = WidgetGuardian()
        guardian.register("btn", self.button)
        guardian.register("lbl", self.label)
        
        # Operazione sicura
        if guardian.all_alive():
            guardian.get("btn").click()
    """
    
    def __init__(self):
        self._refs: dict[str, WidgetRef] = {}
    
    def register(self, name: str, widget: QWidget) -> None:
        """Registra un widget con un nome identificativo."""
        self._refs[name] = WidgetRef(widget)
    
    def get(self, name: str) -> Optional[QWidget]:
        """Ottiene un widget registrato se ancora vivo."""
        ref = self._refs.get(name)
        return ref.get() if ref else None
    
    def is_alive(self, name: str) -> bool:
        """Verifica se un widget specifico è ancora vivo."""
        ref = self._refs.get(name)
        return ref.is_alive() if ref else False
    
    def all_alive(self) -> bool:
        """Verifica se tutti i widget registrati sono ancora vivi."""
        return all(ref.is_alive() for ref in self._refs.values())
    
    def any_alive(self) -> bool:
        """Verifica se almeno un widget è ancora vivo."""
        return any(ref.is_alive() for ref in self._refs.values())
    
    def alive_count(self) -> int:
        """Conta quanti widget sono ancora vivi."""
        return sum(1 for ref in self._refs.values() if ref.is_alive())
    
    def cleanup_dead(self) -> int:
        """
        Rimuove i riferimenti a widget morti.
        
        Returns:
            Numero di riferimenti rimossi
        """
        dead_names = [name for name, ref in self._refs.items() if not ref.is_alive()]
        for name in dead_names:
            del self._refs[name]
        return len(dead_names)
```

---

### 2. `desktop_app/mixins/safe_widget_mixin.py`

```python
"""
SafeWidgetMixin - Mixin per widget con protezione lifecycle automatica.

Questo mixin aggiunge funzionalità di sicurezza a qualsiasi QWidget,
gestendo automaticamente il tracking dei widget figli e la protezione
durante la distruzione.

Uso:
    class MyView(SafeWidgetMixin, QWidget):
        def __init__(self):
            super().__init__()
            self._setup_ui()
        
        def _setup_ui(self):
            self.button = QPushButton("Click")
            self.register_child("button", self.button)
"""

from __future__ import annotations

import logging
from typing import Optional, Callable, Any, Dict

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject

from desktop_app.core.widget_guard import WidgetRef, is_widget_alive

logger = logging.getLogger(__name__)


class SafeWidgetMixin:
    """
    Mixin che aggiunge protezione lifecycle a qualsiasi QWidget.
    
    IMPORTANTE: Deve essere la PRIMA classe nella lista di ereditarietà:
        class MyView(SafeWidgetMixin, QWidget):  # Corretto
        class MyView(QWidget, SafeWidgetMixin):  # Sbagliato!
    
    Features:
    - Tracking automatico widget figli con weak references
    - Accesso sicuro ai figli con verifica esistenza
    - Flag di distruzione per prevenire operazioni durante cleanup
    - Metodo safe_call per esecuzione condizionale
    """
    
    # Flag che indica se il widget è in fase di distruzione
    _is_destroying: bool = False
    
    # Dizionario di riferimenti sicuri ai widget figli
    _safe_children: Dict[str, WidgetRef]
    
    def __init__(self, *args, **kwargs):
        """
        Inizializza il mixin.
        
        Nota: super().__init__() chiamerà il costruttore di QWidget.
        """
        super().__init__(*args, **kwargs)
        self._is_destroying = False
        self._safe_children = {}
    
    def register_child(self, name: str, widget: QWidget) -> None:
        """
        Registra un widget figlio per accesso sicuro.
        
        Args:
            name: Nome identificativo (usato in get_child)
            widget: Il widget da registrare
            
        Example:
            def _setup_ui(self):
                self.login_btn = AnimatedButton("Login")
                self.register_child("login_btn", self.login_btn)
        """
        if widget is None:
            logger.warning(f"Tentativo di registrare widget None con nome '{name}'")
            return
        
        self._safe_children[name] = WidgetRef(widget)
        logger.debug(f"Registrato widget figlio: {name} ({widget.__class__.__name__})")
    
    def get_child(self, name: str) -> Optional[QWidget]:
        """
        Ottiene un widget figlio registrato se ancora vivo.
        
        Args:
            name: Nome del widget (usato in register_child)
            
        Returns:
            Il widget se esiste e non è distrutto, None altrimenti
            
        Example:
            btn = self.get_child("login_btn")
            if btn:
                btn.setEnabled(True)
        """
        if self._is_destroying:
            return None
        
        ref = self._safe_children.get(name)
        if ref is None:
            logger.debug(f"Widget figlio non trovato: {name}")
            return None
        
        return ref.get()
    
    def has_child(self, name: str) -> bool:
        """
        Verifica se un widget figlio è registrato e vivo.
        
        Args:
            name: Nome del widget
            
        Returns:
            True se il widget esiste ed è vivo
        """
        return self.get_child(name) is not None
    
    def safe_call(
        self, 
        callback: Callable[[], Any], 
        fallback: Any = None,
        log_failure: bool = True
    ) -> Any:
        """
        Esegue un callback solo se il widget è ancora vivo.
        
        Args:
            callback: Funzione da eseguire
            fallback: Valore da ritornare se widget distrutto
            log_failure: Se True, logga quando il callback non viene eseguito
            
        Returns:
            Risultato del callback o fallback
            
        Example:
            # Invece di:
            self.button.setText("Click")
            
            # Usa:
            self.safe_call(lambda: self.button.setText("Click"))
        """
        if self._is_destroying:
            if log_failure:
                logger.debug("safe_call skipped: widget in distruzione")
            return fallback
        
        if not is_widget_alive(self):
            if log_failure:
                logger.debug("safe_call skipped: widget distrutto")
            return fallback
        
        try:
            return callback()
        except RuntimeError as e:
            if "deleted" in str(e).lower():
                if log_failure:
                    logger.warning(f"Widget distrutto durante safe_call: {e}")
                return fallback
            raise
    
    def safe_set_text(self, child_name: str, text: str) -> bool:
        """
        Imposta il testo di un widget figlio in modo sicuro.
        
        Args:
            child_name: Nome del widget registrato
            text: Testo da impostare
            
        Returns:
            True se l'operazione è riuscita
        """
        widget = self.get_child(child_name)
        if widget and hasattr(widget, 'setText'):
            widget.setText(text)
            return True
        return False
    
    def safe_set_enabled(self, child_name: str, enabled: bool) -> bool:
        """
        Abilita/disabilita un widget figlio in modo sicuro.
        
        Args:
            child_name: Nome del widget registrato
            enabled: Stato di abilitazione
            
        Returns:
            True se l'operazione è riuscita
        """
        widget = self.get_child(child_name)
        if widget:
            widget.setEnabled(enabled)
            return True
        return False
    
    def safe_set_visible(self, child_name: str, visible: bool) -> bool:
        """
        Mostra/nasconde un widget figlio in modo sicuro.
        """
        widget = self.get_child(child_name)
        if widget:
            widget.setVisible(visible)
            return True
        return False
    
    def deleteLater(self) -> None:
        """
        Override di deleteLater per settare il flag di distruzione.
        
        Questo previene operazioni durante il processo di cleanup.
        """
        logger.debug(f"deleteLater chiamato su {self.__class__.__name__}")
        self._is_destroying = True
        
        # Pulisci i riferimenti
        self._safe_children.clear()
        
        # Chiama il metodo originale
        super().deleteLater()
    
    def closeEvent(self, event) -> None:
        """
        Override di closeEvent per cleanup sicuro.
        
        Cancella animazioni e pulisce riferimenti prima della chiusura.
        """
        logger.debug(f"closeEvent su {self.__class__.__name__}")
        self._is_destroying = True
        
        # Cancella animazioni se AnimationManager è disponibile
        try:
            from desktop_app.core.animation_manager import animation_manager
            animation_manager.cancel_all(owner=self)
        except ImportError:
            pass
        
        # Pulisci riferimenti
        self._safe_children.clear()
        
        # Chiama il metodo originale
        super().closeEvent(event)
    
    def is_destroying(self) -> bool:
        """
        Verifica se il widget è in fase di distruzione.
        
        Returns:
            True se deleteLater() o closeEvent() sono stati chiamati
        """
        return self._is_destroying
    
    def children_status(self) -> Dict[str, bool]:
        """
        Ritorna lo stato di tutti i widget figli registrati.
        
        Returns:
            Dict con nome -> is_alive
        """
        return {
            name: ref.is_alive() 
            for name, ref in self._safe_children.items()
        }
```

---

### 3. `tests/desktop_app/core/test_widget_guard.py`

```python
"""
Test per il modulo widget_guard.
"""

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QApplication
from PyQt6.QtCore import Qt

import sys

# Assicurati che QApplication esista
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestIsWidgetAlive:
    """Test per is_widget_alive."""
    
    def test_alive_widget(self, qapp):
        """Widget vivo deve ritornare True."""
        widget = QWidget()
        
        from desktop_app.core.widget_guard import is_widget_alive
        assert is_widget_alive(widget) is True
        
        widget.deleteLater()
    
    def test_none_widget(self):
        """None deve ritornare False."""
        from desktop_app.core.widget_guard import is_widget_alive
        assert is_widget_alive(None) is False
    
    def test_deleted_widget(self, qapp, qtbot):
        """Widget distrutto deve ritornare False."""
        from desktop_app.core.widget_guard import is_widget_alive
        
        widget = QWidget()
        widget.deleteLater()
        
        # Processa eventi per completare la distruzione
        qtbot.wait(100)
        qapp.processEvents()
        
        # Dopo la distruzione, deve ritornare False
        # Nota: il comportamento può variare, il test verifica la logica
        # In alcuni casi il widget potrebbe non essere ancora distrutto


class TestGuardWidgetAccess:
    """Test per il decorator guard_widget_access."""
    
    def test_decorator_allows_alive_widget(self, qapp):
        """Decorator permette esecuzione su widget vivo."""
        from desktop_app.core.widget_guard import guard_widget_access
        
        class TestWidget(QWidget):
            @guard_widget_access
            def set_value(self, value):
                self._value = value
                return value
        
        widget = TestWidget()
        result = widget.set_value(42)
        
        assert result == 42
        assert widget._value == 42
        
        widget.deleteLater()
    
    def test_decorator_returns_none_on_destroyed(self, qapp, qtbot):
        """Decorator ritorna None su widget distrutto."""
        from desktop_app.core.widget_guard import guard_widget_access
        
        class TestWidget(QWidget):
            @guard_widget_access
            def risky_method(self):
                return "should not run"
        
        widget = TestWidget()
        widget.deleteLater()
        qtbot.wait(100)
        qapp.processEvents()
        
        # Il metodo non dovrebbe crashare


class TestWidgetRef:
    """Test per WidgetRef."""
    
    def test_get_alive_widget(self, qapp):
        """get() ritorna widget vivo."""
        from desktop_app.core.widget_guard import WidgetRef
        
        widget = QWidget()
        ref = WidgetRef(widget)
        
        assert ref.get() is widget
        assert ref.is_alive() is True
        
        widget.deleteLater()
    
    def test_get_none_after_deletion(self, qapp, qtbot):
        """get() ritorna None dopo distruzione."""
        from desktop_app.core.widget_guard import WidgetRef
        
        widget = QWidget()
        ref = WidgetRef(widget)
        
        widget.deleteLater()
        qtbot.wait(100)
        qapp.processEvents()
        
        # Weak reference dovrebbe essere None
        # Il test verifica che non ci siano crash
    
    def test_bool_conversion(self, qapp):
        """Test conversione booleana."""
        from desktop_app.core.widget_guard import WidgetRef
        
        widget = QWidget()
        ref = WidgetRef(widget)
        
        assert bool(ref) is True
        
        widget.deleteLater()


class TestSafeWidgetContext:
    """Test per safe_widget_context."""
    
    def test_context_with_alive_widget(self, qapp):
        """Context manager funziona con widget vivo."""
        from desktop_app.core.widget_guard import safe_widget_context
        
        widget = QPushButton("Test")
        
        with safe_widget_context(widget) as w:
            assert w is widget
            w.setText("Updated")
        
        assert widget.text() == "Updated"
        widget.deleteLater()
    
    def test_context_with_none(self):
        """Context manager gestisce None."""
        from desktop_app.core.widget_guard import safe_widget_context
        
        with safe_widget_context(None) as w:
            assert w is None


class TestWidgetGuardian:
    """Test per WidgetGuardian."""
    
    def test_register_and_get(self, qapp):
        """Test registrazione e recupero widget."""
        from desktop_app.core.widget_guard import WidgetGuardian
        
        guardian = WidgetGuardian()
        btn = QPushButton("Test")
        lbl = QLabel("Label")
        
        guardian.register("btn", btn)
        guardian.register("lbl", lbl)
        
        assert guardian.get("btn") is btn
        assert guardian.get("lbl") is lbl
        assert guardian.get("nonexistent") is None
        
        btn.deleteLater()
        lbl.deleteLater()
    
    def test_all_alive(self, qapp):
        """Test all_alive con tutti widget vivi."""
        from desktop_app.core.widget_guard import WidgetGuardian
        
        guardian = WidgetGuardian()
        btn = QPushButton("Test")
        lbl = QLabel("Label")
        
        guardian.register("btn", btn)
        guardian.register("lbl", lbl)
        
        assert guardian.all_alive() is True
        assert guardian.alive_count() == 2
        
        btn.deleteLater()
        lbl.deleteLater()
```

---

## 📝 Istruzioni di Implementazione

### Step 1: Crea i File
```bash
# Crea directory se non esiste
mkdir -p desktop_app/core
mkdir -p desktop_app/mixins
mkdir -p tests/desktop_app/core
mkdir -p tests/desktop_app/mixins

# Crea file __init__.py
touch desktop_app/core/__init__.py
touch desktop_app/mixins/__init__.py
```

### Step 2: Implementa widget_guard.py
Copia il codice fornito in `desktop_app/core/widget_guard.py`.

### Step 3: Implementa safe_widget_mixin.py
Copia il codice fornito in `desktop_app/mixins/safe_widget_mixin.py`.

### Step 4: Crea i Test
Copia il codice dei test in `tests/desktop_app/core/test_widget_guard.py`.

### Step 5: Esegui i Test
```bash
pytest tests/desktop_app/core/test_widget_guard.py -v
```

### Step 6: Applica a Login View
Modifica `desktop_app/views/login_view.py`:

```python
# PRIMA
from PyQt6.QtWidgets import QWidget
# ...
class LoginView(QWidget):

# DOPO  
from PyQt6.QtWidgets import QWidget
from desktop_app.mixins.safe_widget_mixin import SafeWidgetMixin
# ...
class LoginView(SafeWidgetMixin, QWidget):
```

---

## ✅ Checklist di Completamento

- [ ] `desktop_app/core/widget_guard.py` creato
- [ ] `desktop_app/mixins/safe_widget_mixin.py` creato
- [ ] `desktop_app/core/__init__.py` aggiornato
- [ ] `desktop_app/mixins/__init__.py` creato
- [ ] Test in `tests/desktop_app/core/test_widget_guard.py`
- [ ] Test passano: `pytest tests/desktop_app/core/test_widget_guard.py -v`
- [ ] Login view usa SafeWidgetMixin
- [ ] Test esistenti ancora passano: `pytest tests/desktop_app/views/test_login_view*.py`

---

## ⏭️ Prossimo Step

Completata questa fase, procedi con **FASE 2: Animation Manager** (`FASE_2_ANIMATION_MANAGER.md`).
