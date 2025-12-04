import pytest
from unittest.mock import MagicMock, patch, mock_open
from PyQt6.QtCore import Qt

def test_toast_manager_singleton():
    from desktop_app.components.toast import ToastManager
    ToastManager._instance = None
    m1 = ToastManager.instance()
    m2 = ToastManager.instance()
    assert m1 is m2

def test_toast_history_persistence():
    from desktop_app.components.toast import ToastManager
    ToastManager._instance = None

    # Mock load_history
    with patch("builtins.open", mock_open(read_data='[{"title": "Old", "message": "Msg", "type": "info", "timestamp": "2023-01-01T12:00:00"}]')) as m_open:
        with patch("os.path.exists", return_value=True):
            manager = ToastManager.instance()
            assert len(manager.history) == 1
            assert manager.history[0]["title"] == "Old"

    # Test save on add
    with patch("builtins.open", mock_open()) as m_open:
        with patch("desktop_app.components.toast.ToastNotification") as MockToast:
            # Fix Mock Toast
            MockToast.return_value.width.return_value = 100
            MockToast.return_value.height.return_value = 50

            with patch("desktop_app.components.toast.QApplication") as MockApp:
                # Fix geometry
                screen = MagicMock()
                rect = MagicMock()
                rect.x.return_value = 0
                rect.y.return_value = 0
                rect.width.return_value = 1920
                rect.height.return_value = 1080
                screen.availableGeometry.return_value = rect
                MockApp.primaryScreen.return_value = screen
                MockApp.screenAt.return_value = screen

                manager.show_toast(None, "success", "New", "Msg")

                # Should save
                m_open.assert_called()
                # Check history size
                assert len(manager.history) == 2 # 1 loaded + 1 new

def test_toast_thread_safety():
    from desktop_app.components.toast import ToastManager
    ToastManager._instance = None
    manager = ToastManager.instance()

    # Mock QThread to simulate background thread
    with patch("desktop_app.components.toast.QThread.currentThread") as mock_current_thread:
        with patch("desktop_app.components.toast.QApplication.instance") as mock_app_instance:
            # Setup threads to be different
            mock_current_thread.return_value = "Thread-2"
            mock_app_instance.return_value.thread.return_value = "MainThread"

            # Mock emit
            manager.request_show_toast = MagicMock()

            manager.show_toast(None, "info", "T", "M")

            # Should have emitted signal
            manager.request_show_toast.emit.assert_called_with(None, "info", "T", "M", 3000)

def test_stacking_logic_call():
    from desktop_app.components.toast import ToastManager
    ToastManager._instance = None
    manager = ToastManager.instance()

    with patch("desktop_app.components.toast.ToastNotification") as MockToast:
        # Mock Toast
        t1 = MockToast.return_value
        t1.width.return_value = 100
        t1.height.return_value = 50

        with patch("desktop_app.components.toast.QApplication") as MockApp:
             # Fix geometry
             screen = MagicMock()
             rect = MagicMock()
             rect.x.return_value = 0
             rect.y.return_value = 0
             rect.width.return_value = 1920
             rect.height.return_value = 1080
             screen.availableGeometry.return_value = rect
             MockApp.primaryScreen.return_value = screen
             MockApp.screenAt.return_value = screen

             manager.show_toast(None, "info", "T1", "M1")
             assert len(manager.active_toasts) == 1

             # Simulate cleanup
             manager.cleanup_toast(t1)
             assert len(manager.active_toasts) == 0
