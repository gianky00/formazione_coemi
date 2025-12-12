"""
Error Boundary System - Gestione errori a livello view.

CRASH ZERO FASE 4 - Error Boundaries & Self-Healing

Questo modulo implementa un sistema di error boundaries ispirato a React,
che previene la propagazione di errori e permette recovery automatico.

Uso tipico:
    class MyView(QWidget):
        def __init__(self):
            self.error_boundary = ErrorBoundary(
                owner=self,
                on_error=self._handle_error,
                on_fatal=self._handle_fatal
            )
        
        @self.error_boundary.protect
        def risky_operation(self):
            # Codice che potrebbe fallire
            pass
"""

from __future__ import annotations

import logging
import traceback
from typing import Callable, Optional, Any, Type, Dict
from functools import wraps
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime

from PyQt6.QtWidgets import QWidget, QMessageBox

logger = logging.getLogger(__name__)


# ============================================================================
# Error Types
# ============================================================================

class ErrorSeverity(Enum):
    """Severità dell'errore."""
    LOW = auto()       # Warning, non blocca
    MEDIUM = auto()    # Errore recuperabile
    HIGH = auto()      # Errore grave, richiede attenzione
    CRITICAL = auto()  # Errore fatale, richiede chiusura


class ViewError(Exception):
    """Eccezione base per errori nelle view."""
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    recoverable: bool = True


class RecoverableError(ViewError):
    """
    Errore da cui la view può recuperare automaticamente.
    
    Esempio: errore di rete temporaneo, validazione fallita.
    """
    severity = ErrorSeverity.MEDIUM
    recoverable = True


class TransientError(ViewError):
    """
    Errore transitorio che probabilmente si risolverà da solo.
    
    Esempio: timeout, risorsa temporaneamente non disponibile.
    """
    severity = ErrorSeverity.LOW
    recoverable = True


class FatalViewError(ViewError):
    """
    Errore fatale che richiede la chiusura della view.
    
    Esempio: stato corrotto, dipendenza critica mancante.
    """
    severity = ErrorSeverity.CRITICAL
    recoverable = False


class StateCorruptionError(FatalViewError):
    """Errore specifico per corruzione dello stato."""
    pass


# ============================================================================
# Error Context
# ============================================================================

@dataclass
class ErrorContext:
    """Contesto di un errore per logging/reporting."""
    error: Exception
    view_name: str
    method_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    stack_trace: str = ""
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'error_type': type(self.error).__name__,
            'error_message': str(self.error),
            'view': self.view_name,
            'method': self.method_name,
            'timestamp': self.timestamp.isoformat(),
            'stack_trace': self.stack_trace,
            'extra': self.extra_data
        }


# ============================================================================
# Error Boundary
# ============================================================================

