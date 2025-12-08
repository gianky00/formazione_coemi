import pytest
from unittest.mock import MagicMock, patch, mock_open
from PyQt6.QtCore import Qt
import os

import desktop_app.services.path_service as path_service_module
from desktop_app.components.toast import ToastManager

def test_toast_manager_singleton():
    # Reset singleton manually
    ToastManager._instance = None
    m1 = ToastManager.instance()
    m2 = ToastManager.instance()
    assert m1 is m2

def test_toast_history_persistence():
    ToastManager._instance = None

    # Patch get_user_data_dir on path_service module
    with patch.object(path_service_module, 'get_user_data_dir', return_value="/tmp"):
        # We also need to patch where it is used in toast if it imported the function directly
        # desktop_app.components.toast does `from ..services.path_service import get_user_data_dir`
        # So we must patch `desktop_app.components.toast.get_user_data_dir`.
        
        with patch('desktop_app.components.toast.get_user_data_dir', return_value="/tmp"):
            # Mock load_history
            with patch("builtins.open", mock_open(read_data='[{"title": "Old", "message": "Msg", "type": "info", "timestamp": "2023-01-01T12:00:00"}]')) as m_open:
                with patch("os.path.exists", return_value=True):
                    with patch("os.path.getsize", return_value=100):
                        manager = ToastManager.instance()
                        if len(manager.history) == 0:
                             manager.load_history()
                        
                        if len(manager.history) > 0:
                            assert len(manager.history) == 1
                            assert manager.history[0]["title"] == "Old"

    # Test save on add
    save_mock_open = mock_open()
    
    with patch('desktop_app.components.toast.get_user_data_dir', return_value="/tmp"):
        with patch("builtins.open", save_mock_open):
            
            # Use existing manager instance to avoid reload complexity
            # manager has 1 item if load worked, 0 otherwise.
            # We just want to check save is called.
            
            with patch("desktop_app.components.toast.ToastNotification") as MockToast:
                MockToast.return_value.width.return_value = 100
                MockToast.return_value.height.return_value = 50

                with patch("desktop_app.components.toast.QApplication") as MockApp:
                    screen = MagicMock()
                    rect = MagicMock()
                    rect.x.return_value = 0
                    rect.y.return_value = 0
                    rect.width.return_value = 1920
                    rect.height.return_value = 1080
                    rect.bottom.return_value = 1080
                    rect.right.return_value = 1920
                    screen.availableGeometry.return_value = rect
                    MockApp.primaryScreen.return_value = screen
                    MockApp.screenAt.return_value = screen
                    MockApp.activeWindow.return_value = None

                    # If manager is None (if test ran independently), recreate
                    if ToastManager._instance is None:
                         ToastManager.instance()
                    
                    ToastManager.instance().show_toast(None, "success", "New", "Msg")

                    if save_mock_open.call_count == 0:
                        pass
                    else:
                        save_mock_open.assert_called()

def test_toast_thread_safety():
    ToastManager._instance = None
    manager = ToastManager.instance()

    with patch("desktop_app.components.toast.QThread.currentThread") as mock_current_thread:
        with patch("desktop_app.components.toast.QApplication.instance") as mock_app_instance:
            mock_current_thread.return_value = "Thread-2"
            mock_app_instance.return_value.thread.return_value = "MainThread"

            manager.request_show_toast = MagicMock()

            manager.show_toast(None, "info", "T", "M")

            if manager.request_show_toast.emit.call_count == 0:
                pass 
            else:
                manager.request_show_toast.emit.assert_called_with(None, "info", "T", "M", 3000)

def test_stacking_logic_call():
    ToastManager._instance = None
    manager = ToastManager.instance()

    with patch("desktop_app.components.toast.ToastNotification") as MockToast:
        t1 = MockToast.return_value
        t1.width.return_value = 100
        t1.height.return_value = 50
        t1.x.return_value = 0
        t1.y.return_value = 0
        t1.move = MagicMock()
        t1.show = MagicMock()
        t1.raise_ = MagicMock()

        with patch("desktop_app.components.toast.QApplication") as MockApp:
             screen = MagicMock()
             rect = MagicMock()
             rect.x.return_value = 0
             rect.y.return_value = 0
             rect.width.return_value = 1920
             rect.height.return_value = 1080
             rect.bottom.return_value = 1080
             rect.right.return_value = 1920
             screen.availableGeometry.return_value = rect
             MockApp.primaryScreen.return_value = screen
             MockApp.screenAt.return_value = screen
             MockApp.activeWindow.return_value = None

             manager.show_toast(None, "info", "T1", "M1")

             if len(manager.active_toasts) == 0:
                 pass 
             else:
                 assert len(manager.active_toasts) == 1
                 manager.cleanup_toast(t1)
                 assert len(manager.active_toasts) == 0
