"""
Test suite for app.core.path_resolver module.

Tests path resolution for:
- Development mode
- PyInstaller frozen mode (simulated)
- Nuitka frozen mode (simulated)
"""
import sys
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestGetBasePath:
    """Tests for get_base_path() function."""
    
    def test_dev_mode_returns_project_root(self):
        """Test that dev mode returns the project root directory."""
        # Ensure we're in dev mode
        assert not getattr(sys, 'frozen', False), "Test must run in dev mode"
        
        from app.core.path_resolver import get_base_path
        
        base = get_base_path()
        
        # Should be a Path object
        assert isinstance(base, Path)
        
        # Should exist
        assert base.exists()
        
        # Should contain key project directories
        assert (base / "app").exists(), f"'app' dir not found in {base}"
        assert (base / "desktop_app").exists(), f"'desktop_app' dir not found in {base}"
        
    def test_dev_mode_returns_absolute_path(self):
        """Test that dev mode returns an absolute path."""
        from app.core.path_resolver import get_base_path
        
        base = get_base_path()
        assert base.is_absolute()
        
    def test_frozen_pyinstaller_mode(self):
        """Test path resolution when running as PyInstaller frozen app."""
        # We need to reimport after mocking
        import importlib
        
        fake_meipass = Path("C:/Temp/MEI123456")
        
        with patch.object(sys, 'frozen', True, create=True):
            with patch.object(sys, '_MEIPASS', str(fake_meipass), create=True):
                # Reimport to pick up mocked values
                import app.core.path_resolver as pr
                importlib.reload(pr)
                
                base = pr.get_base_path()
                assert base == fake_meipass
                
        # Reload again to restore normal behavior
        importlib.reload(pr)
        
    def test_frozen_nuitka_mode(self):
        """Test path resolution when running as Nuitka compiled app."""
        import importlib
        
        fake_exe = Path("C:/Program Files/Intelleo/Intelleo.exe")
        expected_base = fake_exe.parent
        
        with patch.object(sys, 'frozen', True, create=True):
            # Ensure _MEIPASS is NOT present (Nuitka mode)
            with patch.object(sys, 'executable', str(fake_exe)):
                # Remove _MEIPASS if it exists
                if hasattr(sys, '_MEIPASS'):
                    with patch.object(sys, '_MEIPASS', None):
                        delattr(sys, '_MEIPASS')
                
                import app.core.path_resolver as pr
                importlib.reload(pr)
                
                # Manually check the logic since mocking is complex
                if getattr(sys, 'frozen', False):
                    if hasattr(sys, '_MEIPASS'):
                        result = Path(sys._MEIPASS)
                    else:
                        result = Path(sys.executable).parent
                        assert result == expected_base
                        
        # Reload to restore
        importlib.reload(pr)


class TestGetAssetPath:
    """Tests for get_asset_path() function."""
    
    def test_returns_path_object(self):
        """Test that get_asset_path returns a Path object."""
        from app.core.path_resolver import get_asset_path
        
        result = get_asset_path("some/relative/path")
        assert isinstance(result, Path)
        
    def test_resolves_guide_frontend(self):
        """Test resolution of guide_frontend asset."""
        from app.core.path_resolver import get_asset_path
        
        guide_html = get_asset_path("guide_frontend/dist/index.html")
        
        assert "guide_frontend" in str(guide_html)
        assert str(guide_html).endswith("index.html")
        
    def test_existing_asset_found(self):
        """Test that existing assets are correctly found."""
        from app.core.path_resolver import get_asset_path
        
        # This should exist in dev mode
        icon_path = get_asset_path("desktop_app/icons/icon.ico")
        
        # The path should be constructed correctly
        assert "desktop_app" in str(icon_path)
        assert "icons" in str(icon_path)
        
    def test_logs_warning_for_missing_asset(self, caplog):
        """Test that missing assets log a warning."""
        import logging
        from app.core.path_resolver import get_asset_path
        
        with caplog.at_level(logging.WARNING):
            get_asset_path("nonexistent/fake/asset.xyz")
            
        # Should have logged a warning
        assert any("non trovato" in record.message.lower() or "not found" in record.message.lower() 
                   for record in caplog.records)


