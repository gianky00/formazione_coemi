"""
SafeWidgetMixin - Mixin per widget con protezione lifecycle automatica.

CRASH ZERO FASE 1 + FASE 3: Widget Lifecycle + Signal/Slot Protection
"""

from __future__ import annotations

import logging
from typing import Optional, Callable, Any, Dict

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject

from desktop_app.core.widget_guard import WidgetRef, is_widget_alive

logger = logging.getLogger(__name__)


# Re-export signal guard utilities for convenience
try:
    from desktop_app.core.signal_guard import (
        ConnectionTracker,
        SafeSignalEmitter,
        safe_emit,
    )
except ImportError:
    ConnectionTracker = None
    SafeSignalEmitter = None
    safe_emit = None


class SafeWidgetMixin:
    """
    Mixin che aggiunge protezione lifecycle a qualsiasi QWidget.
    
    IMPORTANTE: Deve essere la PRIMA classe nella lista di ereditarieta:
        class MyView(SafeWidgetMixin, QWidget):  # Corretto
        class MyView(QWidget, SafeWidgetMixin):  # Sbagliato!
    """
    
    _is_destroying: bool = False
    _safe_children: Dict[str, WidgetRef]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_destroying = False
        self._safe_children = {}
    
    def register_child(self, name: str, widget: QWidget) -> None:
        """Registra un widget figlio per accesso sicuro."""
        if widget is None:
            logger.warning(f"Tentativo di registrare widget None con nome '{name}'")
            return
        self._safe_children[name] = WidgetRef(widget)
        logger.debug(f"Registrato widget figlio: {name} ({widget.__class__.__name__})")
    
    def unregister_child(self, name: str) -> None:
        """Rimuove un widget dalla lista dei figli registrati."""
        if name in self._safe_children:
            del self._safe_children[name]
            logger.debug(f"Rimosso widget figlio: {name}")
    
    def get_child(self, name: str) -> Optional[QWidget]:
        """Ottiene un widget figlio registrato se ancora vivo."""
        if self._is_destroying:
            return None
        ref = self._safe_children.get(name)
        if ref is None:
            logger.debug(f"Widget figlio non trovato: {name}")
            return None
        return ref.get()
    
    def has_child(self, name: str) -> bool:
        """Verifica se un widget figlio e registrato e vivo."""
        return self.get_child(name) is not None
    
    def safe_call(self, callback: Callable[[], Any], fallback: Any = None, log_failure: bool = True) -> Any:
        """Esegue un callback solo se il widget e ancora vivo."""
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
        """Imposta il testo di un widget figlio in modo sicuro."""
        widget = self.get_child(child_name)
        if widget and hasattr(widget, 'setText'):
            try:
                widget.setText(text)
                return True
            except RuntimeError:
                return False
        return False
    
    def safe_set_enabled(self, child_name: str, enabled: bool) -> bool:
        """Abilita/disabilita un widget figlio in modo sicuro."""
        widget = self.get_child(child_name)
        if widget:
            try:
                widget.setEnabled(enabled)
                return True
            except RuntimeError:
                return False
        return False
    
    def safe_set_visible(self, child_name: str, visible: bool) -> bool:
        """Mostra/nasconde un widget figlio in modo sicuro."""
        widget = self.get_child(child_name)
        if widget:
            try:
                widget.setVisible(visible)
                return True
            except RuntimeError:
                return False
        return False
    
    def safe_get_text(self, child_name: str, default: str = "") -> str:
        """Ottiene il testo di un widget figlio in modo sicuro."""
        widget = self.get_child(child_name)
        if widget and hasattr(widget, 'text'):
            try:
                return widget.text()
            except RuntimeError:
                return default
        return default
    
    def deleteLater(self) -> None:
        """Override di deleteLater per settare il flag di distruzione."""
        logger.debug(f"deleteLater chiamato su {self.__class__.__name__}")
        self._is_destroying = True
        self._safe_children.clear()
        self._cancel_pending_animations()
        super().deleteLater()
    
    def closeEvent(self, event) -> None:
        """Override di closeEvent per cleanup sicuro."""
        logger.debug(f"closeEvent su {self.__class__.__name__}")
        self._is_destroying = True
        self._cancel_pending_animations()
        self._safe_children.clear()
        super().closeEvent(event)
    
    def _cancel_pending_animations(self) -> None:
        """Cancella tutte le animazioni pendenti associate a questo widget."""
        try:
            from desktop_app.core.animation_manager import animation_manager
            animation_manager.cancel_all(owner=self)
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"Errore cancellazione animazioni: {e}")
    
    def is_destroying(self) -> bool:
        """Verifica se il widget e in fase di distruzione."""
        return self._is_destroying
    
    def is_safe(self) -> bool:
        """Verifica se e sicuro eseguire operazioni sul widget."""
        if self._is_destroying:
            return False
        return is_widget_alive(self)
    
    def children_status(self) -> Dict[str, bool]:
        """Ritorna lo stato di tutti i widget figli registrati."""
        return {name: ref.is_alive() for name, ref in self._safe_children.items()}
    
    def alive_children_count(self) -> int:
        """Conta quanti widget figli sono ancora vivi."""
        return sum(1 for ref in self._safe_children.values() if ref.is_alive())
    
    def registered_children_names(self) -> list:
        """Ritorna la lista dei nomi dei widget figli registrati."""
        return list(self._safe_children.keys())
