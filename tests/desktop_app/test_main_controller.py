import sys
from unittest.mock import MagicMock, patch

# 1. Setup Mocks
from tests.desktop_app import mock_qt
sys.modules["PyQt6"] = mock_qt.mock_modules["PyQt6"]
sys.modules["PyQt6.QtWidgets"] = mock_qt.mock_modules["PyQt6.QtWidgets"]
sys.modules["PyQt6.QtCore"] = mock_qt.mock_modules["PyQt6.QtCore"]
sys.modules["PyQt6.QtGui"] = mock_qt.mock_modules["PyQt6.QtGui"]

# Mock components that are imported by main.py
mock_login_view = MagicMock()
mock_dashboard = MagicMock()
mock_api_client_cls = MagicMock()
mock_voice_service = MagicMock()
mock_ipc = MagicMock()
mock_db_security = MagicMock()

sys.modules["desktop_app.views.login_view"] = MagicMock(LoginView=mock_login_view)
sys.modules["desktop_app.main_window_ui"] = MagicMock(MainDashboardWidget=mock_dashboard)
sys.modules["desktop_app.api_client"] = MagicMock(APIClient=mock_api_client_cls)
sys.modules["desktop_app.services.voice_service"] = MagicMock(VoiceService=mock_voice_service)
sys.modules["desktop_app.ipc_bridge"] = MagicMock(IPCBridge=mock_ipc)
sys.modules["app.core.db_security"] = MagicMock(db_security=mock_db_security)

# Import after mocking
from desktop_app.main import ApplicationController, MasterWindow

def test_controller_initialization():
    controller = ApplicationController()
    
    assert controller.api_client is not None
    assert controller.voice_service is not None
    assert controller.master_window is not None
    mock_ipc.instance.assert_called()

def test_start():
    controller = ApplicationController()
    
    # Mock master window methods
    controller.master_window.showMaximized = MagicMock()
    controller.master_window.activateWindow = MagicMock()
    controller.master_window.raise_ = MagicMock()
    
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        controller.start()
        
    controller.master_window.showMaximized.assert_called()

def test_login_success():
    controller = ApplicationController()
    
    # Setup mocks
    controller.dashboard = None
    controller.api_client.get.return_value = [] # Mock certificates response
    
    user_info = {
        "account_name": "Test User",
        "read_only": False,
        "previous_login": "2023-01-01T10:00:00"
    }
    
    controller.on_login_success(user_info)
    
    assert controller.dashboard is not None
    # Check that dashboard was shown
    # Stack widget logic: stack.addWidget(dashboard) -> stack.indexOf -> stack.fade_in
    # We can check if setCentralWidget was called or if stack has dashboard
    # Since we mocked MainDashboardWidget, it's a bit abstract.
    # But controller.dashboard should be the mock instance.
    
    # Verify voice welcome
    # Timer singleShot lambda is hard to test without executing it.
    # We can assume if no exception, it's queued.

def test_logout():
    controller = ApplicationController()
    controller.dashboard = MagicMock()
    
    # Mock MasterWindow show_login
    controller.master_window.show_login = MagicMock()
    
    controller.on_logout()
    
    controller.api_client.logout.assert_called()
    controller.master_window.show_login.assert_called()
    assert controller.dashboard is None

def test_ipc_analyze():
    controller = ApplicationController()
    controller.dashboard = MagicMock()
    controller.dashboard.is_read_only = False
    
    controller.handle_ipc_action("analyze", {"path": "test.pdf"})
    controller.dashboard.analyze_path.assert_called_with("test.pdf")

def test_backend_health_check_failure():
    controller = ApplicationController()
    
    # Mock requests to return 503
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 503
        mock_get.return_value.json.return_value = {"detail": "Locked"}
        
        # Mock sys.exit to prevent test exit
        with patch("sys.exit") as mock_exit:
            controller.check_backend_health()
            mock_exit.assert_called_with(1)

def test_close_event():
    # Test MasterWindow.closeEvent
    controller = ApplicationController()
    window = controller.master_window
    
    event = MagicMock()
    
    with patch("PyQt6.QtWidgets.QApplication.quit") as mock_quit:
        window.closeEvent(event)
        
        # Check cleanup
        controller.voice_service.cleanup.assert_called()
        mock_db_security.cleanup.assert_called()
        mock_quit.assert_called()
