# 🎬 FASE 2: Animation Manager Centralizzato

## Obiettivo
Creare un sistema centralizzato per la gestione di tutte le animazioni PyQt6, con tracking, timeout automatico e cancellazione sicura.

---

## 📚 Background Tecnico

### Il Problema
Le animazioni in PyQt6 sono oggetti indipendenti che:
1. Possono continuare a eseguire dopo la distruzione del widget target
2. Non hanno timeout automatico (possono bloccarsi)
3. Sono difficili da cancellare in modo coordinato
4. Possono causare crash se accedono a widget distrutti

```python
# Esempio problematico
def _animate_exit(self):
    self.anim = QPropertyAnimation(self.container, b"opacity")
    self.anim.finished.connect(self._on_exit_done)
    self.anim.start()
    
# Se la view viene distrutta durante l'animazione:
# - self.anim continua a eseguire
# - _on_exit_done viene chiamato con self distrutto → CRASH
```

### Soluzione: AnimationManager
Un singleton che:
- Registra tutte le animazioni con owner (widget proprietario)
- Cancella automaticamente le animazioni quando l'owner viene distrutto
- Implementa timeout per animazioni bloccate
- Fornisce helper per animazioni comuni (fade, slide)

---

## 🏗️ Architettura

```
┌─────────────────────────────────────────────────────────────────────┐
│                       AnimationManager                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────┐ │
│  │  Active Registry │    │  Timeout Manager │    │   Helpers    │ │
│  │                  │    │                  │    │              │ │
│  │  Dict[id, Entry] │    │  QTimer per anim │    │  fade_in()   │ │
│  │  WeakRef owners  │    │  Auto-cancel     │    │  fade_out()  │ │
│  │  Cleanup hooks   │    │  Callback        │    │  slide_*()   │ │
│  └──────────────────┘    └──────────────────┘    └──────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     Public API                                │  │
│  │  register() | cancel_all() | cancel_by_id() | is_animating() │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📁 File da Creare

### 1. `desktop_app/core/animation_manager.py`

```python
"""
AnimationManager - Gestione centralizzata di tutte le animazioni PyQt6.

Questo modulo fornisce un sistema robusto per:
- Registrazione e tracking di animazioni attive
- Cancellazione sicura per owner (widget che ha creato l'animazione)
- Timeout automatico per animazioni bloccate
- Helper per animazioni comuni (fade, slide, etc.)

Uso tipico:
    from desktop_app.core.animation_manager import animation_manager, fade_out
    
    # Registrazione manuale
    anim = QPropertyAnimation(widget, b"opacity")
    animation_manager.register(anim, owner=self)
    
    # Helper (registra automaticamente)
    fade_out(widget, duration_ms=300, on_finished=self._on_done)
    
    # Cancellazione (tipicamente in closeEvent)
    animation_manager.cancel_all(owner=self)
"""

from __future__ import annotations

import uuid
import weakref
import logging
from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, Any, Literal
from enum import Enum, auto

from PyQt6.QtCore import (
    QObject, QTimer, QPropertyAnimation, QAbstractAnimation,
    QSequentialAnimationGroup, QParallelAnimationGroup,
    QEasingCurve, QPoint, QRect, pyqtSignal
)
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect

logger = logging.getLogger(__name__)


class AnimationState(Enum):
    """Stato di un'animazione registrata."""
    PENDING = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()
    CANCELLED = auto()
    TIMEOUT = auto()


@dataclass
class AnimationEntry:
    """Entry per un'animazione registrata."""
    id: str
    animation: QAbstractAnimation
    owner_ref: weakref.ref
    name: str
    timeout_ms: int
    on_finished: Optional[Callable]
    on_timeout: Optional[Callable]
    state: AnimationState = AnimationState.PENDING
    timeout_timer: Optional[QTimer] = field(default=None, repr=False)
    
    def get_owner(self) -> Optional[QObject]:
        """Ottiene l'owner se ancora vivo."""
        return self.owner_ref()


