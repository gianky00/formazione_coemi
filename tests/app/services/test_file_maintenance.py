import pytest
import os
from unittest.mock import MagicMock, patch
from app.services import file_maintenance
from app.db.models import Certificato, Dipendente, Corso
from datetime import date, timedelta

@pytest.fixture
def mock_settings():
    with patch("app.services.file_maintenance.settings") as mock:
        mock.DATABASE_PATH = "/mock/db/path"
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
    cert = Certificato(dipendente=dip, corso=corso, data_scadenza_calcolata=date.today() - timedelta(days=1))

    mock_db_session.query.return_value.filter.return_value.all.return_value = [cert]

    # Mocks
    with patch("app.services.file_maintenance.certificate_logic.get_certificate_status", return_value="scaduto"), \
         patch("app.services.file_maintenance.find_document", return_value="/mock/db/path/DIP/SICUREZZA/ATTIVO/file.pdf"), \
         patch("os.path.exists") as mock_exists, \
         patch("os.path.isfile", return_value=True), \
         patch("os.makedirs") as mock_makedirs, \
         patch("shutil.move") as mock_move:

         # os.path.exists side effect: True for DB path, False for STORICO dir (so it creates it)
         def exists_side_effect(path):
             if path == "/mock/db/path": return True
             if "STORICO" in path: return False
             return True
         mock_exists.side_effect = exists_side_effect

         file_maintenance.organize_expired_files(mock_db_session)

         mock_makedirs.assert_called() # Should create STORICO
         mock_move.assert_called_with(
             "/mock/db/path/DIP/SICUREZZA/ATTIVO/file.pdf",
             "/mock/db/path/DIP/SICUREZZA/STORICO/file.pdf"
         )

def test_organize_expired_files_already_archived(mock_settings, mock_db_session):
    cert = Certificato(data_scadenza_calcolata=date.today() - timedelta(days=1))
    mock_db_session.query.return_value.filter.return_value.all.return_value = [cert]

    with patch("app.services.file_maintenance.certificate_logic.get_certificate_status", return_value="scaduto"), \
         patch("app.services.file_maintenance.find_document", return_value="/mock/db/path/DIP/SICUREZZA/STORICO/file.pdf"), \
         patch("os.path.exists", return_value=True), \
         patch("os.path.isfile", return_value=True), \
         patch("shutil.move") as mock_move:

         file_maintenance.organize_expired_files(mock_db_session)
         mock_move.assert_not_called()

def test_organize_expired_files_active_status(mock_settings, mock_db_session):
    # If status returns "attivo" (e.g. manually overridden or logic quirk), don't move
    cert = Certificato(data_scadenza_calcolata=date.today() - timedelta(days=1))
    mock_db_session.query.return_value.filter.return_value.all.return_value = [cert]

    with patch("app.services.file_maintenance.certificate_logic.get_certificate_status", return_value="attivo"), \
         patch("app.services.file_maintenance.find_document", return_value="/path/file.pdf"), \
         patch("shutil.move") as mock_move:

         file_maintenance.organize_expired_files(mock_db_session)
         mock_move.assert_not_called()
