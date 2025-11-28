import sys
import pytest
from tests.desktop_app.mock_qt import mock_qt_modules

# Apply mocks immediately at import time to prevent ModuleNotFoundError during collection
modules = mock_qt_modules()
for name, mod in modules.items():
    if name not in sys.modules:
        sys.modules[name] = mod

@pytest.fixture(scope="session", autouse=True)
def mock_qt_globally():
    """
    Fixture to ensure mocks are present (redundant if applied above, but keeps structure).
    """
    pass
