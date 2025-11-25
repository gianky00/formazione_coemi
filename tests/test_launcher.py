import sys
import os
import pytest
from unittest.mock import patch, MagicMock
import launcher

def test_verify_license_missing(mocker):
    """Test missing license file."""
    # Mock frozen to True so it checks EXE_DIR
    mocker.patch.object(sys, 'frozen', True, create=True)
    mocker.patch.object(sys, 'executable', '/tmp/fake_exe')
    mocker.patch("os.path.exists", return_value=False)

    # Since the new verify_license imports path_service, we need to mock the functions at their source
    mocker.patch("desktop_app.services.path_service.get_license_dir", return_value="/tmp/user_license_dir")
    mocker.patch("desktop_app.services.path_service.get_app_install_dir", return_value="/tmp/install_dir")

    ok, msg = launcher.verify_license()
    assert not ok
    # The error message was updated, so we update the test assertion
    assert "non trovato" in msg

def test_verify_license_valid_dev_mode(mocker):
    """Test valid license (implicit check) in dev mode."""
    # Mock frozen to False
    mocker.patch.object(sys, 'frozen', False, create=True)

    # Mock existence of rkey
    mocker.patch("os.path.exists", return_value=True)

    # Real import of app.core.config should succeed in dev
    ok, msg = launcher.verify_license()
    assert ok
    assert msg == "OK"

def test_check_port_open(mocker):
    with patch("socket.socket") as mock_sock:
        instance = mock_sock.return_value
        instance.connect_ex.return_value = 0 # 0 means success/open
        assert launcher.check_port("localhost", 8000) is True

def test_check_port_closed(mocker):
    with patch("socket.socket") as mock_sock:
        instance = mock_sock.return_value
        instance.connect_ex.return_value = 111
        assert launcher.check_port("localhost", 8000) is False
