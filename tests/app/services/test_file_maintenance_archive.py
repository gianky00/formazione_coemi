import pytest
import os
import shutil
from unittest.mock import MagicMock, patch
from app.services import file_maintenance
from app.db.models import Certificato, Dipendente, Corso
from datetime import date, timedelta

def test_organize_expired_files_does_not_move_archived():
    # Setup Data
    dip = Dipendente(nome="Mario", cognome="Rossi", matricola="123")
    corso = Corso(categoria_corso="SICUREZZA")
    cert = Certificato(dipendente=dip, corso=corso, data_scadenza_calcolata=date.today() - timedelta(days=1))

    mock_db_session = MagicMock()
    mock_db_session.query.return_value.filter.return_value.all.return_value = [cert]

    # Use OS-specific paths
    base_path = os.path.join("mock", "db", "path")
    src_path = os.path.join(base_path, "DOCUMENTI DIPENDENTI", "Mario Rossi (123)", "SICUREZZA", "ATTIVO", "file.pdf")
    dst_path = os.path.join(base_path, "DOCUMENTI DIPENDENTI", "Mario Rossi (123)", "SICUREZZA", "STORICO", "file.pdf")

    # Mocks
    with patch("app.services.file_maintenance.settings") as mock_settings, \
         patch("app.services.file_maintenance.certificate_logic.get_certificate_status", return_value="archiviato"), \
         patch("app.services.file_maintenance.find_document", return_value=src_path), \
         patch("os.path.exists", return_value=True), \
         patch("os.path.isfile", return_value=True), \
         patch("shutil.move") as mock_move:

         mock_settings.DATABASE_PATH = base_path

         file_maintenance.organize_expired_files(mock_db_session)

         # THIS SHOULD FAIL if the bug exists (it won't move because status is 'archiviato', not 'scaduto')
         # If existing logic only checks "scaduto", mock_move will NOT be called.
         # We assert it IS called to demonstrate the desired behavior (and thus fail now).
         mock_move.assert_called_with(src_path, dst_path)