class AnimationManager(QObject):
    """
    Singleton per gestione globale delle animazioni.
    
    Features:
    - Registrazione con owner tracking
    - Timeout automatico configurabile
    - Cancellazione per owner o ID
    - Statistiche e monitoring
    
    Signals:
        animation_started(str): Emesso quando un'animazione inizia (id)
        animation_finished(str): Emesso quando un'animazione termina (id)
        animation_cancelled(str): Emesso quando un'animazione viene cancellata (id)
        animation_timeout(str): Emesso quando un'animazione va in timeout (id)
    """
    
    # Signals
    animation_started = pyqtSignal(str)
    animation_finished = pyqtSignal(str)
    animation_cancelled = pyqtSignal(str)
    animation_timeout = pyqtSignal(str)
    
    # Singleton
    _instance: Optional['AnimationManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Evita re-inizializzazione del singleton
        if hasattr(self, '_initialized'):
            return
        
        super().__init__()
        self._initialized = True
        
        # Registry delle animazioni attive
        self._animations: Dict[str, AnimationEntry] = {}
        
        # Statistiche
        self._total_registered = 0
        self._total_cancelled = 0
        self._total_timeout = 0
        
        logger.info("AnimationManager inizializzato")
    
    @classmethod
    def instance(cls) -> 'AnimationManager':
        """Ottiene l'istanza singleton."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register(
        self,
        animation: QAbstractAnimation,
        owner: QObject,
        name: str = "",
        timeout_ms: int = 5000,
        on_finished: Optional[Callable] = None,
        on_timeout: Optional[Callable] = None,
        auto_start: bool = False
    ) -> str:
        """
        Registra un'animazione per il tracking.
        
        Args:
            animation: L'animazione da registrare
            owner: Widget proprietario (per cleanup automatico)
            name: Nome identificativo opzionale
            timeout_ms: Timeout dopo cui l'animazione viene cancellata (0 = no timeout)
            on_finished: Callback al completamento
            on_timeout: Callback in caso di timeout
            auto_start: Se True, avvia l'animazione automaticamente
            
        Returns:
            ID univoco dell'animazione
        """
        # Genera ID univoco
        anim_id = str(uuid.uuid4())[:8]
        
        # Verifica owner
        if owner is None:
            logger.warning(f"Registrazione animazione senza owner: {name}")
        
        # Crea entry
        entry = AnimationEntry(
            id=anim_id,
            animation=animation,
            owner_ref=weakref.ref(owner) if owner else weakref.ref(QObject()),
            name=name or f"anim_{anim_id}",
            timeout_ms=timeout_ms,
            on_finished=on_finished,
            on_timeout=on_timeout
        )
        
        # Connetti segnali dell'animazione
        animation.finished.connect(lambda: self._on_animation_finished(anim_id))
        animation.stateChanged.connect(
            lambda new, old: self._on_state_changed(anim_id, new, old)
        )
        
        # Setup timeout timer
        if timeout_ms > 0:
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._on_timeout(anim_id))
            entry.timeout_timer = timer
        
        # Registra
        self._animations[anim_id] = entry
        self._total_registered += 1
        
        logger.debug(f"Animazione registrata: {entry.name} (id={anim_id}, owner={owner.__class__.__name__ if owner else 'None'})")
        
        # Auto-start se richiesto
        if auto_start:
            self.start(anim_id)
        
        return anim_id
    
    def start(self, anim_id: str) -> bool:
        """
        Avvia un'animazione registrata.
        
        Args:
            anim_id: ID dell'animazione
            
        Returns:
            True se avviata con successo
        """
        entry = self._animations.get(anim_id)
        if not entry:
            logger.warning(f"Animazione non trovata: {anim_id}")
            return False
        
        # Verifica owner ancora vivo
        owner = entry.get_owner()
        if owner is None:
            logger.warning(f"Owner distrutto, cancello animazione: {entry.name}")
            self._cleanup_entry(anim_id)
            return False
        
        # Avvia timeout timer
        if entry.timeout_timer:
            entry.timeout_timer.start(entry.timeout_ms)
        
        # Avvia animazione
        entry.animation.start()
        entry.state = AnimationState.RUNNING
        
        self.animation_started.emit(anim_id)
        logger.debug(f"Animazione avviata: {entry.name}")
        
        return True
    
    def cancel(self, anim_id: str) -> bool:
        """
        Cancella un'animazione specifica.
        
        Args:
            anim_id: ID dell'animazione
            
        Returns:
            True se cancellata
        """
        entry = self._animations.get(anim_id)
        if not entry:
            return False
        
        return self._cancel_entry(entry, emit_signal=True)
    
    def cancel_all(self, owner: QObject) -> int:
        """
        Cancella tutte le animazioni di un owner.
        
        Args:
            owner: Widget le cui animazioni vanno cancellate
            
        Returns:
            Numero di animazioni cancellate
        """
        if owner is None:
            return 0
        
        # Trova tutte le animazioni dell'owner
        to_cancel = [
            anim_id for anim_id, entry in self._animations.items()
            if entry.get_owner() is owner
        ]
        
        # Cancella
        count = 0
        for anim_id in to_cancel:
            if self.cancel(anim_id):
                count += 1
        
        if count > 0:
            logger.debug(f"Cancellate {count} animazioni per {owner.__class__.__name__}")
        
        return count
    
    def cancel_all_global(self) -> int:
        """
        Cancella TUTTE le animazioni (emergency stop).
        
        Returns:
            Numero di animazioni cancellate
        """
        count = 0
        for anim_id in list(self._animations.keys()):
            if self.cancel(anim_id):
                count += 1
        
        logger.warning(f"Emergency stop: cancellate {count} animazioni globali")
        return count
    
    def is_animating(self, owner: QObject) -> bool:
        """
        Verifica se un owner ha animazioni attive.
        
        Args:
            owner: Widget da verificare
            
        Returns:
            True se ci sono animazioni running
        """
        for entry in self._animations.values():
            if entry.get_owner() is owner and entry.state == AnimationState.RUNNING:
                return True
        return False
    
    def wait_completion(
        self,
        owner: QObject,
        timeout_ms: int = 5000
    ) -> bool:
        """
        Attende il completamento di tutte le animazioni di un owner.
        
        NOTA: Questo blocca l'event loop. Usare con cautela.
        
        Args:
            owner: Widget le cui animazioni attendere
            timeout_ms: Timeout massimo
            
        Returns:
            True se tutte completate, False se timeout
        """
        from PyQt6.QtCore import QEventLoop
        
        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        
        # Controlla periodicamente
        check_timer = QTimer()
        check_timer.setInterval(50)
        check_timer.timeout.connect(
            lambda: loop.quit() if not self.is_animating(owner) else None
        )
        
        timer.start(timeout_ms)
        check_timer.start()
        
        loop.exec()
        
        timer.stop()
        check_timer.stop()
        
        return not self.is_animating(owner)
    
    def get_active_count(self) -> int:
        """Ritorna il numero di animazioni attive."""
        return len(self._animations)
    
    def get_stats(self) -> Dict[str, int]:
        """Ritorna statistiche sull'uso."""
        return {
            'active': len(self._animations),
            'total_registered': self._total_registered,
            'total_cancelled': self._total_cancelled,
            'total_timeout': self._total_timeout,
        }
    
    # === Private Methods ===
    
    def _cancel_entry(self, entry: AnimationEntry, emit_signal: bool = True) -> bool:
        """Cancella una singola entry."""
        try:
            # Ferma timeout timer
            if entry.timeout_timer:
                entry.timeout_timer.stop()
            
            # Ferma animazione
            if entry.animation.state() != QAbstractAnimation.State.Stopped:
                entry.animation.stop()
            
            entry.state = AnimationState.CANCELLED
            self._total_cancelled += 1
            
            # Rimuovi dal registry
            if entry.id in self._animations:
                del self._animations[entry.id]
            
            if emit_signal:
                self.animation_cancelled.emit(entry.id)
            
            logger.debug(f"Animazione cancellata: {entry.name}")
            return True
            
        except RuntimeError as e:
            # Oggetto già distrutto
            logger.debug(f"Errore cancellazione animazione (già distrutta): {e}")
            if entry.id in self._animations:
                del self._animations[entry.id]
            return True
    
    def _cleanup_entry(self, anim_id: str):
        """Pulisce una entry (senza cancellare l'animazione)."""
        if anim_id in self._animations:
            entry = self._animations[anim_id]
            if entry.timeout_timer:
                entry.timeout_timer.stop()
            del self._animations[anim_id]
    
    def _on_animation_finished(self, anim_id: str):
        """Callback quando un'animazione termina naturalmente."""
        entry = self._animations.get(anim_id)
        if not entry:
            return
        
        entry.state = AnimationState.FINISHED
        
        # Ferma timeout timer
        if entry.timeout_timer:
            entry.timeout_timer.stop()
        
        # Callback
        if entry.on_finished:
            try:
                entry.on_finished()
            except Exception as e:
                logger.error(f"Errore in on_finished callback: {e}")
        
        # Cleanup
        self._cleanup_entry(anim_id)
        self.animation_finished.emit(anim_id)
        
        logger.debug(f"Animazione completata: {entry.name}")
    
    def _on_timeout(self, anim_id: str):
        """Callback quando un'animazione va in timeout."""
        entry = self._animations.get(anim_id)
        if not entry:
            return
        
        logger.warning(f"Animazione in timeout: {entry.name} (>{entry.timeout_ms}ms)")
        
        entry.state = AnimationState.TIMEOUT
        self._total_timeout += 1
        
        # Callback timeout
        if entry.on_timeout:
            try:
                entry.on_timeout()
            except Exception as e:
                logger.error(f"Errore in on_timeout callback: {e}")
        
        # Forza cancellazione
        self._cancel_entry(entry, emit_signal=False)
        self.animation_timeout.emit(anim_id)
    
    def _on_state_changed(
        self,
        anim_id: str,
        new_state: QAbstractAnimation.State,
        old_state: QAbstractAnimation.State
    ):
        """Callback quando lo stato dell'animazione cambia."""
        entry = self._animations.get(anim_id)
        if not entry:
            return
        
        if new_state == QAbstractAnimation.State.Running:
            entry.state = AnimationState.RUNNING
        elif new_state == QAbstractAnimation.State.Paused:
            entry.state = AnimationState.PAUSED
        elif new_state == QAbstractAnimation.State.Stopped:
            # Gestito da _on_animation_finished
            pass


# === Singleton globale ===
animation_manager = AnimationManager.instance()


# === Helper Functions ===

def fade_out(
    widget: QWidget,
    duration_ms: int = 300,
    on_finished: Optional[Callable] = None,
    easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic
) -> Optional[str]:
    """
    Animazione fade out di un widget.
    
    Args:
        widget: Widget da animare
        duration_ms: Durata in millisecondi
        on_finished: Callback al completamento
        easing: Curva di easing
        
    Returns:
        ID dell'animazione o None se widget non valido
    """
    from desktop_app.core.widget_guard import is_widget_alive
    
    if not is_widget_alive(widget):
        logger.warning("fade_out: widget non valido")
        if on_finished:
            on_finished()
        return None
    
    # Crea opacity effect se non presente
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsOpacityEffect):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
    
    # Crea animazione
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration_ms)
    anim.setStartValue(1.0)
    anim.setEndValue(0.0)
    anim.setEasingCurve(easing)
    
    # Registra e avvia
    anim_id = animation_manager.register(
        animation=anim,
        owner=widget,
        name=f"fade_out_{widget.__class__.__name__}",
        on_finished=on_finished,
        auto_start=True
    )
    
    return anim_id


