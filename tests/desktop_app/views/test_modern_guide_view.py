"""
Tests for ModernGuideView - React SPA loading.

Updated for Nuitka migration: tests now use sys.frozen pattern
instead of sys._MEIPASS directly, matching the path_resolver approach.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from tests.desktop_app.mock_qt import DummyQWebEngineView


class TestModernGuideView:

    def test_init_dev_mode(self):
        """Test initialization in development mode (not frozen)."""
        # Ensure we're in dev mode
        assert not getattr(sys, 'frozen', False), "Test should run in dev mode"

        from desktop_app.views import modern_guide_view
        view = modern_guide_view.ModernGuideView()

        # Verify internal state of our dummy webview
        assert isinstance(view.webview, DummyQWebEngineView)

        # In dev mode with guide built, should load URL
        # Without guide, should show fallback HTML
        if view.webview.html:
            assert "Guida non disponibile" in view.webview.html
        else:
            assert view.webview.url is not None

    @patch('app.core.path_resolver.get_asset_path')
    def test_init_frozen_mode_nuitka(self, mock_get_asset_path):
        """Test initialization in frozen mode (Nuitka - no _MEIPASS)."""
        from pathlib import Path
        
        # Mock the asset path to return a fake path that "exists"
        fake_path = Path('/opt/Intelleo/guide/index.html')
        mock_path_obj = MagicMock(spec=Path)
        mock_path_obj.exists.return_value = True
        mock_path_obj.__str__ = lambda self: str(fake_path)
        mock_get_asset_path.return_value = mock_path_obj

        mock_qtcore = sys.modules['PyQt6.QtCore']
        mock_qtcore.QUrl.fromLocalFile.side_effect = lambda path: f"file://{path}"

        with patch.object(sys, 'frozen', True, create=True):
            # Ensure _MEIPASS is NOT present (Nuitka mode)
            import desktop_app.views.modern_guide_view as mgv
            import importlib
            importlib.reload(mgv)
            
            view = mgv.ModernGuideView()

            assert view.webview.url is not None
            # In frozen mode, should use 'guide' path (not guide_frontend/dist)
            mock_get_asset_path.assert_called()

    @patch('app.core.path_resolver.get_asset_path')
    def test_init_frozen_mode_pyinstaller(self, mock_get_asset_path):
        """Test initialization in frozen mode (PyInstaller - has _MEIPASS)."""
        from pathlib import Path
        
        # Mock the asset path
        fake_path = Path('C:/Temp/MEI123/guide/index.html')
        mock_path_obj = MagicMock(spec=Path)
        mock_path_obj.exists.return_value = True
        mock_path_obj.__str__ = lambda self: str(fake_path)
        mock_get_asset_path.return_value = mock_path_obj

        mock_qtcore = sys.modules['PyQt6.QtCore']
        mock_qtcore.QUrl.fromLocalFile.side_effect = lambda path: f"file://{path}"

        with patch.object(sys, 'frozen', True, create=True):
            with patch.object(sys, '_MEIPASS', 'C:/Temp/MEI123', create=True):
                import desktop_app.views.modern_guide_view as mgv
                import importlib
                importlib.reload(mgv)
                
                view = mgv.ModernGuideView()

                assert view.webview.url is not None

    @patch('app.core.path_resolver.get_asset_path')
    def test_fallback_html_when_file_missing(self, mock_get_asset_path):
        """Test that HTML fallback is used when guide file is missing."""
        from pathlib import Path
        
        # Mock path that doesn't exist
        mock_path_obj = MagicMock(spec=Path)
        mock_path_obj.exists.return_value = False
        mock_path_obj.__str__ = lambda self: '/fake/path/index.html'
        mock_get_asset_path.return_value = mock_path_obj

        import desktop_app.views.modern_guide_view as mgv
        import importlib
        importlib.reload(mgv)
        
        view = mgv.ModernGuideView()

        # Should show fallback HTML
        assert view.webview.html is not None
        assert "Guida non disponibile" in view.webview.html

    def test_guide_bridge_exists(self):
        """Test that GuideBridge is properly initialized."""
        from desktop_app.views import modern_guide_view
        view = modern_guide_view.ModernGuideView()

        assert hasattr(view, 'bridge')
        assert isinstance(view.bridge, modern_guide_view.GuideBridge)

    def test_web_channel_configured(self):
        """Test that QWebChannel is properly configured."""
        from desktop_app.views import modern_guide_view
        view = modern_guide_view.ModernGuideView()

        assert hasattr(view, 'channel')
        # Channel should be registered with the bridge
        # Note: actual registration testing would require deeper mocking
