"""
Widget Guard - Protezione accesso a widget Qt.
"""

from __future__ import annotations

import weakref
import logging
from typing import TypeVar, Generic, Optional, Callable, Any, Dict
from functools import wraps
from contextlib import contextmanager

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=QWidget)


def is_widget_alive(widget: Optional[QWidget]) -> bool:
    """Verifica se un widget Qt e ancora vivo."""
    if widget is None:
        return False
    try:
        _ = widget.objectName()
        return True
    except RuntimeError:
        return False
    except AttributeError:
        return False


def is_qobject_alive(obj: Optional[QObject]) -> bool:
    """Verifica se un QObject e ancora vivo."""
    if obj is None:
        return False
    try:
        _ = obj.objectName()
        return True
    except RuntimeError:
        return False
    except AttributeError:
        return False


def guard_widget_access(func: Callable) -> Callable:
    """Decorator che protegge metodi che accedono a widget."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not is_widget_alive(self):
            logger.warning(f"Attempted to call {func.__name__} on destroyed widget {self.__class__.__name__}")
            return None
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if "deleted" in str(e).lower():
                logger.warning(f"Widget destroyed during {func.__name__} execution: {e}")
                return None
            raise
    return wrapper


def guard_widget_access_with_fallback(fallback_value: Any = None):
    """Decorator con valore di fallback configurabile."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not is_widget_alive(self):
                logger.warning(f"Returning fallback for {func.__name__} on destroyed widget")
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
    """Reference sicura a un widget usando weak reference."""
    
    def __init__(self, widget: T):
        self._ref: weakref.ref[T] = weakref.ref(widget)
        self._class_name = widget.__class__.__name__
    
    def get(self) -> Optional[T]:
        widget = self._ref()
        if widget is None:
            return None
        if not is_widget_alive(widget):
            return None
        return widget
    
    def is_alive(self) -> bool:
        return self.get() is not None
    
    def __bool__(self) -> bool:
        return self.is_alive()
    
    def __repr__(self) -> str:
        status = "alive" if self.is_alive() else "dead"
        return f"WidgetRef({self._class_name}, {status})"


@contextmanager
def safe_widget_context(widget: QWidget):
    """Context manager per operazioni sicure su widget."""
    if not is_widget_alive(widget):
        logger.debug("Widget gia distrutto all ingresso del context")
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
    """Classe helper per gestire gruppi di widget con protezione."""
    
    def __init__(self):
        self._refs: Dict[str, WidgetRef] = {}
    
    def register(self, name: str, widget: QWidget) -> None:
        if widget is None:
            logger.warning(f"Tentativo di registrare widget None con nome '{name}'")
            return
        self._refs[name] = WidgetRef(widget)
    
    def get(self, name: str) -> Optional[QWidget]:
        ref = self._refs.get(name)
        return ref.get() if ref else None
    
    def is_alive(self, name: str) -> bool:
        ref = self._refs.get(name)
        return ref.is_alive() if ref else False
    
    def all_alive(self) -> bool:
        return all(ref.is_alive() for ref in self._refs.values())
    
    def any_alive(self) -> bool:
        return any(ref.is_alive() for ref in self._refs.values())
    
    def alive_count(self) -> int:
        return sum(1 for ref in self._refs.values() if ref.is_alive())
    
    def cleanup_dead(self) -> int:
        dead_names = [name for name, ref in self._refs.items() if not ref.is_alive()]
        for name in dead_names:
            del self._refs[name]
        return len(dead_names)
    
    def clear(self) -> None:
        self._refs.clear()
    
    def names(self) -> list:
        return list(self._refs.keys())
    
    def __len__(self) -> int:
        return len(self._refs)
    
    def __contains__(self, name: str) -> bool:
        return name in self._refs