def fade_in(
    widget: QWidget,
    duration_ms: int = 300,
    on_finished: Optional[Callable] = None,
    easing: QEasingCurve.Type = QEasingCurve.Type.InCubic
) -> Optional[str]:
    """
    Animazione fade in di un widget.
    """
    from desktop_app.core.widget_guard import is_widget_alive
    
    if not is_widget_alive(widget):
        logger.warning("fade_in: widget non valido")
        if on_finished:
            on_finished()
        return None
    
    # Crea opacity effect
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsOpacityEffect):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
    
    effect.setOpacity(0.0)
    
    # Crea animazione
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration_ms)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(easing)
    
    anim_id = animation_manager.register(
        animation=anim,
        owner=widget,
        name=f"fade_in_{widget.__class__.__name__}",
        on_finished=on_finished,
        auto_start=True
    )
    
    return anim_id


def slide_out(
    widget: QWidget,
    direction: Literal['left', 'right', 'up', 'down'] = 'left',
    duration_ms: int = 300,
    on_finished: Optional[Callable] = None
) -> Optional[str]:
    """
    Animazione slide out di un widget.
    """
    from desktop_app.core.widget_guard import is_widget_alive
    
    if not is_widget_alive(widget):
        if on_finished:
            on_finished()
        return None
    
    start_pos = widget.pos()
    end_pos = QPoint(start_pos)
    
    # Calcola posizione finale
    if direction == 'left':
        end_pos.setX(-widget.width())
    elif direction == 'right':
        end_pos.setX(widget.parent().width() if widget.parent() else 1920)
    elif direction == 'up':
        end_pos.setY(-widget.height())
    elif direction == 'down':
        end_pos.setY(widget.parent().height() if widget.parent() else 1080)
    
    anim = QPropertyAnimation(widget, b"pos")
    anim.setDuration(duration_ms)
    anim.setStartValue(start_pos)
    anim.setEndValue(end_pos)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    anim_id = animation_manager.register(
        animation=anim,
        owner=widget,
        name=f"slide_out_{direction}_{widget.__class__.__name__}",
        on_finished=on_finished,
        auto_start=True
    )
    
    return anim_id


