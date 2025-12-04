import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import Qt

def test_toast_manager_singleton():
    from desktop_app.components.toast import ToastManager
    ToastManager._instance = None
    m1 = ToastManager.instance()
    m2 = ToastManager.instance()
    assert m1 is m2

def test_toast_history():
    from desktop_app.components.toast import ToastManager
    ToastManager._instance = None
    manager = ToastManager.instance()

    assert len(manager.history) == 0

    with patch("desktop_app.components.toast.ToastNotification") as MockToast:
        # Ensure geometry math results in ints
        MockToast.return_value.width.return_value = 200
        MockToast.return_value.height.return_value = 50

        # Mock QApplication to avoid crash in fallback logic if parent is None
        with patch("desktop_app.components.toast.QApplication") as MockApp:
            # Set up mock screen to return valid ints
            screen_mock = MagicMock()
            rect_mock = MagicMock()
            rect_mock.x.return_value = 0
            rect_mock.y.return_value = 0
            rect_mock.width.return_value = 1920
            rect_mock.height.return_value = 1080
            screen_mock.availableGeometry.return_value = rect_mock
            MockApp.primaryScreen.return_value = screen_mock

            manager.show_toast(None, "info", "Title 1", "Msg 1")
            assert len(manager.history) == 1
            assert manager.history[0]["title"] == "Title 1"

            manager.show_toast(None, "error", "Title 2", "Msg 2")
            assert len(manager.history) == 2
            assert manager.history[0]["title"] == "Title 2" # Newest first

def test_toast_positioning_fallback():
    # Test fallback to screen when parent is None or minimized
    from desktop_app.components.toast import ToastManager

    ToastManager._instance = None
    manager = ToastManager.instance()

    parent = MagicMock()
    parent.isVisible.return_value = False # Hidden

    with patch("desktop_app.components.toast.ToastNotification") as MockToast:
        toast_instance = MockToast.return_value
        toast_instance.width.return_value = 200
        toast_instance.height.return_value = 50

        with patch("desktop_app.components.toast.QApplication") as MockApp:
            # Mock screen geometry explicitly
            screen_mock = MagicMock()
            rect_mock = MagicMock()
            rect_mock.x.return_value = 0
            rect_mock.y.return_value = 0
            rect_mock.width.return_value = 1920
            rect_mock.height.return_value = 1080

            screen_mock.availableGeometry.return_value = rect_mock
            MockApp.primaryScreen.return_value = screen_mock

            manager.show_toast(parent, "info", "T", "M")

            assert len(manager.active_toasts) == 1
            toast = manager.active_toasts[0]
            toast.move.assert_called()

            # Should have moved to bottom right: 1920 - 200 - 20, 1080 - 50 - 20
            args = toast.move.call_args[0]
            expected_x = 1920 - 200 - 20
            expected_y = 1080 - 50 - 20

            assert args[0] == expected_x
            assert args[1] == expected_y

def test_toast_positioning_valid_parent():
    from desktop_app.components.toast import ToastManager

    ToastManager._instance = None
    manager = ToastManager.instance()

    parent = MagicMock()
    parent.isVisible.return_value = True
    # Qt.WindowState.WindowNoState should now be available via our updated mock
    parent.windowState.return_value = Qt.WindowState.WindowNoState
    parent.isWindow.return_value = True

    # Mock geometry() return
    rect_mock = MagicMock()
    rect_mock.x.return_value = 100
    rect_mock.y.return_value = 100
    rect_mock.width.return_value = 800
    rect_mock.height.return_value = 600
    parent.geometry.return_value = rect_mock

    with patch("desktop_app.components.toast.ToastNotification") as MockToast:
        toast_instance = MockToast.return_value
        toast_instance.width.return_value = 200
        toast_instance.height.return_value = 50

        manager.show_toast(parent, "info", "T", "M")

        toast = manager.active_toasts[0]
        toast.move.assert_called()

        # Should have moved to bottom right of parent
        # x = 100 + 800 - 200 - 20 = 680
        # y = 100 + 600 - 50 - 20 = 630
        args = toast.move.call_args[0]
        assert args[0] == 680
        assert args[1] == 630
