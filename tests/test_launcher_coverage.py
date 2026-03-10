import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock modules that might not exist in test env or cause issues
sys.modules["desktop_app.main"] = MagicMock()
sys.modules["app.main"] = MagicMock()
sys.modules["uvicorn"] = MagicMock()
sys.modules["PySide6.QtWidgets"] = MagicMock()

import launcher


class TestLauncherCoverage(unittest.TestCase):
    def test_is_port_in_use(self):
        with patch("socket.socket") as mock_sock_cls:
            mock_sock = mock_sock_cls.return_value
            mock_sock.__enter__.return_value = mock_sock
            mock_sock.connect_ex.return_value = 0
            self.assertTrue(launcher.is_port_in_use(8000))

        with patch("socket.socket") as mock_sock_cls:
            mock_sock = mock_sock_cls.return_value
            mock_sock.__enter__.return_value = mock_sock
            mock_sock.connect_ex.return_value = 111
            self.assertFalse(launcher.is_port_in_use(8000))

    @patch("launcher.is_port_in_use", side_effect=[False, True])
    @patch("threading.Thread")
    @patch("time.sleep")
    def test_main_flow(
        self,
        mock_sleep,
        mock_thread,
        mock_port,
    ):
        with patch("sys.exit") as mock_exit:
            with patch("PySide6.QtWidgets.QApplication"):
                with patch("desktop_app.main.ApplicationController") as mock_controller:
                    launcher.main()

                    # Verify server thread was started
                    mock_thread.assert_called_once()
                    _args, kwargs = mock_thread.call_args
                    self.assertEqual(kwargs.get("target"), launcher.start_server)

                    # Verify controller was started
                    mock_controller.return_value.start.assert_called_once()
                    mock_exit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
