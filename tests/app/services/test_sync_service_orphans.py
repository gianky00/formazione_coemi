
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from app.services import sync_service
from app.db.models import Certificato, Dipendente
from datetime import date

# Tests for link_orphaned_certificates in app/services/sync_service.py
# Covers lines 133-193

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_dipendente():
    d = MagicMock(spec=Dipendente)
    d.id = 100
    d.nome = "Mario"
    d.cognome = "Rossi"
    d.matricola = "12345"
    d.data_nascita = date(1980, 1, 1)
    return d

def test_link_orphans_success(mock_db, mock_dipendente):
    """
    Test successful linking of an orphaned certificate to an employee.
    Verifies DB update and file move.
    """
    # Setup Orphan Certificate
    orphan = MagicMock(spec=Certificato)
    orphan.id = 1
    orphan.dipendente_id = None
    orphan.nome_dipendente_raw = "Mario Rossi"
    orphan.data_nascita_raw = "01/01/1980"
    orphan.corso.categoria_corso = "SICUREZZA"
    orphan.data_scadenza_calcolata = date(2025, 1, 1)

    # Setup Query Result
    mock_db.query.return_value.options.return_value.filter.return_value.all.return_value = [orphan]

    # Setup Mocks
    # Bug Fix: We must mock get_unique_filename or be careful with os.path.exists
    # because get_unique_filename has a 'while os.path.exists' loop.
    # If we mock os.path.exists to ALWAYS return True, that loop never ends.
    # So we simply mock get_unique_filename to bypass the loop entirely.

    with patch("app.services.sync_service.matcher.find_employee_by_name") as mock_matcher, \
         patch("app.services.sync_service.find_document", return_value="/tmp/orphan/Mario Rossi.pdf") as mock_find, \
         patch("app.services.sync_service.construct_certificate_path", return_value="/tmp/linked/Mario Rossi.pdf") as mock_construct, \
         patch("app.services.sync_service.certificate_logic.get_certificate_status", return_value="attivo"), \
         patch("app.services.sync_service.get_unique_filename", return_value="Mario Rossi.pdf"), \
         patch("os.path.exists", return_value=True), \
         patch("os.makedirs") as mock_makedirs, \
         patch("shutil.move") as mock_move, \
         patch("app.services.sync_service.remove_empty_folders") as mock_cleanup, \
         patch("app.services.sync_service.settings") as mock_settings:

        mock_settings.DATABASE_PATH = "/tmp/db"

        # Matcher returns the target employee
        mock_matcher.return_value = mock_dipendente

        # Execute
        count = sync_service.link_orphaned_certificates(mock_db, mock_dipendente)

        # Assertions
        assert count == 1
        assert orphan.dipendente_id == mock_dipendente.id  # Linked!

        # Verify Matcher Call
        mock_matcher.assert_called_with(mock_db, "Mario Rossi", date(1980, 1, 1))

        # Verify File Move
        mock_find.assert_called()
        mock_construct.assert_called()
        mock_move.assert_called_with("/tmp/orphan/Mario Rossi.pdf", "/tmp/linked/Mario Rossi.pdf")
        mock_cleanup.assert_called()

def test_link_orphans_dob_mismatch(mock_db, mock_dipendente):
    """
    Test that linking is skipped if the orphan's raw DOB doesn't match the employee's DOB.
    """
    orphan = MagicMock(spec=Certificato)
    orphan.id = 2
    orphan.dipendente_id = None
    orphan.nome_dipendente_raw = "Mario Rossi"
    orphan.data_nascita_raw = "05/05/1990" # Different DOB

    mock_db.query.return_value.options.return_value.filter.return_value.all.return_value = [orphan]

    with patch("app.services.sync_service.matcher.find_employee_by_name") as mock_matcher:
        count = sync_service.link_orphaned_certificates(mock_db, mock_dipendente)

        assert count == 0
        assert orphan.dipendente_id is None
        mock_matcher.assert_not_called() # Should skip before calling matcher

def test_link_orphans_no_match(mock_db, mock_dipendente):
    """
    Test that linking is skipped if the matcher returns None or a different employee.
    """
    orphan = MagicMock(spec=Certificato)
    orphan.id = 3
    orphan.dipendente_id = None
    orphan.nome_dipendente_raw = "Luigi Verdi" # Different Name
    orphan.data_nascita_raw = None

    mock_db.query.return_value.options.return_value.filter.return_value.all.return_value = [orphan]

    with patch("app.services.sync_service.matcher.find_employee_by_name") as mock_matcher:
        # Matcher finds nobody
        mock_matcher.return_value = None

        count = sync_service.link_orphaned_certificates(mock_db, mock_dipendente)

        assert count == 0
        assert orphan.dipendente_id is None

def test_link_orphans_file_locked(mock_db, mock_dipendente):
    """
    Test graceful handling of PermissionError during file move.
    """
    orphan = MagicMock(spec=Certificato)
    orphan.id = 1
    orphan.dipendente_id = None
    orphan.nome_dipendente_raw = "Mario Rossi"
    orphan.data_nascita_raw = None # No DOB check
    orphan.corso.categoria_corso = "SICUREZZA"
    orphan.data_scadenza_calcolata = None

    mock_db.query.return_value.options.return_value.filter.return_value.all.return_value = [orphan]

    with patch("app.services.sync_service.matcher.find_employee_by_name", return_value=mock_dipendente), \
         patch("app.services.sync_service.find_document", return_value="/tmp/orphan.pdf"), \
         patch("app.services.sync_service.construct_certificate_path", return_value="/tmp/linked.pdf"), \
         patch("app.services.sync_service.certificate_logic.get_certificate_status", return_value="attivo"), \
         patch("app.services.sync_service.get_unique_filename", return_value="linked.pdf"), \
         patch("os.path.exists", return_value=True), \
         patch("os.makedirs"), \
         patch("shutil.move", side_effect=PermissionError("File in use")), \
         patch("app.services.sync_service.settings") as mock_settings:

        mock_settings.DATABASE_PATH = "/tmp/db"

        # Should not raise exception
        count = sync_service.link_orphaned_certificates(mock_db, mock_dipendente)

        assert count == 1 # Still counted as linked in DB
        assert orphan.dipendente_id == mock_dipendente.id # DB link happens before file move

def test_link_orphans_file_not_found(mock_db, mock_dipendente):
    """
    Test case where the orphan matches but the physical file is missing.
    """
    orphan = MagicMock(spec=Certificato)
    orphan.id = 1
    orphan.nome_dipendente_raw = "Mario Rossi"
    orphan.data_nascita_raw = None
    orphan.corso.categoria_corso = "SICUREZZA"

    mock_db.query.return_value.options.return_value.filter.return_value.all.return_value = [orphan]

    with patch("app.services.sync_service.matcher.find_employee_by_name", return_value=mock_dipendente), \
         patch("app.services.sync_service.find_document", return_value=None), \
         patch("shutil.move") as mock_move, \
         patch("app.services.sync_service.settings") as mock_settings:

        mock_settings.DATABASE_PATH = "/tmp/db"

        count = sync_service.link_orphaned_certificates(mock_db, mock_dipendente)

        assert count == 1
        mock_move.assert_not_called()
