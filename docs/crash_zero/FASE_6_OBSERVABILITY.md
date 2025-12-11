# 👁️ FASE 6: Observability Refactor

## Obiettivo
Rimuovere completamente PostHog e potenziare l'integrazione con Sentry per un monitoring robusto e rispettoso della privacy.

---

## 📚 Background

### Perché Rimuovere PostHog
- Non più necessario per le analytics attuali
- Riduce complessità e dipendenze
- Migliora privacy utenti
- Sentry è sufficiente per error tracking e monitoring

### Cosa Potenziare in Sentry
- Breadcrumbs per azioni UI
- Context Qt-aware
- Performance monitoring
- Structured logging

---

## 🏗️ Piano di Lavoro

### 1. Rimozione PostHog

```bash
# Trova tutti i riferimenti
grep -r "posthog" --include="*.py" -l

# File tipici da controllare:
# - app/core/analytics.py (se esiste)
# - desktop_app/main.py
# - launcher.py
# - requirements.txt
```

### 2. Enhanced Sentry

Creare un modulo centralizzato per Sentry con features specifiche per PyQt6.

---

## 📁 File da Creare/Modificare

### 1. `desktop_app/core/observability.py`

```python
"""
Observability - Sistema centralizzato di monitoring e logging.

Questo modulo fornisce:
- Integrazione Sentry ottimizzata per PyQt6
- Structured logging
- UI breadcrumbs
- Performance tracking
- Error context enrichment

Uso:
    from desktop_app.core.observability import (
        init_observability,
        log_ui_action,
        log_error,
        track_performance
    )
    
    # All'avvio
    init_observability(
        sentry_dsn="https://...",
        environment="production"
    )
    
    # Durante l'uso
    log_ui_action("click", "LoginView", {"button": "submit"})
"""

from __future__ import annotations

import logging
import time
import platform
from typing import Optional, Dict, Any, Callable
from functools import wraps
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)

# Flag per verificare se Sentry è inizializzato
_sentry_initialized = False


def init_observability(
    sentry_dsn: Optional[str] = None,
    environment: str = "development",
    release: Optional[str] = None,
    debug: bool = False,
    sample_rate: float = 1.0,
    traces_sample_rate: float = 0.1,
    enable_logging_integration: bool = True
) -> bool:
    """
    Inizializza il sistema di observability.
    
    Args:
        sentry_dsn: DSN Sentry (None per disabilitare)
        environment: Nome ambiente (production, staging, development)
        release: Versione dell'app
        debug: Abilita debug mode
        sample_rate: Percentuale errori da inviare (0.0-1.0)
        traces_sample_rate: Percentuale transazioni per performance
        enable_logging_integration: Integra con logging Python
        
    Returns:
        True se Sentry è stato inizializzato
    """
    global _sentry_initialized
    
    # Setup logging base
    _setup_logging(debug)
    
    if not sentry_dsn:
        logger.info("Sentry DSN not provided, running without Sentry")
        return False
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
        
        integrations = []
        
        if enable_logging_integration:
            integrations.append(
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                )
            )
        
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            release=release,
            debug=debug,
            
            # Sampling
            sample_rate=sample_rate,
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=traces_sample_rate,
            
            # Privacy
            send_default_pii=False,
            
            # Integrations
            integrations=integrations,
            
            # Hooks
            before_send=_before_send,
            before_breadcrumb=_before_breadcrumb,
        )
        
        # Set default tags
        sentry_sdk.set_tag("platform", platform.system())
        sentry_sdk.set_tag("python_version", platform.python_version())
        
        _sentry_initialized = True
        logger.info(f"Sentry initialized (env={environment})")
        return True
        
    except ImportError:
        logger.warning("sentry_sdk not installed")
        return False
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False


def _setup_logging(debug: bool = False):
    """Configura il logging dell'applicazione."""
    level = logging.DEBUG if debug else logging.INFO
    
    # Format strutturato
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Riduci verbosità di alcuni moduli
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)


def _before_send(event: Dict, hint: Dict) -> Optional[Dict]:
    """
    Hook chiamato prima di inviare un evento a Sentry.
    
    Usato per:
    - Filtrare eventi non necessari
    - Arricchire con context Qt
    - Sanitizzare dati sensibili
    """
    # Filtra errori di rete comuni
    if 'exc_info' in hint:
        exc_type, exc_value, _ = hint['exc_info']
        exc_name = exc_type.__name__ if exc_type else ''
        
        # Skip errori di connessione (troppo comuni)
        if exc_name in ('ConnectionError', 'TimeoutError', 'ConnectTimeout'):
            return None
        
        # Skip errori Qt di widget distrutto (gestiti internamente)
        if exc_name == 'RuntimeError' and 'deleted' in str(exc_value).lower():
            return None
    
    # Aggiungi context Qt
    event['contexts'] = event.get('contexts', {})
    event['contexts']['qt'] = _get_qt_context()
    event['contexts']['app'] = _get_app_context()
    
    return event


def _before_breadcrumb(crumb: Dict, hint: Dict) -> Optional[Dict]:
    """
    Hook per filtrare/modificare breadcrumbs.
    """
    # Skip HTTP breadcrumbs troppo verbosi
    if crumb.get('category') == 'http':
        if crumb.get('level') == 'info':
            return None
    
    return crumb


def _get_qt_context() -> Dict[str, Any]:
    """Raccoglie informazioni sullo stato Qt."""
    context = {}
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QT_VERSION_STR
        
        context['qt_version'] = QT_VERSION_STR
        
        app = QApplication.instance()
        if app:
            # Finestra attiva
            active_window = app.activeWindow()
            if active_window:
                context['active_window'] = active_window.__class__.__name__
            
            # Widget con focus
            focus_widget = app.focusWidget()
            if focus_widget:
                context['focus_widget'] = focus_widget.__class__.__name__
            
            # Numero finestre aperte
            context['window_count'] = len(app.topLevelWidgets())
            
    except Exception:
        pass
    
    return context


def _get_app_context() -> Dict[str, Any]:
    """Raccoglie informazioni sullo stato dell'app."""
    context = {}
    
    try:
        from desktop_app.core.app_state_machine import get_state_machine
        
        sm = get_state_machine()
        context['state'] = sm.current_state().name
        context['previous_state'] = sm.previous_state().name if sm.previous_state() else None
        
    except Exception:
        pass
    
    return context


# === Public API ===

def log_ui_action(
    action: str,
    view: str,
    data: Optional[Dict[str, Any]] = None,
    level: str = "info"
):
    """
    Registra un'azione UI come breadcrumb Sentry.
    
    Args:
        action: Tipo di azione (click, input, navigate, etc.)
        view: Nome della view
        data: Dati aggiuntivi
        level: Livello (info, warning, error)
        
    Example:
        log_ui_action("click", "LoginView", {"button": "submit"})
        log_ui_action("navigate", "DatabaseView")
    """
    if not _sentry_initialized:
        return
    
    try:
        import sentry_sdk
        
        sentry_sdk.add_breadcrumb(
            category="ui",
            message=f"{action} in {view}",
            level=level,
            data=data or {}
        )
        
    except Exception as e:
        logger.debug(f"Failed to log UI action: {e}")


def log_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    tags: Optional[Dict[str, str]] = None,
    level: str = "error"
):
    """
    Registra un errore con context arricchito.
    
    Args:
        error: L'eccezione da registrare
        context: Dati di context aggiuntivi
        tags: Tag per categorizzazione
        level: Livello (error, warning, fatal)
    """
    # Log locale sempre
    logger.exception(f"Error: {error}")
    
    if not _sentry_initialized:
        return
    
    try:
        import sentry_sdk
        
        with sentry_sdk.push_scope() as scope:
            if tags:
                for key, value in tags.items():
                    scope.set_tag(key, value)
            
            if context:
                for key, value in context.items():
                    scope.set_extra(key, value)
            
            scope.level = level
            sentry_sdk.capture_exception(error)
            
    except Exception as e:
        logger.debug(f"Failed to send to Sentry: {e}")


def set_user(user_id: str, username: Optional[str] = None):
    """
    Imposta il context utente per Sentry.
    
    NOTA: Non inviare PII sensibili (email, nome completo, etc.)
    
    Args:
        user_id: ID utente (può essere hash)
        username: Username (opzionale)
    """
    if not _sentry_initialized:
        return
    
    try:
        import sentry_sdk
        
        sentry_sdk.set_user({
            "id": user_id,
            "username": username,
        })
        
    except Exception:
        pass


def clear_user():
    """Rimuove il context utente (es. dopo logout)."""
    if not _sentry_initialized:
        return
    
    try:
        import sentry_sdk
        sentry_sdk.set_user(None)
    except Exception:
        pass


@contextmanager
def track_performance(name: str, op: str = "function"):
    """
    Context manager per tracking performance.
    
    Args:
        name: Nome dell'operazione
        op: Tipo operazione (function, db, http, etc.)
        
    Example:
        with track_performance("load_certificates", "db"):
            certificates = db.get_all_certificates()
    """
    start_time = time.time()
    
    try:
        if _sentry_initialized:
            import sentry_sdk
            with sentry_sdk.start_span(op=op, description=name):
                yield
        else:
            yield
    finally:
        duration = time.time() - start_time
        logger.debug(f"Performance: {name} took {duration:.3f}s")


def track_function(op: str = "function"):
    """
    Decorator per tracking automatico di funzioni.
    
    Example:
        @track_function("db")
        def load_data():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with track_performance(func.__name__, op):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def capture_message(message: str, level: str = "info"):
    """
    Invia un messaggio a Sentry (non un errore).
    
    Args:
        message: Il messaggio
        level: Livello (info, warning, error)
    """
    logger.log(
        getattr(logging, level.upper(), logging.INFO),
        message
    )
    
    if not _sentry_initialized:
        return
    
    try:
        import sentry_sdk
        sentry_sdk.capture_message(message, level=level)
    except Exception:
        pass


def add_breadcrumb(
    category: str,
    message: str,
    level: str = "info",
    data: Optional[Dict] = None
):
    """
    Aggiunge un breadcrumb generico.
    
    Args:
        category: Categoria (ui, http, query, etc.)
        message: Messaggio
        level: Livello
        data: Dati aggiuntivi
    """
    if not _sentry_initialized:
        return
    
    try:
        import sentry_sdk
        sentry_sdk.add_breadcrumb(
            category=category,
            message=message,
            level=level,
            data=data or {}
        )
    except Exception:
        pass
```

