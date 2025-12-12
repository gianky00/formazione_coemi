"""
Fixtures per test di simulazione utente.

CRASH ZERO - FASE 7: User Simulation Testing
"""

import pytest
from unittest.mock import MagicMock, patch
import sys


@pytest.fixture(scope="module")
def qapp_module(qapp):
    """QApplication per modulo di test (riusa quella di pytest-qt)."""
    return qapp


@pytest.fixture
def mock_backend():
    """Mock del backend FastAPI per test isolati."""
    mock_client = MagicMock()
    mock_client.login.return_value = {
        "access_token": "test_token",
        "user_info": {"id": 1, "username": "admin", "is_admin": True}
    }
    mock_client.get_certificati.return_value = []
    mock_client.get_dipendenti.return_value = []
    mock_client.get_scadenze.return_value = []
    mock_client.user_info = {"id": 1, "username": "admin", "is_admin": True}
    mock_client.logout.return_value = None
    
    return mock_client


@pytest.fixture
def mock_license():
    """Mock del license checker."""
    mock_license_data = {
        "Cliente": "Test Company",
        "Scadenza Licenza": "31/12/2030",
        "Hardware ID": "TEST-HW-ID",
        "is_valid": True,
    }
    return mock_license_data


@pytest.fixture
def app_controller_factory(qapp, mock_backend, mock_license):
    """
    Factory per creare ApplicationController con mock.
    
    Uso:
        controller = app_controller_factory()
        # ... test ...
        controller.cleanup()  # Importante per cleanup
    """
    controllers = []
    
    def _create():
        with patch('desktop_app.api_client.APIClient', return_value=mock_backend), \
             patch('desktop_app.views.login_view.LicenseManager') as MockLM, \
             patch('desktop_app.main.VoiceService') as MockVoice, \
             patch('desktop_app.main.IPCBridge') as MockIPC, \
             patch('desktop_app.main.FloatingChatWidget') as MockChat:
            
            # Configure license mock
            MockLM.return_value.get_license_data.return_value = mock_license
            MockLM.return_value.is_license_valid.return_value = True
            
            # Configure voice mock
            MockVoice.return_value.speak.return_value = None
            MockVoice.return_value.stop.return_value = None
            
            from desktop_app.main import ApplicationController
            
            controller = ApplicationController()
            controllers.append(controller)
            return controller
    
    yield _create
    
    # Cleanup all created controllers
    for ctrl in controllers:
        try:
            if hasattr(ctrl, 'cleanup'):
                ctrl.cleanup()
            if hasattr(ctrl, 'master_window') and ctrl.master_window:
                ctrl.master_window.close()
        except Exception:
            pass


@pytest.fixture
def app_controller(app_controller_factory):
    """Controller applicazione singolo per test."""
    return app_controller_factory()
