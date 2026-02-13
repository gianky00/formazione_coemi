import os
from unittest import mock

import pytest

from app.db.models import AuditLog, Certificato
from app.services.file_maintenance import clean_all_empty_folders, organize_expired_files


@pytest.fixture
def mock_db_session():
    return mock.MagicMock()


def test_clean_all_empty_folders(test_dirs):
    # Setup: root/a/b/c (empty), root/x/y/file.txt (not empty)
    root = os.path.join(str(test_dirs), "cleanup_test")
    os.makedirs(os.path.join(root, "a", "b", "c"), exist_ok=True)
    os.makedirs(os.path.join(root, "x", "y"), exist_ok=True)
    with open(os.path.join(root, "x", "y", "file.txt"), "w") as f:
        f.write("keep")

    clean_all_empty_folders(root)

    # Assert a/b/c gone
    assert not os.path.exists(os.path.join(root, "a"))
    # Assert x/y stays
    assert os.path.exists(os.path.join(root, "x", "y", "file.txt"))
    # Root stays
    assert os.path.exists(root)


def test_daily_maintenance_calls_cleanup(mock_db_session, test_dirs):
    # Setup: No audit log (so it runs)
    # query(AuditLog)... -> None
    # query(Certificato)... -> []

    def query_side_effect(model):
        m = mock.MagicMock()
        if model == AuditLog:
            m.filter.return_value.first.return_value = None
        elif model == Certificato:
            m.filter.return_value.all.return_value = []
        return m

    mock_db_session.query.side_effect = query_side_effect

    with (
        mock.patch("app.services.file_maintenance.settings") as mock_settings,
        mock.patch("app.services.file_maintenance.os.path.exists", return_value=True),
        mock.patch("app.services.file_maintenance.clean_all_empty_folders") as mock_clean,
        mock.patch("app.services.file_maintenance.log_security_action"),
    ):
        mock_settings.DATABASE_PATH = str(test_dirs)

        organize_expired_files(mock_db_session)

        # Assert cleanup called
        expected_path = os.path.join(str(test_dirs), "DOCUMENTI DIPENDENTI")
        mock_clean.assert_called_with(expected_path)
