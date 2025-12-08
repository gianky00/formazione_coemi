import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import socket
import logging
import importlib

# Patch settings and logging BEFORE importing launcher
# We need to prevent setup_global_logging from creating real files
sys.modules['logging.handlers'] = MagicMock()

# Patch path_service
mock_path_service = MagicMock()
mock_path_service.get_user_data_dir.return_value = '/tmp/mock_user_data'
sys.modules['desktop_app.services.path_service'] = mock_path_service

# Patch Sentry and PostHog
sys.modules['sentry_sdk'] = MagicMock()
sys.modules['posthog'] = MagicMock()

# Patch PyQt BEFORE import
from tests.desktop_app.mock_qt import DummyQObject, DummySignal
mock_qt = MagicMock()
mock_qt.QApplication = MagicMock()
mock_qt.QCoreApplication = MagicMock()
mock_qt.QWebEngineWidgets = MagicMock()

# Define a proper MockQThread that doesn't crash on init
class MockQThread(DummyQObject):
    started = DummySignal()
    finished = DummySignal()
    def __init__(self, parent=None):
        super().__init__()
    def start(self):
        pass
    def wait(self):
        pass

# DummySignal needs to accept args in constructor to match pyqtSignal signatures like pyqtSignal(str, int)
class FlexibleDummySignal(DummySignal):
    def __init__(self, *args, **kwargs):
        super().__init__()

mock_qt.QThread = MockQThread
mock_qt.pyqtSignal = FlexibleDummySignal

sys.modules['PyQt6.QtWidgets'] = mock_qt
sys.modules['PyQt6.QtCore'] = mock_qt
sys.modules['PyQt6.QtWebEngineWidgets'] = mock_qt
sys.modules['PyQt6.QtGui'] = mock_qt

# Mock DB security
sys.modules['app.core.db_security'] = MagicMock()

# Now import launcher
import launcher

