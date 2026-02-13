import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock modules that might not exist in test env or cause issues
sys.modules["desktop_app.services.security_service"] = MagicMock()
sys.modules["desktop_app.services.integrity_service"] = MagicMock()
sys.modules["desktop_app.services.time_service"] = MagicMock()
sys.modules["app.main"] = MagicMock()
sys.modules["uvicorn"] = MagicMock()
sys.modules["pyttsx3"] = MagicMock()
sys.modules["comtypes"] = MagicMock()
sys.modules["comtypes.client"] = MagicMock()

# Import target
import launcher


class TestLauncherCoverage(unittest.TestCase):
    def test_find_free_port(self):
        with patch("socket.socket") as mock_sock_cls:
            mock_sock = mock_sock_cls.return_value
            mock_sock.__enter__.return_value = mock_sock
            mock_sock.connect_ex.return_value = 111

            port = launcher.find_free_port(8000, 8001)
            self.assertEqual(port, 8000)

    def test_check_port(self):
        with patch("socket.socket") as mock_sock_cls:
            mock_sock = mock_sock_cls.return_value
            mock_sock.connect_ex.return_value = 0
            self.assertTrue(launcher.check_port("127.0.0.1", 80))

        with patch("socket.socket") as mock_sock_cls:
            mock_sock = mock_sock_cls.return_value
            mock_sock.connect_ex.return_value = 111
            self.assertFalse(launcher.check_port("127.0.0.1", 80))

    def test_verify_license_files(self):
        with (
            patch("pathlib.Path.exists") as mock_exists,
            patch("app.core.path_resolver.get_license_path", return_value=Path("/user/lic")),
        ):
            # Case 1: Files exist
            mock_exists.return_value = True
            self.assertTrue(launcher.verify_license_files())

            # Case 2: Files missing
            mock_exists.return_value = False
            self.assertFalse(launcher.verify_license_files())

    @patch("launcher.find_free_port", return_value=8000)
    @patch("launcher.verify_license_files", return_value=True)
    @patch("threading.Thread")
    @patch("launcher.check_port", side_effect=[False, True])
    @patch("desktop_app.main.ApplicationController")
    # Use a lambda to avoid StopIteration when internal libs call time.time()
    @patch("time.time")
    @patch("time.sleep")
    def test_main_flow(
        self,
        mock_sleep,
        mock_time,
        mock_controller,
        mock_check,
        mock_thread,
        mock_verify,
        mock_port,
    ):
        # Configure time.time to return increasing values
        times = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        mock_time.side_effect = lambda: times.pop(0) if times else 100

        # Test the main entry point
        with patch("sys.exit") as mock_exit:
            launcher.main()

            # Verify license was checked
            mock_verify.assert_called_once()

            # Verify server thread was started
            mock_thread.assert_called_once()
            args, kwargs = mock_thread.call_args
            self.assertEqual(kwargs.get("target"), launcher.start_server)

            # Verify controller was started
            mock_controller.return_value.start.assert_called_once()

            # Verify exit was not called
            mock_exit.assert_not_called()

    @patch("launcher.verify_license_files", return_value=False)
    def test_main_license_failure(self, mock_verify):
        with patch("sys.exit", side_effect=SystemExit) as mock_exit:
            with self.assertRaises(SystemExit):
                launcher.main()
            mock_exit.assert_called_with(1)


if __name__ == "__main__":
    unittest.main()
