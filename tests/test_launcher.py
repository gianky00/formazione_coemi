import sys
import os
import pytest
from unittest.mock import patch, MagicMock
import launcher

def test_verify_license_files_missing(mocker):
    """Test missing license file."""
    # Mock paths
    mocker.patch("desktop_app.services.path_service.get_license_dir", return_value="/tmp/user_license_dir")
    mocker.patch("desktop_app.services.path_service.get_app_install_dir", return_value="/tmp/install_dir")

    # Mock exists to always return False
    mocker.patch("os.path.exists", return_value=False)

    ok = launcher.verify_license_files()
    assert not ok

def test_verify_license_files_user_dir(mocker):
    """Test license found in user dir."""
    mocker.patch("desktop_app.services.path_service.get_license_dir", return_value="/tmp/user_license_dir")
    mocker.patch("desktop_app.services.path_service.get_app_install_dir", return_value="/tmp/install_dir")

    def side_effect(path):
        if "/tmp/user_license_dir" in path: return True
        return False

    mocker.patch("os.path.exists", side_effect=side_effect)

    ok = launcher.verify_license_files()
    assert ok
    # Verify sys.path modification
    assert "/tmp/user_license_dir" in sys.path

def test_verify_license_files_install_dir(mocker):
    """Test license found in install dir."""
    mocker.patch("desktop_app.services.path_service.get_license_dir", return_value="/tmp/user_license_dir")
    mocker.patch("desktop_app.services.path_service.get_app_install_dir", return_value="/tmp/install_dir")

    def side_effect(path):
        if "/tmp/user_license_dir" in path: return False
        if "/tmp/install_dir/Licenza" in path: return True
        return False

    mocker.patch("os.path.exists", side_effect=side_effect)

    ok = launcher.verify_license_files()
    assert ok
    # Verify sys.path modification
    assert "/tmp/install_dir/Licenza" in sys.path

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

def test_initialize_new_database(mocker, tmp_path):
    """Test database initialization logic."""
    db_path = tmp_path / "test.db"

    # Mock SQLAlchemy and Seeding
    mock_create_engine = mocker.patch("sqlalchemy.create_engine")
    mock_base = mocker.patch("app.db.models.Base")
    mock_seed = mocker.patch("app.db.seeding.seed_database")
    mock_settings = mocker.patch("app.core.config.settings")

    # Run initialization
    launcher.initialize_new_database(db_path)

    # Verify Steps
    # 1. Existence
    assert db_path.exists()

    # 2. Schema Creation
    mock_base.metadata.create_all.assert_called_once()

    # 3. Seeding
    mock_seed.assert_called_once()

    # 4. Settings Update
    mock_settings.save_mutable_settings.assert_called_once_with({"DATABASE_PATH": str(db_path)})

    # 5. Verify NO WAL files (Ensure DELETE mode)
    wal_file = db_path.with_suffix(".db-wal")
    shm_file = db_path.with_suffix(".db-shm")
    # Note: If sqlite was mocked, this check is void. But we didn't mock sqlite3.
    # In DELETE mode, they shouldn't exist after connection close.
    assert not wal_file.exists()
    assert not shm_file.exists()
