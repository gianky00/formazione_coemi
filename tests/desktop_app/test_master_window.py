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

def test_master_window_init(mock_qt_env):
    """
    Verifies that MasterWindow definition is valid and can be instantiated.
    This catches NameError if QMainWindow is not imported.
    """
    # We need to mock things used in MasterWindow.__init__

    with patch("desktop_app.components.animated_widgets.AnimatedStackedWidget"), \
         patch("desktop_app.views.login_view.LoginView"), \
         patch("desktop_app.main_window_ui.MainDashboardWidget"):

        from desktop_app.main import MasterWindow, ApplicationController

        mock_controller = MagicMock()
        mock_controller.api_client = MagicMock()

        # Instantiate
        window = MasterWindow(mock_controller, license_ok=True, license_error="")
        assert window is not None