---

### 2. Script di Pulizia PostHog

```bash
#!/bin/bash
# cleanup_posthog.sh
# Script per rimuovere tutti i riferimenti a PostHog

echo "🔍 Cercando riferimenti a PostHog..."

# Trova tutti i file con posthog
files=$(grep -r "posthog" --include="*.py" -l 2>/dev/null)

if [ -z "$files" ]; then
    echo "✅ Nessun riferimento a PostHog trovato!"
    exit 0
fi

echo "📁 File con riferimenti PostHog:"
echo "$files"
echo ""

echo "📝 Dettagli riferimenti:"
grep -r "posthog" --include="*.py" -n

echo ""
echo "⚠️  Rimuovi manualmente i riferimenti dai file sopra elencati."
echo ""
echo "Cose da rimuovere:"
echo "  - import posthog"
echo "  - posthog.init(...)"
echo "  - posthog.capture(...)"
echo "  - posthog.identify(...)"
echo "  - Qualsiasi altra chiamata posthog.*"
echo ""
echo "Dopo la rimozione, rimuovi anche da requirements.txt:"
echo "  - posthog"
```

---

### 3. Pattern di Migrazione

#### PRIMA (con PostHog):
```python
import posthog

# Inizializzazione
posthog.project_api_key = "..."

# Tracking evento
posthog.capture(
    distinct_id=user_id,
    event="login_success",
    properties={"method": "password"}
)
```

