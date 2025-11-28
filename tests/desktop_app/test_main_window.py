import sys
import pytest
from unittest.mock import patch, MagicMock
from tests.desktop_app.mock_qt import mock_qt_modules

@pytest.fixture(scope="function")
def mock_qt_env():
    modules = mock_qt_modules()
    with patch.dict(sys.modules, modules):
        # Unload desktop_app modules to force re-import with mocks
        for k in list(sys.modules.keys()):
            if k.startswith('desktop_app'):
                del sys.modules[k]
        yield

def test_mainwindow_init(mock_qt_env):
    """
    Verifies that MainWindow initializes and loads views.
    We patch the views where they are used (in MainDashboardWidget or its methods).
    """

    # We patch the imports inside main_window_ui or wherever they are used.
    # Since MainDashboardWidget does local imports, we must patch the modules they import from.

    with patch("desktop_app.views.database_view.DatabaseView") as MockDash, \
         patch("desktop_app.views.import_view.ImportView") as MockImport, \
         patch("desktop_app.views.validation_view.ValidationView") as MockValid, \
         patch("desktop_app.views.scadenzario_view.ScadenzarioView") as MockScad, \
         patch("desktop_app.views.config_view.ConfigView") as MockConfig, \
         patch("desktop_app.views.modern_guide_view.ModernGuideView") as MockGuide, \
         patch("desktop_app.main_window_ui.QIcon") as MockIcon, \
         patch("os.path.exists", return_value=True):

        # Mock QIcon.isNull to return False (so it enters if block)
        MockIcon.return_value.isNull.return_value = False

        from desktop_app.main_window_ui import MainDashboardWidget

        # Mock api client
        mock_client = MagicMock()
        window = MainDashboardWidget(mock_client)
        assert window.stacked_widget is not None

        # Test switch
        window.switch_to("database")
        assert window.page_title.text() != ""

        # Verify views were instantiated
        # DatabaseView is loaded immediately
        MockDash.assert_called()

def test_sidebar_init(mock_qt_env):
    with patch("desktop_app.main_window_ui.QIcon") as MockIcon, \
         patch("os.path.exists", return_value=True):

        MockIcon.return_value.isNull.return_value = False

        from desktop_app.main_window_ui import Sidebar
        sidebar = Sidebar()
        # Sidebar adds buttons
        assert len(sidebar.buttons) > 0
