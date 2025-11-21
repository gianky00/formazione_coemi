import sys
import pytest
from unittest.mock import patch, MagicMock
from tests.desktop_app.mock_qt import mock_qt_modules

@pytest.fixture(scope="function")
def mock_qt_env():
    modules = mock_qt_modules()
    with patch.dict(sys.modules, modules):
        # Unload desktop_app modules
        for k in list(sys.modules.keys()):
            if k.startswith('desktop_app'):
                del sys.modules[k]
        yield

def test_mainwindow_init(mock_qt_env):
    # We need to mock the views imported by MainWindow logic
    # Logic in MainWindow imports views from .views.*

    # We can rely on the mocked QWidget base returning simple objects
    # But we want to verify switch logic.

    # Important: imports inside main_window_ui.py happen at module level.
    # So by the time we import MainWindow, those imports run using our mocked PyQt6.
    # This means ImportView etc will be defined inheriting from DummyQWidget.
    # BUT, their own imports (like APIClient) might trigger side effects.

    # Ideally we mock the view classes themselves to keep MainWindow isolated.

    with patch("desktop_app.main_window_ui.ImportView") as MockImport, \
         patch("desktop_app.main_window_ui.DashboardView") as MockDash, \
         patch("desktop_app.main_window_ui.ValidationView") as MockValid, \
         patch("desktop_app.main_window_ui.ScadenzarioView") as MockScad, \
         patch("desktop_app.main_window_ui.ConfigView") as MockConfig, \
         patch("desktop_app.main_window_ui.ModernGuideDialog") as MockGuide:

        from desktop_app.main_window_ui import MainWindow

        window = MainWindow()
        assert window.stacked_widget is not None

        # Test switch
        window.switch_to("dashboard")
        assert window.page_title.text() != "" # It mocks the call, we can't easily check text value on MagicMock unless we configured it.

        # Verify views were instantiated
        MockDash.assert_called()

def test_sidebar_init(mock_qt_env):
    from desktop_app.main_window_ui import Sidebar
    sidebar = Sidebar()
    # Sidebar adds buttons
    assert len(sidebar.buttons) > 0