class ErrorBoundary:
    """
    Gestisce errori in una view con possibilità di recovery.
    
    Features:
    - Decoratore @protect per metodi rischiosi
    - Classificazione automatica errori
    - Conteggio errori con escalation automatica
    - Integrazione Sentry
    - Recovery automatico per errori transitori
    
    Example:
        class MyView(QWidget):
            def __init__(self):
                super().__init__()
                
                self.error_boundary = ErrorBoundary(
                    owner=self,
                    on_error=self._on_recoverable_error,
                    on_fatal=self._on_fatal_error,
                    max_errors=3
                )
            
            @property
            def protect(self):
                return self.error_boundary.protect
            
            @protect
            def do_risky_thing(self):
                # Codice protetto
                pass
            
            def _on_recoverable_error(self, ctx: ErrorContext):
                self._reset_ui_state()
                self._show_error_toast(str(ctx.error))
            
            def _on_fatal_error(self, ctx: ErrorContext):
                self.close()
    """
    
    def __init__(
        self,
        owner: QWidget,
        on_error: Optional[Callable[[ErrorContext], None]] = None,
        on_fatal: Optional[Callable[[ErrorContext], None]] = None,
        max_errors: int = 3,
        error_window_seconds: int = 60,
        report_to_sentry: bool = True,
        fallback_widget: Optional[Callable[[], QWidget]] = None
    ):
        """
        Args:
            owner: Widget proprietario
            on_error: Callback per errori recuperabili
            on_fatal: Callback per errori fatali
            max_errors: Numero massimo di errori prima di considerare fatale
            error_window_seconds: Finestra temporale per conteggio errori
            report_to_sentry: Se True, invia errori a Sentry
            fallback_widget: Factory per widget fallback in caso di errore fatale
        """
        self._owner = owner
        self._on_error = on_error or self._default_error_handler
        self._on_fatal = on_fatal or self._default_fatal_handler
        self._max_errors = max_errors
        self._error_window = error_window_seconds
        self._report_to_sentry = report_to_sentry
        self._fallback_widget = fallback_widget
        
        # Tracking errori
        self._error_history: list[ErrorContext] = []
        self._is_in_error_state = False
        
        logger.debug(f"ErrorBoundary creato per {owner.__class__.__name__}")
    
    def protect(self, func: Callable) -> Callable:
        """
        Decoratore che protegge un metodo.
        
        Example:
            @self.error_boundary.protect
            def risky_method(self):
                ...
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FatalViewError as e:
                self._handle_fatal(e, func.__name__)
            except RecoverableError as e:
                self._handle_recoverable(e, func.__name__)
            except TransientError as e:
                self._handle_transient(e, func.__name__)
            except Exception as e:
                self._handle_unknown(e, func.__name__)
            return None
        
        return wrapper
    
    def execute_safe(
        self, 
        func: Callable, 
        *args, 
        fallback: Any = None,
        **kwargs
    ) -> Any:
        """
        Esegue una funzione in modo protetto.
        
        Args:
            func: Funzione da eseguire
            *args: Argomenti posizionali
            fallback: Valore di ritorno in caso di errore
            **kwargs: Argomenti keyword
            
        Returns:
            Risultato della funzione o fallback
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self._handle_unknown(e, func.__name__)
            return fallback
    
    def _handle_recoverable(self, error: RecoverableError, method: str):
        """Gestisce errore recuperabile."""
        ctx = self._create_context(error, method)
        
        logger.warning(f"Recoverable error in {method}: {error}")
        self._record_error(ctx)
        self._report_error(ctx)
        
        # Verifica se troppi errori
        if self._should_escalate():
            self._handle_fatal(
                FatalViewError(f"Too many errors: {error}"),
                method
            )
            return
        
        self._on_error(ctx)
    
    def _handle_transient(self, error: TransientError, method: str):
        """Gestisce errore transitorio."""
        ctx = self._create_context(error, method)
        
        logger.info(f"Transient error in {method}: {error}")
        self._record_error(ctx)
        
        # Non riporta a Sentry per errori transitori (troppo rumore)
        # Solo callback locale
        self._on_error(ctx)
    
    def _handle_fatal(self, error: FatalViewError, method: str):
        """Gestisce errore fatale."""
        ctx = self._create_context(error, method)
        
        logger.error(f"Fatal error in {method}: {error}")
        self._report_error(ctx, force=True)
        
        self._is_in_error_state = True
        self._on_fatal(ctx)
        
        if self._fallback_widget:
            self._show_fallback()
    
    def _handle_unknown(self, error: Exception, method: str):
        """Gestisce errore sconosciuto (non classificato)."""
        ctx = self._create_context(error, method)
        
        logger.exception(f"Unknown error in {method}")
        self._record_error(ctx)
        self._report_error(ctx)
        
        # Errori sconosciuti: tratta come recuperabili ma con cautela
        if self._should_escalate():
            self._handle_fatal(FatalViewError(str(error)), method)
        else:
            self._on_error(ctx)
    
    def _create_context(self, error: Exception, method: str) -> ErrorContext:
        """Crea contesto errore."""
        return ErrorContext(
            error=error,
            view_name=self._owner.__class__.__name__,
            method_name=method,
            stack_trace=traceback.format_exc(),
            extra_data=self._collect_extra_data()
        )
    
    def _collect_extra_data(self) -> Dict[str, Any]:
        """Raccoglie dati extra per il contesto."""
        data = {}
        
        try:
            data['widget_visible'] = self._owner.isVisible()
            data['widget_enabled'] = self._owner.isEnabled()
            
            if hasattr(self._owner, 'objectName'):
                data['object_name'] = self._owner.objectName()
                
        except RuntimeError:
            data['widget_destroyed'] = True
        
        return data
    
    def _record_error(self, ctx: ErrorContext):
        """Registra errore nella history."""
        self._error_history.append(ctx)
        
        # Pulisci errori vecchi
        cutoff = datetime.now().timestamp() - self._error_window
        self._error_history = [
            e for e in self._error_history
            if e.timestamp.timestamp() > cutoff
        ]
    
    def _should_escalate(self) -> bool:
        """Verifica se gli errori devono essere escalati a fatali."""
        return len(self._error_history) >= self._max_errors
    
    def _report_error(self, ctx: ErrorContext, force: bool = False):
        """Invia errore a Sentry."""
        if not self._report_to_sentry and not force:
            return
        
        try:
            import sentry_sdk
            
            if not sentry_sdk.is_initialized():
                return
            
            with sentry_sdk.push_scope() as scope:
                scope.set_tag("view", ctx.view_name)
                scope.set_tag("method", ctx.method_name)
                scope.set_extra("context", ctx.to_dict())
                
                sentry_sdk.capture_exception(ctx.error)
                
        except ImportError:
            logger.debug("Sentry non disponibile")
        except Exception as e:
            logger.error(f"Errore invio a Sentry: {e}")
    
    def _show_fallback(self):
        """Mostra widget fallback."""
        if not self._fallback_widget:
            return
        
        try:
            fallback = self._fallback_widget()
            # Sostituisci contenuto del widget owner con fallback
            # Implementazione dipende dal layout specifico
        except Exception as e:
            logger.error(f"Errore creazione fallback widget: {e}")
    
    def _default_error_handler(self, ctx: ErrorContext):
        """Handler di default per errori recuperabili."""
        try:
            from desktop_app.components.toast import Toast
            Toast.warning(
                self._owner,
                "Si è verificato un errore",
                str(ctx.error)[:100]
            )
        except ImportError:
            pass
        except Exception:
            # Fallback silenzioso se Toast non disponibile
            pass
    
    def _default_fatal_handler(self, ctx: ErrorContext):
        """Handler di default per errori fatali."""
        try:
            QMessageBox.critical(
                self._owner,
                "Errore Critico",
                f"Si è verificato un errore critico:\n\n"
                f"{ctx.error}\n\n"
                f"La vista verrà chiusa."
            )
        except RuntimeError:
            # Widget già distrutto
            pass
    
    # === Public API ===
    
    def reset(self):
        """Resetta lo stato dell'error boundary."""
        self._error_history.clear()
        self._is_in_error_state = False
    
    def is_in_error_state(self) -> bool:
        """Verifica se siamo in stato di errore."""
        return self._is_in_error_state
    
    def error_count(self) -> int:
        """Ritorna il numero di errori nella finestra temporale."""
        return len(self._error_history)


