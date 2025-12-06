import sys
import os
import pytest
from unittest.mock import MagicMock, patch, ANY

# --- 1. SETUP MOCKS GLOBALI ---
# Importante: Mockiamo i moduli grafici PRIMA di importare qualsiasi altra cosa
from tests.desktop_app import mock_qt
sys.modules["PyQt6"] = mock_qt.mock_modules["PyQt6"]
sys.modules["PyQt6.QtWidgets"] = mock_qt.mock_modules["PyQt6.QtWidgets"]
sys.modules["PyQt6.QtCore"] = mock_qt.mock_modules["PyQt6.QtCore"]
sys.modules["PyQt6.QtGui"] = mock_qt.mock_modules["PyQt6.QtGui"]
sys.modules["PyQt6.QtWebEngineWidgets"] = mock_qt.mock_modules["PyQt6.QtWebEngineWidgets"]

# Mock Uvicorn
sys.modules["uvicorn"] = MagicMock()

# --- 2. IMPORT SICURO DEL MODULO REALE ---
# Tentiamo di rimuovere launcher se è un Mock residuo da altri test
if "launcher" in sys.modules and isinstance(sys.modules["launcher"], MagicMock):
    del sys.modules["launcher"]

try:
    # Caso 1: launcher.py è nella root o nel path diretto
    import launcher
except ImportError:
    try:
        # Caso 2: launcher.py è dentro desktop_app
        from desktop_app import launcher
        # Lo registriamo anche come 'launcher' globale per coerenza
        sys.modules["launcher"] = launcher
    except ImportError:
        # Caso estremo: creiamo un mock se il file manca davvero fisicamente, 
        # ma questo farà fallire i test logici.
        print("CRITICAL: Could not import real launcher module.")
        launcher = MagicMock()

# --- 3. TEST CLASS (PYTEST STYLE) ---
# Rimuoviamo unittest.TestCase per supportare fixture come tmp_path
class TestLauncher:
    
    @patch("launcher.find_free_port", return_value=8000)
    @patch("launcher.QApplication")
    @patch("desktop_app.views.splash_screen.CustomSplashScreen")
    @patch("launcher.check_license_gatekeeper")
    @patch("launcher.StartupWorker")
    @patch("sys.exit")
    def test_main_execution(self, mock_exit, mock_worker_cls, mock_gatekeeper, mock_splash_cls, mock_qapp, mock_find_port):
        """Test main() executes the startup sequence."""
        mock_splash = mock_splash_cls.return_value
        mock_worker = mock_worker_cls.return_value
        mock_qapp.instance.return_value = None
        
        launcher.main()
        
        mock_find_port.assert_called()
        mock_qapp.assert_called()
        mock_splash.show.assert_called()
        mock_gatekeeper.assert_called_with(mock_splash)
        mock_worker.start.assert_called()
        mock_qapp.return_value.exec.assert_called()

    def test_verify_license_files(self):
        """Test verify_license_files logic without side effects."""
        # Test successo
        with patch("desktop_app.services.path_service.get_license_dir", return_value="/mock/lic"):
            with patch("os.path.exists", return_value=True):
                with patch("sys.path", ["/existing/path"]):
                    result = launcher.verify_license_files()
                    assert result is True
                    assert "/mock/lic" in sys.path

        # Test fallimento
        with patch("desktop_app.services.path_service.get_license_dir", return_value="/mock/lic"):
            with patch("desktop_app.services.path_service.get_app_install_dir", return_value="/mock/install"):
                with patch("os.path.exists", return_value=False):
                    result = launcher.verify_license_files()
                    assert result is False

    @patch("launcher.verify_license_files", return_value=True)
    def test_check_license_gatekeeper_valid(self, mock_verify):
        """Test gatekeeper passes if files exist and import works."""
        mock_splash = MagicMock()
        
        # Mockiamo il modulo config per evitare errori di import reali
        with patch.dict(sys.modules, {"app.core.config": MagicMock()}):
            launcher.check_license_gatekeeper(mock_splash)
            
        mock_splash.update_status.assert_called()

    @patch("launcher.verify_license_files", return_value=False)
    @patch("sys.exit")
    @patch("PyQt6.QtWidgets.QMessageBox.critical")
    def test_check_license_gatekeeper_invalid(self, mock_msg, mock_exit, mock_verify):
        """Test gatekeeper enters recovery mode if license invalid."""
        mock_splash = MagicMock()
        
        # Mockiamo il servizio di update
        with patch("desktop_app.services.license_updater_service.LicenseUpdaterService") as MockUpdater:
            instance = MockUpdater.return_value
            instance.update_license.return_value = (False, "Failed")
            
            with patch("desktop_app.services.hardware_id_service.get_machine_id", return_value="HWID"):
                launcher.check_license_gatekeeper(mock_splash)
        
        mock_exit.assert_called_with(1)

    @patch("socket.socket")
    def test_find_free_port(self, mock_socket_cls):
        """Test finding a free port."""
        mock_socket = mock_socket_cls.return_value
        mock_socket.__enter__.return_value = mock_socket
        mock_socket.connect_ex.side_effect = [0, 1] 
        
        # Chiamiamo la funzione reale
        port = launcher.find_free_port(8000, 8001)
        assert port == 8001

    @patch("requests.get")
    def test_startup_worker(self, mock_get):
        worker = launcher.StartupWorker(8000)
        # Mock segnali Qt
        worker.progress_update = MagicMock()
        worker.startup_complete = MagicMock()
        worker.error_occurred = MagicMock()
        
        with patch("launcher.check_port", return_value=True):
            # Mockiamo i servizi importati internamente
            with patch.dict(sys.modules, {
                "desktop_app.services.security_service": MagicMock(),
                "desktop_app.services.integrity_service": MagicMock(verify_critical_components=lambda: (True, "OK")),
                "desktop_app.services.time_service": MagicMock(check_system_clock=lambda: (True, "OK"))
            }):
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {}
                mock_get.return_value = mock_response
                
                worker.run()
            
        worker.startup_complete.emit.assert_called_with(True, "OK")

    def test_check_port(self):
        """Test check_port logic."""
        with patch("socket.socket") as mock_socket_cls:
            mock_socket = mock_socket_cls.return_value
            
            # Caso 1: Porta aperta (return 0) -> check_port ritorna True
            mock_socket.connect_ex.return_value = 0 
            assert launcher.check_port("127.0.0.1", 8000) is True
            
            # Caso 2: Porta chiusa (return != 0) -> check_port ritorna False
            mock_socket.connect_ex.return_value = 1 
            assert launcher.check_port("127.0.0.1", 8000) is False

    @patch("sqlalchemy.create_engine")
    @patch("app.db.models.Base")
    @patch("app.db.seeding.seed_database")
    @patch("app.core.config.settings")
    def test_initialize_new_database(self, mock_settings, mock_seed, mock_base, mock_create, tmp_path):
        """Test database initialization logic using pytest tmp_path fixture."""
        db_path = tmp_path / "test.db"
        
        launcher.initialize_new_database(db_path)

        assert db_path.exists()
        mock_base.metadata.create_all.assert_called_once()
        mock_seed.assert_called_once()
        mock_settings.save_mutable_settings.assert_called_once_with({"DATABASE_PATH": str(db_path)})