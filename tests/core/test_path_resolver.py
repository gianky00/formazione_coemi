import os
import sys
from pathlib import Path
from unittest.mock import patch

from app.core import path_resolver


def test_get_base_path_dev_mode():
    with patch.object(sys, "frozen", False, create=True):
        # In dev mode, it uses __file__
        # path_resolver.py is in app/core/
        # base path is 3 levels up
        base = path_resolver.get_base_path()
        # We expect it to be the project root
        assert base.exists()
        assert (base / "app").exists()


def test_get_base_path_pyinstaller():
    with patch.object(sys, "frozen", True, create=True):
        with patch.object(sys, "_MEIPASS", "/tmp/fake_meipass", create=True):
            base = path_resolver.get_base_path()
            assert base == Path("/tmp/fake_meipass")


def test_get_base_path_nuitka():
    with patch.object(sys, "frozen", True, create=True):
        # Remove _MEIPASS if it exists from other tests
        if hasattr(sys, "_MEIPASS"):
            delattr(sys, "_MEIPASS")

        fake_exe = "/usr/bin/intelleo.exe" if sys.platform == "win32" else "/usr/bin/intelleo"
        with patch.object(sys, "executable", fake_exe):
            base = path_resolver.get_base_path()
            assert base == Path("/usr/bin")


def test_get_user_data_path_windows():
    with patch("sys.platform", "win32"):
        with patch.dict(os.environ, {"LOCALAPPDATA": r"C:\FakeAppData"}):
            # Mock mkdir to avoid creating real folders
            with patch("pathlib.Path.mkdir"):
                path = path_resolver.get_user_data_path()
                assert str(path).startswith(r"C:\FakeAppData")
                assert "Intelleo" in str(path)


def test_get_license_path_priority(tmp_path):
    # Setup: mock user data path and base path
    user_data = tmp_path / "user_data"
    base_path = tmp_path / "base"

    (user_data / "Licenza").mkdir(parents=True)
    (base_path / "Licenza").mkdir(parents=True)

    with patch("app.core.path_resolver.get_user_data_path", return_value=user_data):
        with patch("app.core.path_resolver.get_base_path", return_value=base_path):
            # 1. Neither has config.dat -> returns user_data/Licenza (default)
            res = path_resolver.get_license_path()
            assert res == user_data / "Licenza"

            # 2. Base path has config.dat -> returns base_path/Licenza
            (base_path / "Licenza" / "config.dat").touch()
            res = path_resolver.get_license_path()
            assert res == base_path / "Licenza"

            # 3. User data has config.dat -> returns user_data/Licenza (Priority 1)
            (user_data / "Licenza" / "config.dat").touch()
            res = path_resolver.get_license_path()
            assert res == user_data / "Licenza"


def test_get_asset_path():
    base = Path("/fake/base")
    with patch("app.core.path_resolver.get_base_path", return_value=base):
        asset = path_resolver.get_asset_path("subdir/asset.txt")
        assert asset == base / "subdir" / "asset.txt"
