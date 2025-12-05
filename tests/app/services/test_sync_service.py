
import pytest
from unittest.mock import MagicMock, patch
from app.services import sync_service
import shutil

# --- Bug 3, 4, 7: Sync Service Tests ---

def test_sync_service_calls_bulk():
    """
    Bug 3 Check: synchronize_all_files should use bulk status check.
    """
    mock_db = MagicMock()
    # Mock certs
    c1 = MagicMock(id=1); 
    c1.corso.categoria_corso = "A"
    c1.dipendente = None; c1.nome_dipendente_raw = "N"
    c1.data_scadenza_calcolata = None
    
    c2 = MagicMock(id=2); 
    c2.corso.categoria_corso = "B"
    c2.dipendente = None; c2.nome_dipendente_raw = "M"
    c2.data_scadenza_calcolata = None
    
    mock_certs = [c1, c2]
    mock_db.query.return_value.options.return_value.all.return_value = mock_certs
    
    # Patch dependencies
    with patch("app.services.sync_service.certificate_logic.get_bulk_certificate_statuses") as mock_bulk, \
         patch("app.services.sync_service.certificate_logic.get_certificate_status") as mock_single, \
         patch("app.services.sync_service.find_document", return_value="/tmp/found.pdf"), \
         patch("os.path.exists", return_value=True), \
         patch("app.services.sync_service.construct_certificate_path", return_value="/tmp/found.pdf"), \
         patch("shutil.move"):
         
         mock_bulk.return_value = {1: "attivo", 2: "scaduto"}
         
         sync_service.synchronize_all_files(mock_db)
         
         mock_bulk.assert_called_once()
         mock_single.assert_not_called()

def test_file_move_permission_error():
    """
    Bug 4: shutil.move crashes on PermissionError (File in use).
    Expectation: Catch error, log it, return False/continue (don't crash).
    """
    mock_db = MagicMock()
    # Single cert to trigger move
    c1 = MagicMock(id=1); c1.corso.categoria_corso = "A"; c1.dipendente = None
    c1.nome_dipendente_raw = "N"; c1.data_scadenza_calcolata = None
    mock_db.query.return_value.options.return_value.all.return_value = [c1]

    with patch("app.services.sync_service.certificate_logic.get_bulk_certificate_statuses", return_value={1:"attivo"}), \
         patch("app.services.sync_service.find_document", return_value="/old/path.pdf"), \
         patch("os.path.exists", return_value=True), \
         patch("app.services.sync_service.construct_certificate_path", return_value="/new/path.pdf"), \
         patch("shutil.move", side_effect=PermissionError("File locked")):
         
         # Should not raise exception
         try:
             sync_service.synchronize_all_files(mock_db)
         except PermissionError:
             pytest.fail("synchronize_all_files crashed on PermissionError")

def test_remove_empty_folders_safety():
    """
    Bug 7: remove_empty_folders recurses up to root.
    Expectation: It should stop at a safe root path.
    """
    with patch("os.rmdir") as mock_rmdir, \
         patch("os.path.isdir", return_value=True), \
         patch("os.listdir") as mock_listdir:
         
         # Setup mocks
         root_path = "/root/db"
         
         # Test Guard:
         # 1. Path is root -> No delete
         sync_service.remove_empty_folders(root_path, root_path=root_path)
         mock_rmdir.assert_not_called()
