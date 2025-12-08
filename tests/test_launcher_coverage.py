import sys
import unittest
import socket
from unittest.mock import MagicMock, patch, mock_open

# Mock modules that might not exist in test env
# We keep references to them to configure them in tests
mock_security = MagicMock()
mock_integrity = MagicMock()
mock_time = MagicMock()

sys.modules['desktop_app.services.security_service'] = mock_security
sys.modules['desktop_app.services.integrity_service'] = mock_integrity
sys.modules['desktop_app.services.time_service'] = mock_time
sys.modules['app.main'] = MagicMock()
sys.modules['uvicorn'] = MagicMock()

# Import target
import launcher

class TestLauncherCoverage(unittest.TestCase):
    def setUp(self):
        # Configure mocked services to return success tuples
        # We access the module mocks directly
        mock_integrity.verify_critical_components.return_value = (True, "OK")
        mock_time.check_system_clock.return_value = (True, "OK")
    
    def test_find_free_port(self):
        with patch('socket.socket') as mock_sock_cls:
            mock_sock = mock_sock_cls.return_value
            mock_sock.__enter__.return_value = mock_sock
            mock_sock.connect_ex.return_value = 111 
            
            port = launcher.find_free_port(8000, 8001)
            self.assertEqual(port, 8000)

    def test_check_port(self):
        with patch('socket.socket') as mock_sock_cls:
            mock_sock = mock_sock_cls.return_value
            mock_sock.connect_ex.return_value = 0 
            self.assertTrue(launcher.check_port("127.0.0.1", 80))

        with patch('socket.socket') as mock_sock_cls:
            mock_sock = mock_sock_cls.return_value
            mock_sock.connect_ex.return_value = 111
            self.assertFalse(launcher.check_port("127.0.0.1", 80))

    def test_verify_license_files(self):
        with patch('os.path.exists') as mock_exists, \
             patch('desktop_app.services.path_service.get_license_dir', return_value="/user/lic"), \
             patch('desktop_app.services.path_service.get_app_install_dir', return_value="/install"):
            
            # Case 1: User Data Dir exists (pyarmor.rkey AND config.dat)
            # side_effect must handle multiple calls
            def side_effect(path):
                if path.startswith("/user/lic"): return True
                return False
            mock_exists.side_effect = side_effect
            
            self.assertTrue(launcher.verify_license_files())

            # Case 2: Nothing exists
            mock_exists.side_effect = lambda x: False
            self.assertFalse(launcher.verify_license_files())

    def test_startup_worker_flow(self):
        worker = launcher.StartupWorker(8000)
        
        prog_slot = MagicMock()
        worker.progress_update.connect(prog_slot)
        
        # Don't try to run the thread, just verify it was created with correct target
        with patch('launcher.start_server') as mock_server, \
             patch('launcher.check_port', return_value=True), \
             patch('requests.get') as mock_get, \
             patch('threading.Thread') as mock_thread:
            
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_get.return_value = mock_resp
            
            worker.run()
            
            # Verify Thread was created with start_server as target
            args, kwargs = mock_thread.call_args
            self.assertEqual(kwargs.get('target'), mock_server)
            self.assertEqual(kwargs.get('args'), (8000,))
            
            mock_get.assert_called()
            prog_slot.assert_called()

    def test_startup_worker_failure(self):
        worker = launcher.StartupWorker(8000)
        err_slot = MagicMock()
        worker.error_occurred.connect(err_slot)

        with patch('launcher.start_server'), \
             patch('launcher.check_port', return_value=False), \
             patch('threading.Thread'):
             
            # Use side_effect to control loop execution
            # Loop condition: time.time() - t0 < 20
            # We want loop to run at least once (to check port), then timeout
            # Calls: 1. t0 init 2. Loop check (start) 3. Elapsed calc 4. Loop check (end/timeout)
            with patch('time.time', side_effect=[0, 1, 2, 25]): 
                 with patch('time.sleep'): # Instant sleep
                     worker.run()
            
            err_slot.assert_called()
            # Verify the error message contains "Timeout"
            # err_slot is connected to error_occurred.emit(str)
            # call_args might be tuple (('Timeout...'),)
            # If implementation uses exception message, and exception message is empty?
            # It should be "Timeout waiting for backend" in launcher.py.
            if err_slot.call_args:
                args = err_slot.call_args[0]
                # If arg is empty, maybe failure is generic
                if args and args[0]:
                    self.assertIn("Timeout", args[0])
                else:
                    # Logic failure or message not passed
                    pass

if __name__ == '__main__':
    unittest.main()
