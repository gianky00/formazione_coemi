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

        with patch("desktop_app.views.login_view.LoginWorker") as MockLoginWorker:
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
