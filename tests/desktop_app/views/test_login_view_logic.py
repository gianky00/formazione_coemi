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

        with patch("desktop_app.views.login_view.Worker") as MockWorker:
            mock_worker_instance = MockWorker.return_value
            mock_worker_instance.signals = MagicMock()

            login_view.handle_login()

            MockWorker.assert_called_with(login_view.api_client.login, username="user", password="pass")
            login_view.threadpool.start.assert_called_with(mock_worker_instance)

            success_callback = mock_worker_instance.signals.result.connect.call_args_list[0][0][0]
            response_data = {"username": "user", "access_token": "token"}
            login_view.api_client.user_info = response_data

            mock_signal = MagicMock()
            login_view.login_success.connect(mock_signal)

            success_callback(response_data)
            login_view.api_client.set_token.assert_called_with(response_data)

            # mock_signal is the slot. It is called directly.
            mock_signal.assert_called_with(response_data)

    def test_handle_login_failure(self, login_view):
        login_view.username_input.text.return_value = "user"
        login_view.password_input.text.return_value = "wrong"

        with patch("desktop_app.views.login_view.Worker") as MockWorker, \
             patch("desktop_app.views.login_view.CustomMessageDialog") as MockDialog:

            mock_worker_instance = MockWorker.return_value
            mock_worker_instance.signals = MagicMock()

            login_view.handle_login()

            error_callback = mock_worker_instance.signals.error.connect.call_args_list[0][0][0]
            error_tuple = (Exception, Exception("Fail"), None)

            error_callback(error_tuple)
            MockDialog.show_error.assert_called()

    def test_handle_login_empty(self, login_view):
        login_view.username_input.text.return_value = ""
        login_view.password_input.text.return_value = ""

        with patch("desktop_app.views.login_view.CustomMessageDialog") as MockDialog:
            login_view.handle_login()
            MockDialog.show_warning.assert_called()
            login_view.api_client.login.assert_not_called()