class TestLauncherRobustness(unittest.TestCase):
    
    def setUp(self):
        # Reset environment
        if "API_URL" in os.environ:
            del os.environ["API_URL"]
    
    def test_find_free_port_success(self):
        """Test finding a free port."""
        with patch('socket.socket') as m_socket:
            m_socket.return_value.__enter__.return_value.connect_ex.return_value = 1 # Fail connection = Free
            port = launcher.find_free_port(8000, 8001)
            self.assertEqual(port, 8000)

    def test_find_free_port_all_busy(self):
        """Test handling when all ports are busy."""
        with patch('socket.socket') as m_socket:
            m_socket.return_value.__enter__.return_value.connect_ex.return_value = 0 # Success = Busy
            port = launcher.find_free_port(8000, 8002)
            self.assertIsNone(port)

    def test_verify_license_files_user_dir(self):
        """Test license verification in user directory."""
        mock_path_service.get_license_dir = MagicMock(return_value='/tmp/mock_user_data/Licenza')
        
        with patch('os.path.exists') as m_exists:
            def side_effect(path):
                # Allow pyarmor.rkey and config.dat inside the lic dir
                return '/tmp/mock_user_data/Licenza' in str(path)
            m_exists.side_effect = side_effect
            
            with patch('sys.path', []):
                result = launcher.verify_license_files()
                self.assertTrue(result)
                self.assertTrue(any('Licenza' in p for p in sys.path))

    def test_verify_license_files_none(self):
        """Test license verification fails if no files."""
        with patch('os.path.exists', return_value=False):
            result = launcher.verify_license_files()
            self.assertFalse(result)

    def test_check_license_gatekeeper_valid(self):
        """Test gatekeeper passes with valid license."""
        mock_splash = MagicMock()
        
        with patch('launcher.verify_license_files', return_value=True):
            with patch('importlib.import_module') as mock_import:
                mock_import.return_value = MagicMock()
                launcher.check_license_gatekeeper(mock_splash)
                mock_import.assert_called_with('app.core.config')

    def test_check_license_gatekeeper_invalid_update_success(self):
        """Test gatekeeper triggers update on invalid license."""
        mock_splash = MagicMock()
        
        # 1. Verify files returns False OR import fails
        with patch('launcher.verify_license_files', return_value=False):
            
            # Mock Updater
            mock_updater = MagicMock()
            mock_updater.update_license.return_value = (True, "Updated")
            
            # Use patch.dict on sys.modules to inject mocks for the imports inside the try block
            mock_config_module = MagicMock()
            mock_config_module.settings.LICENSE_REPO_OWNER = "owner"
            mock_config_module.settings.LICENSE_REPO_NAME = "name"
            mock_config_module.settings.LICENSE_GITHUB_TOKEN = "token"

            with patch.dict(sys.modules, {'app.core.config': mock_config_module}):
                with patch('desktop_app.services.license_updater_service.LicenseUpdaterService', return_value=mock_updater):
                    # Patch get_machine_id which is imported inside the function
                    with patch('desktop_app.services.hardware_id_service.get_machine_id', return_value="mock_hwid"):
                        with patch('os.execl') as m_execl:
                             launcher.check_license_gatekeeper(mock_splash)

                             mock_updater.update_license.assert_called()
                             m_execl.assert_called() # Should restart

    def test_check_license_gatekeeper_invalid_update_fail(self):
        """Test gatekeeper exits if update fails."""
        mock_splash = MagicMock()
        
        with patch('launcher.verify_license_files', return_value=False):
            mock_updater = MagicMock()
            mock_updater.update_license.return_value = (False, "Failed")
            
            mock_config_module = MagicMock()
            mock_config_module.settings.LICENSE_REPO_OWNER = "owner"
            mock_config_module.settings.LICENSE_REPO_NAME = "name"
            mock_config_module.settings.LICENSE_GITHUB_TOKEN = "token"

            with patch.dict(sys.modules, {'app.core.config': mock_config_module}):
                with patch('desktop_app.services.license_updater_service.LicenseUpdaterService', return_value=mock_updater):
                    # Patch get_machine_id which is imported inside the function
                    with patch('desktop_app.services.hardware_id_service.get_machine_id', return_value="mock_hwid"):
                        with patch('sys.exit') as m_exit:
                            # Patch the QMessageBox on the launcher module directly
                            with patch('launcher.QMessageBox') as m_msg_cls:
                                launcher.check_license_gatekeeper(mock_splash)

                                m_msg_cls.critical.assert_called()
                                m_exit.assert_called_with(1)

    @patch('launcher.start_server')
    @patch('launcher.check_port', return_value=True)
    @patch('requests.get')
    # Use return_value instead of side_effect for simple return unless iterating
    @patch('desktop_app.services.security_service.is_analysis_tool_running', return_value=(False, "OK"))
    def test_startup_worker_success(self, m_is_analysis, m_get, m_check, m_start):
        """Test successful startup sequence."""
        m_get.return_value.status_code = 200
        
        worker = launcher.StartupWorker(8000)
        
        # Mock signals
        worker.progress_update = MagicMock()
        worker.startup_complete = MagicMock()
        worker.error_occurred = MagicMock()

        # Patch verify_critical_components since it runs inside run()
        with patch('desktop_app.services.integrity_service.verify_critical_components', return_value=(True, "OK")):
             # Patch check_system_clock
             with patch('desktop_app.services.time_service.check_system_clock', return_value=(True, "OK")):
                # Ensure is_analysis_tool_running is returning (False, "OK") via the decorator logic
                # The decorator argument return_value might not be enough if it's called multiple times?
                # No, standard MagicMock return_value is fine.
                
                worker.run()
        
        # Assert start called
        m_start.assert_called()
        worker.startup_complete.emit.assert_called_with(True, "OK")

    @patch('launcher.start_server')
    @patch('launcher.check_port', return_value=True)
    @patch('requests.get')
    def test_startup_worker_health_fail(self, m_get, m_check, m_start):
        """Test startup fails if health check fails."""
        m_get.return_value.status_code = 500
        m_get.return_value.json.return_value = {'detail': 'Internal Server Error'}
        
        # Patch time service and security service components
        with patch('desktop_app.services.time_service.check_system_clock', return_value=(True, None)):
            with patch('desktop_app.services.integrity_service.verify_critical_components', return_value=(True, "OK")):
                with patch('desktop_app.services.security_service.is_analysis_tool_running', return_value=(False, "OK")):
                    worker = launcher.StartupWorker(8000)
                    worker.progress_update = MagicMock()
                    worker.error_occurred = MagicMock()
                    worker.error_occurred.emit = MagicMock()

                    worker.run()

                    worker.error_occurred.emit.assert_called()
                    args = worker.error_occurred.emit.call_args[0][0]
                    self.assertIn("Server Error", args)

    @patch('launcher.start_server')
    @patch('launcher.check_port', return_value=False)
    def test_startup_worker_timeout(self, m_check, m_start):
        """Test startup fails on timeout."""
        worker = launcher.StartupWorker(8000)
        worker.error_occurred = MagicMock()
        worker.error_occurred.emit = MagicMock()
        
        with patch('time.sleep'): 
            with patch('time.time', side_effect=[100, 100, 105, 130, 130, 130]):
                 with patch('desktop_app.services.time_service.check_system_clock', return_value=(True, None)):
                    with patch('desktop_app.services.integrity_service.verify_critical_components', return_value=(True, "OK")):
                        with patch('desktop_app.services.security_service.is_analysis_tool_running', return_value=(False, "OK")):
                             worker.run()
                 
        worker.error_occurred.emit.assert_called()
        args = worker.error_occurred.emit.call_args[0]
        if args and args[0]:
             self.assertIn("Timeout", args[0])
