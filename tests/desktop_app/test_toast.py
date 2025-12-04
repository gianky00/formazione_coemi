import pytest
from unittest.mock import MagicMock, patch

def test_toast_manager_singleton():
    from desktop_app.components.toast import ToastManager
    m1 = ToastManager.instance()
    m2 = ToastManager.instance()
    assert m1 is m2

def test_show_toast():
    # Mock QPoint and parent
    parent = MagicMock()
    parent.mapToGlobal.return_value = MagicMock()
    parent.mapToGlobal.return_value.x.return_value = 0
    parent.mapToGlobal.return_value.y.return_value = 0
    parent.width.return_value = 800
    parent.height.return_value = 600

    # Patch ToastNotification to avoid QWidget/Qt logic and verify manager interaction
    with patch("desktop_app.components.toast.ToastNotification") as MockToast:
        toast_instance = MockToast.return_value
        toast_instance.width.return_value = 200
        toast_instance.height.return_value = 50

        from desktop_app.components.toast import ToastManager

        # Reset manager
        ToastManager._instance = None
        manager = ToastManager.instance()

        manager.show_toast(parent, "success", "Title", "Message")

        assert len(manager.active_toasts) == 1
        assert manager.active_toasts[0] == toast_instance

        toast_instance.show_toast.assert_called()
        toast_instance.move.assert_called()

        # Simulate close
        # We need to trigger the closed signal.
        # Since signals are mocked (DummySignal), we can try emitting it?
        # But we patched the class, so toast_instance is a MagicMock.
        # MagicMock doesn't have real signals unless we config it.

        # Manually call cleanup
        # manager.active_toasts.remove(toast_instance)
        # assert len(manager.active_toasts) == 0
