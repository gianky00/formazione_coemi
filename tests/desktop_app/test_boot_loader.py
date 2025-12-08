import sys
import unittest
import importlib
from unittest.mock import MagicMock, patch

class TestBootLoader(unittest.TestCase):
    
    def setUp(self):
        # Setup: Creiamo un mock per 'launcher' PRIMA di importare boot_loader
        self.mock_launcher = MagicMock()
        
        # Patchiamo sys.modules per iniettare il nostro mock
        self.module_patcher = patch.dict(sys.modules, {"launcher": self.mock_launcher})
        self.module_patcher.start()
        
        # Importiamo (o ricarichiamo) boot_loader per assicurarci che usi il mock
        import boot_loader
        importlib.reload(boot_loader)
        self.boot_loader = boot_loader

    def tearDown(self):
        self.module_patcher.stop()

    @patch("sys.exit")
    def test_main_success(self, mock_exit):
        """Test successful execution of launcher.main()."""
        # Eseguiamo il main
        self.boot_loader.main()
        
        # Verifiche
        self.mock_launcher.main.assert_called_once()
        mock_exit.assert_not_called()

    @patch("sys.exit")
    @patch("boot_loader.log_crash")
    @patch("boot_loader.show_error")
    def test_main_failure(self, mock_show, mock_log, mock_exit):
        """Test crash handling."""
        # Simuliamo un crash nel launcher
        self.mock_launcher.main.side_effect = Exception("Boom")
        
        self.boot_loader.main()
        
        # Verifiche
        mock_log.assert_called()
        mock_show.assert_called()
        mock_exit.assert_called_with(1)

    def test_show_error_windows(self):
        mock_windll = MagicMock()
        with patch("ctypes.windll", mock_windll, create=True):
            with patch("os.name", "nt"):
                self.boot_loader.show_error("Title", "Msg")
                if hasattr(mock_windll.user32, 'MessageBoxW'):
                    mock_windll.user32.MessageBoxW.assert_called()

    @patch("builtins.print")
    def test_show_error_linux(self, mock_print):
        with patch("os.name", "posix"):
            self.boot_loader.show_error("Title", "Msg")
            mock_print.assert_called()