def slide_in(
    widget: QWidget,
    direction: Literal['left', 'right', 'up', 'down'] = 'right',
    duration_ms: int = 300,
    on_finished: Optional[Callable] = None
) -> Optional[str]:
    """
    Animazione slide in di un widget.
    """
    from desktop_app.core.widget_guard import is_widget_alive
    
    if not is_widget_alive(widget):
        if on_finished:
            on_finished()
        return None
    
    end_pos = widget.pos()
    start_pos = QPoint(end_pos)
    
    # Calcola posizione iniziale (fuori schermo)
    if direction == 'left':
        start_pos.setX(widget.parent().width() if widget.parent() else 1920)
    elif direction == 'right':
        start_pos.setX(-widget.width())
    elif direction == 'up':
        start_pos.setY(widget.parent().height() if widget.parent() else 1080)
    elif direction == 'down':
        start_pos.setY(-widget.height())
    
    widget.move(start_pos)
    
    anim = QPropertyAnimation(widget, b"pos")
    anim.setDuration(duration_ms)
    anim.setStartValue(start_pos)
    anim.setEndValue(end_pos)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    anim_id = animation_manager.register(
        animation=anim,
        owner=widget,
        name=f"slide_in_{direction}_{widget.__class__.__name__}",
        on_finished=on_finished,
        auto_start=True
    )
    
    return anim_id


