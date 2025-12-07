import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from desktop_app.services.security_service import is_virtual_environment, is_analysis_tool_running, is_debugger_active

class TestSecurityService:

    @patch('desktop_app.services.security_service.os.name', 'nt')
    @patch('desktop_app.services.security_service._get_running_processes_wmi')
    def test_is_virtual_environment_detects_process(self, mock_processes):
        # Simulate VM process running
        mock_processes.return_value = ["system", "svchost.exe", "vmtoolsd.exe"]

        is_vm, msg = is_virtual_environment()

        # Verify
        assert is_vm is True
        assert "vmtoolsd.exe" in msg

    @patch('desktop_app.services.security_service.os.name', 'nt')
    @patch('desktop_app.services.security_service._get_running_processes_wmi')
    @patch('desktop_app.services.security_service.os.path.exists')
    def test_is_virtual_environment_detects_file(self, mock_exists, mock_processes):
        # Processes clean
        mock_processes.return_value = ["explorer.exe"]

        # Simulate VM driver file exists
        def side_effect(path):
            return path == r"C:\Windows\System32\drivers\vboxguest.sys"
        mock_exists.side_effect = side_effect

        is_vm, msg = is_virtual_environment()
        assert is_vm is True
        assert "Driver rilevati" in msg

    @patch('desktop_app.services.security_service.os.name', 'nt')
    @patch('desktop_app.services.security_service._get_running_processes_wmi')
    @patch('desktop_app.services.security_service.os.path.exists')
    def test_is_virtual_environment_clean(self, mock_exists, mock_processes):
        mock_processes.return_value = ["chrome.exe", "notepad.exe"]
        mock_exists.return_value = False

        is_vm, msg = is_virtual_environment()
        assert is_vm is False
        assert msg == ""

    @patch('desktop_app.services.security_service._get_running_processes_wmi')
    def test_is_analysis_tool_running_detects_wireshark(self, mock_processes):
        mock_processes.return_value = ["wireshark.exe", "chrome.exe"]

        is_tool, msg = is_analysis_tool_running()
        assert is_tool is True
        assert "wireshark.exe" in msg

    @patch('sys.gettrace')
    def test_is_debugger_active_detected(self, mock_gettrace):
        mock_gettrace.return_value = lambda x, y, z: None # Not None implies debugger

        is_dbg, msg = is_debugger_active()
        assert is_dbg is True
        assert "Debugger rilevato" in msg

    @patch('sys.gettrace')
    def test_is_debugger_active_clean(self, mock_gettrace):
        mock_gettrace.return_value = None

        is_dbg, msg = is_debugger_active()
        assert is_dbg is False
