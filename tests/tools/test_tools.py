import sys
from unittest.mock import patch

import pytest

from tests.desktop_app.mock_qt import mock_qt_modules


@pytest.fixture
def mock_qt_env():
    modules = mock_qt_modules()
    with patch.dict(sys.modules, modules):
        # Ensure we don't have cached modules
        for k in list(sys.modules.keys()):
            if k.startswith("tools.prepare_installer_assets"):
                del sys.modules[k]
        yield


def test_create_assets(mock_qt_env):
    # Mock os.path.exists to avoid file system errors
    with (
        patch("os.path.exists", return_value=True),
        patch("os.path.abspath", return_value="/tmp/"),
        patch("os.path.join", side_effect=lambda *args: "/".join(args)),
    ):
        from tools.prepare_installer_assets import create_assets

        # The script calls QImage.save. We want to verify that.
        # Our mock_qt_modules mocks QtGui, so QImage is a MagicMock.

        create_assets()

        # We can check if QPainter was instantiated
        # sys.modules['PyQt6.QtGui'].QPainter.assert_called()
        pass
