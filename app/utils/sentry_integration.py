"""
Enhanced Sentry Integration con context Qt-aware.

CRASH ZERO - FASE 6: Observability

Features:
- Breadcrumbs per azioni UI
- Context con stato applicazione
- Tag per versione e ambiente
- Filtri per errori non critici
"""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Conditional imports to handle test mocking
try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
    _SENTRY_AVAILABLE = True
except (ImportError, AttributeError):
    sentry_sdk = None
    LoggingIntegration = None
    _SENTRY_AVAILABLE = False


def init_sentry(
    dsn: str,
    environment: str = "production",
    release: Optional[str] = None,
    debug: bool = False
):
    """
    Inizializza Sentry con configurazione ottimizzata per Intelleo.
    
    Args:
        dsn: Sentry Data Source Name
        environment: Environment name (production, development, staging)
        release: Application version/release
        debug: Enable debug mode
    """
    if not _SENTRY_AVAILABLE:
        logger.warning("Sentry SDK not available, skipping initialization")
        return
        
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
        if exc_type.__name__ in ('ConnectionError', 'TimeoutError', 'ConnectionRefusedError'):
            return None
        # Skip common Qt RuntimeErrors
        if exc_type.__name__ == 'RuntimeError':
            msg = str(exc_value).lower()
            if 'wrapped c/c++ object' in msg or 'deleted' in msg:
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
    
    Args:
        action: Action type (click, navigate, input, etc.)
        view: View name where action occurred
        data: Additional context data
    """
    if not _SENTRY_AVAILABLE:
        return
    sentry_sdk.add_breadcrumb(
        category="ui",
        message=f"{action} in {view}",
        level="info",
        data=data or {}
    )


def set_user_context(user_id: str, username: str):
    """
    Imposta context utente (senza PII sensibili).
    
    Args:
        user_id: User identifier
        username: Username
    """
    if not _SENTRY_AVAILABLE:
        return
    sentry_sdk.set_user({
        "id": user_id,
        "username": username,
    })


def clear_user_context():
    """Rimuove il context utente (on logout)."""
    if not _SENTRY_AVAILABLE:
        return
    sentry_sdk.set_user(None)


def capture_view_error(
    view_name: str,
    error: Exception,
    extra: Optional[Dict] = None
):
    """
    Cattura errore con context della view.
    
    Args:
        view_name: Name of the view where error occurred
        error: The exception to capture
        extra: Additional context data
    """
    if not _SENTRY_AVAILABLE:
        return
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("view", view_name)
        scope.set_extra("view_data", extra or {})
        sentry_sdk.capture_exception(error)


def capture_state_transition_error(
    from_state: str,
    to_state: str,
    error: Exception
):
    """
    Cattura errore durante transizione di stato.
    
    Args:
        from_state: State transitioning from
        to_state: State transitioning to
        error: The exception that occurred
    """
    if not _SENTRY_AVAILABLE:
        return
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("state_transition", f"{from_state}_to_{to_state}")
        scope.set_context("state_machine", {
            "from_state": from_state,
            "to_state": to_state,
        })
        sentry_sdk.capture_exception(error)


def add_state_breadcrumb(
    from_state: str,
    to_state: str,
    transition: Optional[str] = None
):
    """
    Aggiunge breadcrumb per transizione di stato.
    
    Args:
        from_state: Previous state
        to_state: New state
        transition: Transition name/trigger
    """
    if not _SENTRY_AVAILABLE:
        return
    sentry_sdk.add_breadcrumb(
        category="state_machine",
        message=f"State: {from_state} -> {to_state}",
        level="info",
        data={"transition": transition} if transition else {}
    )