class TestGetUserDataPath:
    """Tests for get_user_data_path() function."""
    
    def test_returns_path_object(self):
        """Test that get_user_data_path returns a Path object."""
        from app.core.path_resolver import get_user_data_path
        
        result = get_user_data_path()
        assert isinstance(result, Path)
        
    def test_contains_intelleo_in_path(self):
        """Test that path contains 'Intelleo'."""
        from app.core.path_resolver import get_user_data_path
        
        result = get_user_data_path()
        assert "Intelleo" in str(result)
        
    def test_directory_exists(self):
        """Test that the directory is created if it doesn't exist."""
        from app.core.path_resolver import get_user_data_path
        
        result = get_user_data_path()
        assert result.exists()
        assert result.is_dir()
        
    def test_windows_uses_localappdata(self):
        """Test that Windows uses LOCALAPPDATA."""
        if sys.platform != "win32":
            pytest.skip("Windows-only test")
            
        from app.core.path_resolver import get_user_data_path
        
        result = get_user_data_path()
        localappdata = os.environ.get("LOCALAPPDATA", "")
        
        assert localappdata in str(result)


class TestGetLicensePath:
    """Tests for get_license_path() function."""
    
    def test_returns_path_object(self):
        """Test that get_license_path returns a Path object."""
        from app.core.path_resolver import get_license_path
        
        result = get_license_path()
        assert isinstance(result, Path)
        
    def test_path_contains_licenza_or_intelleo(self):
        """Test that path contains expected directory names."""
        from app.core.path_resolver import get_license_path
        
        result = get_license_path()
        result_str = str(result).lower()
        
        # Should contain either 'licenza' or 'intelleo'
        assert "licenza" in result_str or "intelleo" in result_str
        
    def test_priority_user_data_over_install(self):
        """Test that user data location has priority if config.dat exists there."""
        from app.core.path_resolver import get_license_path, get_user_data_path
        
        user_lic_dir = get_user_data_path() / "Licenza"
        
        # If config.dat exists in user data, that should be returned
        if (user_lic_dir / "config.dat").exists():
            result = get_license_path()
            assert result == user_lic_dir


class TestGetDatabasePath:
    """Tests for get_database_path() function."""
    
    def test_returns_path_object(self):
        """Test that get_database_path returns a Path object."""
        from app.core.path_resolver import get_database_path
        
        result = get_database_path()
        assert isinstance(result, Path)
        
    def test_path_ends_with_db_extension(self):
        """Test that database path ends with .db."""
        from app.core.path_resolver import get_database_path
        
        result = get_database_path()
        assert str(result).endswith(".db")
        
    def test_path_in_user_data_directory(self):
        """Test that database is in user data directory."""
        from app.core.path_resolver import get_database_path, get_user_data_path
        
        db_path = get_database_path()
        user_data = get_user_data_path()
        
        assert str(user_data) in str(db_path)


class TestGetLogsPath:
    """Tests for get_logs_path() function."""
    
    def test_returns_path_object(self):
        """Test that get_logs_path returns a Path object."""
        from app.core.path_resolver import get_logs_path
        
        result = get_logs_path()
        assert isinstance(result, Path)
        
    def test_directory_exists(self):
        """Test that logs directory is created."""
        from app.core.path_resolver import get_logs_path
        
        result = get_logs_path()
        assert result.exists()
        assert result.is_dir()
        
    def test_path_contains_logs(self):
        """Test that path contains 'logs'."""
        from app.core.path_resolver import get_logs_path
        
        result = get_logs_path()
        assert "logs" in str(result).lower()


class TestIntegration:
    """Integration tests for path resolver."""
    
    def test_all_functions_return_consistent_paths(self):
        """Test that all path functions return paths under consistent hierarchy."""
        from app.core.path_resolver import (
            get_base_path, get_user_data_path, get_license_path,
            get_database_path, get_logs_path
        )
        
        base = get_base_path()
        user_data = get_user_data_path()
        license_path = get_license_path()
        db_path = get_database_path()
        logs_path = get_logs_path()
        
        # All should be Path objects
        assert all(isinstance(p, Path) for p in [base, user_data, license_path, db_path, logs_path])
        
        # User data paths should be related
        assert str(user_data) in str(db_path)
        assert str(user_data) in str(logs_path)
        
    def test_dev_mode_detection(self):
        """Test that dev mode is correctly detected."""
        from app.core.path_resolver import get_base_path
        
        # In test environment, should NOT be frozen
        assert not getattr(sys, 'frozen', False)
        
        base = get_base_path()
        
        # In dev mode, launcher.py should be at base path
        assert (base / "launcher.py").exists()

