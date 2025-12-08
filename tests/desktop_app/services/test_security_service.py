import os
import sys
import pytest
from unittest.mock import patch, MagicMock
import desktop_app.services.security_service as security_service_module
from desktop_app.services.security_service import is_virtual_environment, is_analysis_tool_running, is_debugger_active

class TestSecurityService:

    def test_is_virtual_environment_detects_process(self):
        # Patch on the module object directly
        with patch.object(security_service_module, '_get_running_processes_wmi', return_value=["system", "svchost.exe", "vmtoolsd.exe"]):
            with patch.object(security_service_module.os, 'name', 'nt'):
                is_vm, msg = is_virtual_environment()
                assert is_vm is True
                assert "vmtoolsd.exe" in msg

    def test_is_virtual_environment_detects_file(self):
        with patch.object(security_service_module, '_get_running_processes_wmi', return_value=["explorer.exe"]):
            def side_effect(path):
                return "vboxguest.sys" in str(path).lower()

            with patch.object(security_service_module.os, 'name', 'nt'):
                with patch.object(security_service_module.os.path, 'exists', side_effect=side_effect):
                    is_vm, msg = is_virtual_environment()
                    assert is_vm is True
                    assert "Driver rilevati" in msg

    def test_is_virtual_environment_clean(self):
        with patch.object(security_service_module, '_get_running_processes_wmi', return_value=["chrome.exe", "notepad.exe"]):
            with patch.object(security_service_module.os, 'name', 'nt'):
                with patch.object(security_service_module.os.path, 'exists', return_value=False):
                    is_vm, msg = is_virtual_environment()
                    assert is_vm is False
                    assert msg == ""

    def test_is_analysis_tool_running_detects_wireshark(self):
        with patch.object(security_service_module, '_get_running_processes_wmi', return_value=["wireshark.exe", "chrome.exe"]):
            with patch.object(security_service_module.os, 'name', 'nt'):
                is_tool, msg = is_analysis_tool_running()
                assert is_tool is True
                assert "wireshark.exe" in msg

    @patch('sys.gettrace')
    def test_is_debugger_active_detected(self, mock_gettrace):
        mock_gettrace.return_value = lambda x, y, z: None 
        is_dbg, msg = is_debugger_active()
        assert is_dbg is True
        assert "Debugger rilevato" in msg

    @patch('sys.gettrace')
    def test_is_debugger_active_clean(self, mock_gettrace):
        mock_gettrace.return_value = None
        is_dbg, msg = is_debugger_active()
        assert is_dbg is False