#### DOPO (con Sentry):
```python
from desktop_app.core.observability import (
    init_observability,
    log_ui_action,
    set_user
)

# Inizializzazione
init_observability(
    sentry_dsn="https://...",
    environment="production"
)

# Tracking azione UI
set_user(user_id)
log_ui_action("login", "LoginView", {"method": "password"})
```

---

### 4. Integrazione nel Launcher

```python
# launcher.py

from desktop_app.core.observability import init_observability
import os

def main():
    # Inizializza observability
    sentry_dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("ENVIRONMENT", "development")
    version = os.getenv("APP_VERSION", "0.0.0")
    
    init_observability(
        sentry_dsn=sentry_dsn,
        environment=environment,
        release=f"intelleo@{version}",
        debug=(environment == "development")
    )
    
    # ... resto dell'avvio
```

---

### 5. `tests/desktop_app/core/test_observability.py`

```python
"""
Test per il modulo observability.
"""

import pytest
from unittest.mock import MagicMock, patch
import logging


class TestObservability:
    """Test per funzioni observability."""
    
    def test_init_without_sentry(self):
        """Test inizializzazione senza Sentry DSN."""
        from desktop_app.core.observability import init_observability
        
        result = init_observability(sentry_dsn=None)
        
        assert result is False
    
    @patch('sentry_sdk.init')
    def test_init_with_sentry(self, mock_init):
        """Test inizializzazione con Sentry."""
        from desktop_app.core import observability
        observability._sentry_initialized = False
        
        result = observability.init_observability(
            sentry_dsn="https://test@sentry.io/123",
            environment="test"
        )
        
        assert result is True
        mock_init.assert_called_once()
    
    def test_log_ui_action_without_sentry(self):
        """Test log UI quando Sentry non è inizializzato."""
        from desktop_app.core import observability
        observability._sentry_initialized = False
        
        # Non deve sollevare eccezioni
        observability.log_ui_action("click", "TestView", {"button": "test"})
    
    @patch('sentry_sdk.add_breadcrumb')
    def test_log_ui_action_with_sentry(self, mock_breadcrumb):
        """Test log UI con Sentry."""
        from desktop_app.core import observability
        observability._sentry_initialized = True
        
        observability.log_ui_action("click", "TestView", {"button": "test"})
        
        mock_breadcrumb.assert_called_once()
    
    def test_track_performance_timing(self):
        """Test che track_performance misuri il tempo."""
        from desktop_app.core.observability import track_performance
        import time
        
        with track_performance("test_op"):
            time.sleep(0.1)
        
        # Non deve sollevare eccezioni
    
    def test_track_function_decorator(self):
        """Test decorator track_function."""
        from desktop_app.core.observability import track_function
        
        @track_function("test")
        def my_function():
            return 42
        
        result = my_function()
        assert result == 42
```