def animate_property(
    target: QObject,
    property_name: bytes,
    end_value: Any,
    start_value: Optional[Any] = None,
    duration_ms: int = 300,
    easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
    on_finished: Optional[Callable] = None,
    owner: Optional[QObject] = None
) -> Optional[str]:
    """
    Helper generico per animare qualsiasi proprietà Qt.
    
    Args:
        target: Oggetto con la proprietà
        property_name: Nome della proprietà (es. b"geometry")
        end_value: Valore finale
        start_value: Valore iniziale (None = valore corrente)
        duration_ms: Durata
        easing: Curva di easing
        on_finished: Callback
        owner: Owner per tracking (default = target)
    """
    from desktop_app.core.widget_guard import is_qobject_alive
    
    if not is_qobject_alive(target):
        if on_finished:
            on_finished()
        return None
    
    anim = QPropertyAnimation(target, property_name)
    anim.setDuration(duration_ms)
    
    if start_value is not None:
        anim.setStartValue(start_value)
    
    anim.setEndValue(end_value)
    anim.setEasingCurve(easing)
    
    anim_id = animation_manager.register(
        animation=anim,
        owner=owner or target,
        name=f"prop_{property_name.decode()}_{target.__class__.__name__}",
        on_finished=on_finished,
        auto_start=True
    )
    
    return anim_id
