import os
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

from app.db.models import Certificato, Corso, Dipendente
from app.services import file_maintenance


@pytest.fixture
def mock_settings():
    with patch("app.services.file_maintenance.settings") as mock:
        mock.DATABASE_PATH = os.path.join("mock", "db", "path")
        yield mock


@pytest.fixture
def mock_db_session():
    return MagicMock()


def test_organize_expired_files_no_db_path(mock_settings, mock_db_session):
    mock_settings.DATABASE_PATH = None
    with patch("app.services.file_maintenance.get_user_data_dir", return_value=None):
        file_maintenance.organize_expired_files(mock_db_session)
        # Should return early
        mock_db_session.query.assert_not_called()


def test_organize_expired_files_move_success(mock_settings, mock_db_session):
    # Setup Data
    dip = Dipendente(nome="Mario", cognome="Rossi", matricola="123")
    corso = Corso(categoria_corso="SICUREZZA")
    cert = Certificato(
        dipendente=dip, corso=corso, data_scadenza_calcolata=date.today() - timedelta(days=1)
    )

    mock_db_session.query.return_value.filter.return_value.all.return_value = [cert]

    # Use OS-specific paths
    base_path = os.path.join("mock", "db", "path")
    # Note: find_document result is usually absolute.
    # We construct a path that matches what find_document returns (mocked) and what logic expects.

    src_path = os.path.join(base_path, "DIP", "SICUREZZA", "ATTIVO", "file.pdf")
    # Target structure: .../Category/STORICO/file.pdf
    dst_path = os.path.join(base_path, "DIP", "SICUREZZA", "STORICO", "file.pdf")

    # Mocks
    with (
        patch(
            "app.services.file_maintenance.certificate_logic.get_certificate_status",
            return_value="scaduto",
        ),
        patch("app.services.sync_service.find_document", return_value=src_path),
        patch("app.services.sync_service.construct_certificate_path", return_value=dst_path),
        patch("os.path.exists") as mock_exists,
        patch("os.path.isfile", return_value=True),
        patch("os.makedirs") as mock_makedirs,
        patch("shutil.move") as mock_move,
    ):
        # Mock Audit Log check (return None so it runs)
        def query_side_effect(model):
            m = MagicMock()
            if model.__name__ == "AuditLog":
                m.filter.return_value.first.return_value = None  # No existing log today
                return m
            elif model.__name__ == "Certificato":
                m.filter.return_value.all.return_value = [cert]
                return m
            return m

        mock_db_session.query.side_effect = query_side_effect

        # os.path.exists side effect: True for DB path, False for STORICO dir (so it creates it)
        def exists_side_effect(path):
            # Normalize for comparison
            path = os.path.normpath(path)
            if path == os.path.normpath(base_path):
                return True
            if "STORICO" in path:
                return False
            return True

        mock_exists.side_effect = exists_side_effect

        file_maintenance.organize_expired_files(mock_db_session)

        mock_makedirs.assert_called()  # Should create STORICO
        mock_move.assert_called_with(src_path, dst_path)


def test_organize_expired_files_already_archived(mock_settings, mock_db_session):
    cert = Certificato(data_scadenza_calcolata=date.today() - timedelta(days=1))
    mock_db_session.query.return_value.filter.return_value.all.return_value = [cert]

    path = os.path.join("mock", "db", "path", "DIP", "SICUREZZA", "STORICO", "file.pdf")

    with (
        patch(
            "app.services.file_maintenance.certificate_logic.get_certificate_status",
            return_value="scaduto",
        ),
        patch("app.services.file_maintenance.find_document", return_value=path),
        patch("os.path.exists", return_value=True),
        patch("os.path.isfile", return_value=True),
        patch("shutil.move") as mock_move,
    ):
        file_maintenance.organize_expired_files(mock_db_session)
        mock_move.assert_not_called()


def test_organize_expired_files_active_status(mock_settings, mock_db_session):
    # If status returns "attivo" (e.g. manually overridden or logic quirk), don't move
    cert = Certificato(data_scadenza_calcolata=date.today() - timedelta(days=1))
    mock_db_session.query.return_value.filter.return_value.all.return_value = [cert]

    with (
        patch(
            "app.services.file_maintenance.certificate_logic.get_certificate_status",
            return_value="attivo",
        ),
        patch("app.services.file_maintenance.find_document", return_value="/path/file.pdf"),
        patch("shutil.move") as mock_move,
    ):
        file_maintenance.organize_expired_files(mock_db_session)
        mock_move.assert_not_called()
