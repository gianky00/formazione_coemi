from unittest.mock import MagicMock, patch

import pytest

from app.core.db_security import DBSecurityManager


@pytest.fixture
def manager(tmp_path):
    with (
        patch("app.core.db_security.settings") as mock_settings,
        patch("app.core.db_security.get_user_data_dir", return_value=tmp_path),
    ):
        mock_settings.DATABASE_PATH = None
        mgr = DBSecurityManager()
        mgr.db_path = tmp_path / "database_documenti.db"
        mgr.lock_path = tmp_path / ".test.db.lock"
        return mgr


def test_stale_lock_corrupt_json(manager, tmp_path):
    lock = tmp_path / ".test.db.lock"
    lock.write_bytes(b"L{bad_json")

    # Ensure we mock the method on the instance, and it returns None
    with patch.object(manager, "_force_remove_lock", autospec=True) as mock_rem:
        manager._check_and_recover_stale_lock()
        mock_rem.assert_called()


def test_read_only_save_blocked(manager):
    manager.is_read_only = True
    manager.active_connection = MagicMock()

    assert manager.save_to_disk() is False
    manager.active_connection.serialize.assert_not_called()


def test_save_disk_failure(manager):
    manager.is_read_only = False
    manager.active_connection = MagicMock()
    manager.active_connection.serialize.side_effect = Exception("Disk full")

    assert manager.save_to_disk() is False