```

---

### 2. `tests/desktop_app/core/test_animation_manager.py`

```python
"""
Test per AnimationManager.
"""

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import QPropertyAnimation
import sys


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestAnimationManager:
    """Test per AnimationManager."""
    
    def test_singleton(self):
        """Verifica che sia singleton."""
        from desktop_app.core.animation_manager import AnimationManager
        
        am1 = AnimationManager.instance()
        am2 = AnimationManager.instance()
        
        assert am1 is am2
    
    def test_register_animation(self, qapp):
        """Test registrazione animazione."""
        from desktop_app.core.animation_manager import animation_manager
        
        widget = QWidget()
        anim = QPropertyAnimation(widget, b"pos")
        
        anim_id = animation_manager.register(
            animation=anim,
            owner=widget,
            name="test_anim"
        )
        
        assert anim_id is not None
        assert len(anim_id) == 8
        
        # Cleanup
        animation_manager.cancel(anim_id)
        widget.deleteLater()
    
    def test_cancel_all_by_owner(self, qapp):
        """Test cancellazione per owner."""
        from desktop_app.core.animation_manager import animation_manager
        
        widget = QWidget()
        
        # Registra 3 animazioni
        ids = []
        for i in range(3):
            anim = QPropertyAnimation(widget, b"pos")
            anim_id = animation_manager.register(anim, owner=widget)
            ids.append(anim_id)
        
        # Cancella tutte
        count = animation_manager.cancel_all(owner=widget)
        
        assert count == 3
        
        widget.deleteLater()
    
    def test_is_animating(self, qapp, qtbot):
        """Test verifica animazioni attive."""
        from desktop_app.core.animation_manager import animation_manager
        
        widget = QWidget()
        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setDuration(1000)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        
        anim_id = animation_manager.register(
            anim, 
            owner=widget,
            auto_start=True
        )
        
        # Dovrebbe essere in esecuzione
        assert animation_manager.is_animating(widget) is True
        
        # Cancella
        animation_manager.cancel(anim_id)
        
        assert animation_manager.is_animating(widget) is False
        
        widget.deleteLater()


class TestAnimationHelpers:
    """Test per helper functions."""
    
    def test_fade_out(self, qapp, qtbot):
        """Test fade_out helper."""
        from desktop_app.core.animation_manager import fade_out, animation_manager
        
        widget = QWidget()
        widget.show()
        
        finished = MagicMock()
        
        anim_id = fade_out(
            widget,
            duration_ms=100,
            on_finished=finished
        )
        
        assert anim_id is not None
        
        # Attendi completamento
        qtbot.wait(200)
        
        # Callback chiamato
        finished.assert_called_once()
        
        widget.deleteLater()
    
    def test_fade_out_dead_widget(self, qapp):
        """Test fade_out su widget morto."""
        from desktop_app.core.animation_manager import fade_out
        
        finished = MagicMock()
        
        # Widget None
        anim_id = fade_out(None, on_finished=finished)
        
        assert anim_id is None
        finished.assert_called_once()  # Callback chiamato comunque
    
    def test_animate_property(self, qapp, qtbot):
        """Test animate_property helper."""
        from desktop_app.core.animation_manager import animate_property
        
        widget = QWidget()
        widget.setWindowOpacity(0.0)
        
        finished = MagicMock()
        
        anim_id = animate_property(
            target=widget,
            property_name=b"windowOpacity",
            end_value=1.0,
            duration_ms=100,
            on_finished=finished
        )
        
        assert anim_id is not None
        
        qtbot.wait(200)
        
        finished.assert_called_once()
        
        widget.deleteLater()
```

---

## 📝 Istruzioni di Implementazione

### Step 1: Crea animation_manager.py
Copia il codice in `desktop_app/core/animation_manager.py`.

### Step 2: Aggiorna __init__.py
```python
# desktop_app/core/__init__.py
from .widget_guard import is_widget_alive, guard_widget_access, WidgetRef
from .animation_manager import (
    animation_manager, 
    fade_in, fade_out, 
    slide_in, slide_out,
    animate_property
)
```

### Step 3: Crea i Test
Copia in `tests/desktop_app/core/test_animation_manager.py`.

### Step 4: Esegui Test
```bash
pytest tests/desktop_app/core/test_animation_manager.py -v
```

### Step 5: Refactoring animated_widgets.py
Modifica `desktop_app/components/animated_widgets.py` per usare gli helper.

### Step 6: Refactoring login_view.py
Sostituisci le animazioni manuali con gli helper.

---

## ✅ Checklist di Completamento

- [ ] `desktop_app/core/animation_manager.py` creato
- [ ] Test passano
- [ ] `animated_widgets.py` refactored
- [ ] `login_view.py` animazioni migrate
- [ ] Tutte le view con animazioni usano AnimationManager
- [ ] `closeEvent` in ogni view cancella animazioni

---

## ⏭️ Prossimo Step

Completata questa fase, procedi con **FASE 3: Signal/Slot Hardening** (`FASE_3_SIGNAL_SLOT.md`).