# ============================================================================
# Decorator Standalone
# ============================================================================

def error_boundary(
    on_error: Optional[Callable[[Exception], None]] = None,
    recoverable: bool = True,
    log_level: int = logging.WARNING
):
    """
    Decoratore standalone per metodi singoli.
    
    Utile quando non si vuole un ErrorBoundary completo.
    
    Example:
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
                logger.log(log_level, f"Error in {func.__name__}: {e}")
                
                if on_error:
                    on_error(e)
                elif not recoverable:
                    raise
                
                return None
        return wrapper
    return decorator


def suppress_errors(
    *exception_types: Type[Exception],
    default: Any = None,
    log: bool = True
):
    """
    Decoratore che sopprime specifiche eccezioni.
    
    Example:
        @suppress_errors(ValueError, KeyError, default=[])
        def get_items(self):
            ...
    """
    if not exception_types:
        exception_types = (Exception,)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_types as e:
                if log:
                    logger.debug(f"Suppressed {type(e).__name__} in {func.__name__}: {e}")
                return default
        return wrapper
    return decorator


# ============================================================================
# Recovery Helpers
# ============================================================================

class UIStateRecovery:
    """
    Helper per recovery dello stato UI.
    
    Example:
        recovery = UIStateRecovery(view)
        
        # In caso di errore
        recovery.reset_buttons()
        recovery.clear_inputs()
        recovery.hide_loading()
    """
    
    def __init__(self, widget: QWidget):
        self._widget = widget
    
    def reset_buttons(self):
        """Resetta tutti i bottoni a stato default."""
        from PyQt6.QtWidgets import QPushButton
        
        for btn in self._widget.findChildren(QPushButton):
            try:
                btn.setEnabled(True)
                if hasattr(btn, 'set_loading'):
                    btn.set_loading(False)
            except RuntimeError:
                pass
    
    def clear_inputs(self):
        """Resetta stato input senza cancellare contenuto."""
        from PyQt6.QtWidgets import QLineEdit
        
        for input_widget in self._widget.findChildren(QLineEdit):
            try:
                input_widget.setEnabled(True)
            except RuntimeError:
                pass
    
    def hide_loading(self):
        """Nasconde indicatori di caricamento."""
        for child in self._widget.findChildren(QWidget):
            try:
                name = child.objectName().lower()
                if 'loading' in name or 'spinner' in name:
                    child.hide()
            except RuntimeError:
                pass
    
    def reset_all(self):
        """Esegue reset completo."""
        self.reset_buttons()
        self.clear_inputs()
        self.hide_loading()


__all__ = [
    # Error Types
    'ViewError',
    'RecoverableError',
    'TransientError',
    'FatalViewError',
    'StateCorruptionError',
    'ErrorSeverity',
    # Core
    'ErrorBoundary',
    'ErrorContext',
    # Decorators
    'error_boundary',
    'suppress_errors',
    # Recovery
    'UIStateRecovery',
]
