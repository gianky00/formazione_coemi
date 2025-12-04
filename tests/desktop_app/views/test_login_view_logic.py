import sys
from unittest.mock import MagicMock, patch
import pytest
from tests.desktop_app.mock_qt import mock_modules

class TestLoginViewLogic:
    @pytest.fixture
    def login_view(self):
        with patch.dict(sys.modules, mock_modules):
            from desktop_app.views.login_view import LoginView

            with patch("desktop_app.services.license_manager.LicenseManager.get_license_data", return_value={}):
                client = MagicMock()
                view = LoginView(client)
                view.username_input = MagicMock()
                view.password_input = MagicMock()
                view.login_btn = MagicMock()
                view.threadpool = MagicMock()
                yield view

    def test_handle_login_success(self, login_view):
        login_view.username_input.text.return_value = "user"
        login_view.password_input.text.return_value = "pass"

        with patch("desktop_app.views.login_view.LoginWorker") as MockLoginWorker, \
             patch("desktop_app.views.login_view.QTimer") as MockTimer: # Patch QTimer

            # Configure QTimer.singleShot to execute the callback immediately
            def side_effect_singleShot(ms, callback):
                callback()
            MockTimer.singleShot.side_effect = side_effect_singleShot

            mock_worker_instance = MockLoginWorker.return_value
            mock_worker_instance.finished_success = MagicMock()
            mock_worker_instance.finished_error = MagicMock()

            login_view.handle_login()

            MockLoginWorker.assert_called_with(login_view.api_client, "user", "pass")
            mock_worker_instance.start.assert_called()

            mock_worker_instance.finished_success.connect.assert_called_with(login_view.on_login_success)
            mock_worker_instance.finished_error.connect.assert_called_with(login_view._on_login_error)

            response_data = {"username": "user", "access_token": "token"}
            login_view.api_client.user_info = response_data

            # Mock the certificates API call for pending count
            login_view.api_client.get.return_value = []

            mock_signal = MagicMock()
            login_view.login_success.connect(mock_signal)

            # Manually call success handler
            login_view.on_login_success(response_data)

            login_view.api_client.set_token.assert_called_with(response_data)

            # Verify get was called
            login_view.api_client.get.assert_called_with("certificati", params={"validated": "false"})

            # mock_signal is the slot. It is called directly.
            # Note: response_data is modified in place inside on_login_success, so we assert against the modified version
            mock_signal.assert_called_with(response_data)

    def test_handle_login_failure(self, login_view):
        login_view.username_input.text.return_value = "user"
        login_view.password_input.text.return_value = "wrong"

        with patch("desktop_app.views.login_view.LoginWorker") as MockLoginWorker, \
             patch("desktop_app.views.login_view.CustomMessageDialog") as MockDialog:

            mock_worker_instance = MockLoginWorker.return_value
            mock_worker_instance.finished_success = MagicMock()
            mock_worker_instance.finished_error = MagicMock()

            login_view.handle_login()

            mock_worker_instance.finished_error.connect.assert_called_with(login_view._on_login_error)

            # Manually call error handler
            error_msg = "Fail"
            login_view._on_login_error(error_msg)

            MockDialog.show_error.assert_called_with(login_view, "Errore di Accesso", error_msg)

    def test_handle_login_empty(self, login_view):
        login_view.username_input.text.return_value = ""
        login_view.password_input.text.return_value = ""

        with patch("desktop_app.views.login_view.CustomMessageDialog") as MockDialog:
            login_view.handle_login()
            MockDialog.show_warning.assert_called()
            login_view.api_client.login.assert_not_called()

    def test_on_login_success_read_only(self, login_view):
        """Test that login success with read_only=True shows a warning with owner info."""
        response_data = {
            "username": "user",
            "access_token": "token",
            "read_only": True,
            "lock_owner": {
                "username": "other_user",
                "full_name": "Other User",
                "hostname": "OTHER-PC",
                "acquired_at": "2023-01-01 12:00:00"
            }
        }

        login_view.api_client.get.return_value = []
        # Crucial: Since api_client is a Mock, set_token won't update user_info.
        # We must manually set the property to the dict we want.
        # However, on_login_success calls set_token first.
        # So we can set a side_effect on set_token to update user_info
        def side_effect_set_token(data):
            login_view.api_client.user_info = data

        login_view.api_client.set_token.side_effect = side_effect_set_token

        with patch("desktop_app.views.login_view.CustomMessageDialog") as MockDialog, \
             patch("desktop_app.views.login_view.QTimer") as MockTimer:

            # Configure QTimer to run callback immediately
            def side_effect_singleShot(ms, callback):
                callback()
            MockTimer.singleShot.side_effect = side_effect_singleShot

            # We need to mock the signal connection
            mock_signal = MagicMock()
            login_view.login_success.connect(mock_signal)

            login_view.on_login_success(response_data)

            # Verify warning dialog was shown
            MockDialog.show_warning.assert_called()
            args = MockDialog.show_warning.call_args
            # args[0] is self (view), args[1] is title, args[2] is message
            assert args[0][1] == "Modalità Sola Lettura"
            assert "Utente: other_user" in args[0][2]
            assert "Host: OTHER-PC" in args[0][2]

            # Verify login success signal was still emitted
            mock_signal.assert_called()