---

## 📝 Istruzioni di Implementazione

### Step 1: Cerca Riferimenti PostHog
```bash
grep -r "posthog" --include="*.py" -l
grep -r "posthog" --include="*.txt" -l
grep -r "posthog" --include="*.toml" -l
```

### Step 2: Rimuovi da Ogni File

Per ogni file trovato:
1. Rimuovi `import posthog`
2. Rimuovi `posthog.init()` o configurazione
3. Rimuovi tutte le chiamate `posthog.capture()`, `posthog.identify()`, etc.
4. Se il file diventa vuoto (es. `analytics.py`), eliminalo

### Step 3: Rimuovi da Requirements
```bash
# Modifica requirements.txt
# Rimuovi la riga con "posthog"
```

### Step 4: Crea observability.py
Copia il codice in `desktop_app/core/observability.py`.

### Step 5: Aggiorna Launcher
Integra `init_observability()` nel launcher.

### Step 6: Verifica Rimozione Completa
```bash
# Deve ritornare vuoto
grep -r "posthog" --include="*.py"
```

### Step 7: Test
```bash
pytest tests/desktop_app/core/test_observability.py -v
pytest tests/ -v  # Tutti i test devono passare
```

---

## ✅ Checklist di Completamento

- [ ] `grep -r "posthog"` ritorna vuoto
- [ ] `posthog` rimosso da requirements.txt
- [ ] `desktop_app/core/observability.py` creato
- [ ] Launcher integra `init_observability()`
- [ ] Test passano
- [ ] App si avvia senza errori
- [ ] Sentry riceve eventi (test manuale)

---

## ⏭️ Prossimo Step

Completata questa fase, procedi con **FASE 7: User Simulation Testing** (`FASE_7_USER_SIMULATION.md`).
