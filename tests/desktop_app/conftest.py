"""
Conftest per i test desktop_app - CRASH ZERO

Questo file gestisce i fixtures Qt senza dipendere dal backend FastAPI.
pytest-qt fornisce automaticamente qapp e qtbot quando è installato.

IMPORTANT: Some tests use mocked PyQt6 (via mock_qt.py) which pollutes
sys.modules. Tests that need REAL Qt (core/, mixins/) should be run
BEFORE tests that mock Qt, or in a separate pytest invocation:

  pytest tests/desktop_app/core/ tests/desktop_app/mixins/ -v
  pytest tests/desktop_app/ --ignore=tests/desktop_app/core --ignore=tests/desktop_app/mixins -v
"""

import sys
import os
import pytest
from unittest.mock import MagicMock

# --- MOCK EXTERNAL SERVICES (prevent network calls) ---
mock_wmi = MagicMock()
mock_wmi.WMI.return_value = MagicMock()
sys.modules["wmi"] = mock_wmi

# Note: PostHog was removed in FASE 6 (CRASH ZERO), no mock needed

mock_sentry = MagicMock()
mock_sentry.init.return_value = None
mock_sentry.is_initialized.return_value = False
mock_sentry.capture_exception.return_value = None
mock_sentry.capture_message.return_value = None
sys.modules["sentry_sdk"] = mock_sentry
sys.modules["sentry_sdk.integrations"] = MagicMock()
sys.modules["sentry_sdk.integrations.fastapi"] = MagicMock()
sys.modules["sentry_sdk.integrations.starlette"] = MagicMock()

sys.modules["wandb"] = MagicMock()

# --- PATH SETUP ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


# --- CRASH ZERO: Reset singletons between tests ---
@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singletons after each test."""
    yield
    
    # Cleanup after test
    try:
        from desktop_app.core.state_machine import AppStateMachine
        AppStateMachine.reset_instance()
    except ImportError:
        pass
    
    try:
        from desktop_app.core.animation_manager import AnimationManager
        # Reset animation manager state
        am = AnimationManager.instance()
        am._animations.clear()
        am._owner_map.clear()
    except ImportError:
        pass
