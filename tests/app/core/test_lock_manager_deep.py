import sys
from unittest.mock import MagicMock, patch

import pytest

from app.core.lock_manager import LockManager


@pytest.fixture
def mock_path(tmp_path):
    return str(tmp_path / ".lock")


def test_lock_byte_0_windows(mock_path):
    mgr = LockManager(mock_path)
    mgr._lock_handle = MagicMock()

    mock_msvcrt = MagicMock()

    with patch("os.name", "nt"), patch.dict(sys.modules, {"msvcrt": mock_msvcrt}):
        mgr._lock_byte_0()

        mock_msvcrt.locking.assert_called()


def test_acquire_generic_exception(mock_path):
    mgr = LockManager(mock_path)

    with patch("builtins.open", side_effect=Exception("Generic Fail")):
        success, owner = mgr.acquire({"uuid": "1"}, retries=0)

    assert success is False
    assert "Error: Generic Fail" in owner["error"]
