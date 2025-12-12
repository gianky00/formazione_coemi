"""
Conftest per i test desktop_app - CRASH ZERO

Questo file gestisce i fixtures Qt senza dipendere dal backend FastAPI.
pytest-qt fornisce automaticamente qapp e qtbot quando è installato.
"""

import sys
import os
from unittest.mock import MagicMock

# --- MOCK EXTERNAL SERVICES (prevent network calls) ---
mock_wmi = MagicMock()
mock_wmi.WMI.return_value = MagicMock()
sys.modules["wmi"] = mock_wmi

mock_ph = MagicMock()
mock_ph.capture.return_value = None
mock_ph.flush.return_value = None
sys.modules["posthog"] = mock_ph

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
