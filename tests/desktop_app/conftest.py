import sys
import pytest
from tests.desktop_app.mock_qt import mock_qt_modules

@pytest.fixture(scope="session", autouse=True)
def mock_qt_globally():
    """
    Mocks PyQt6 modules globally for all desktop_app tests.
    This ensures that no real Qt bindings are used, preventing
    headless crashes and ensuring tests run in a controlled environment.
    """
    modules = mock_qt_modules()
    for name, mod in modules.items():
        if name not in sys.modules:
            sys.modules[name] = mod
