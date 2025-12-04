import pytest
from unittest.mock import patch, MagicMock
import os
from app.services.document_locator import find_document

@pytest.fixture
def mock_db_path():
    return "/mock/db/path"

@pytest.fixture
def base_cert_data():
    return {
        "nome": "ROSSI MARIO",
        "matricola": "12345",
        "categoria": "ANTINCENDIO",
        "data_scadenza": "31/12/2025"
    }

def test_find_document_success_active(mock_db_path, base_cert_data):
    """Test finding a document in the primary status folder (ATTIVO)."""
    expected_filename = "ROSSI MARIO (12345) - ANTINCENDIO - 31_12_2025.pdf"
    expected_path = os.path.join(mock_db_path, "DOCUMENTI DIPENDENTI", "ROSSI MARIO (12345)", "ANTINCENDIO", "ATTIVO", expected_filename)

    with patch("os.path.isfile") as mock_isfile:
        # Simulate file exists only at the expected path
        mock_isfile.side_effect = lambda x: x == expected_path

        result = find_document(mock_db_path, base_cert_data)
        assert result == expected_path

def test_find_document_success_fallback_status(mock_db_path, base_cert_data):
    """Test finding a document in a fallback status folder (e.g., STORICO)."""
    expected_filename = "ROSSI MARIO (12345) - ANTINCENDIO - 31_12_2025.pdf"
    target_path = os.path.join(mock_db_path, "DOCUMENTI DIPENDENTI", "ROSSI MARIO (12345)", "ANTINCENDIO", "STORICO", expected_filename)

    with patch("os.path.isfile") as mock_isfile:
        mock_isfile.side_effect = lambda x: x == target_path

        result = find_document(mock_db_path, base_cert_data)
        assert result == target_path

def test_find_document_missing_matricola(mock_db_path):
    """Test that missing matricola defaults to 'N-A'."""
    cert_data = {
        "nome": "VERDI LUIGI",
        "matricola": None, # Missing
        "categoria": "VISITA MEDICA",
        "data_scadenza": "01/01/2024"
    }

    # Expect folder "VERDI LUIGI (N-A)"
    expected_filename = "VERDI LUIGI (N-A) - VISITA MEDICA - 01_01_2024.pdf"
    expected_path = os.path.join(mock_db_path, "DOCUMENTI DIPENDENTI", "VERDI LUIGI (N-A)", "VISITA MEDICA", "ATTIVO", expected_filename)

    with patch("os.path.isfile") as mock_isfile:
        mock_isfile.side_effect = lambda x: x == expected_path

        result = find_document(mock_db_path, cert_data)
        assert result == expected_path

def test_find_document_date_parsing_formats(mock_db_path, base_cert_data):
    """Test handling of different date formats or invalid dates."""
    # Case 1: None -> 'no scadenza'
    base_cert_data["data_scadenza"] = None
    expected_filename_1 = "ROSSI MARIO (12345) - ANTINCENDIO - no scadenza.pdf"
    path_1 = os.path.join(mock_db_path, "DOCUMENTI DIPENDENTI", "ROSSI MARIO (12345)", "ANTINCENDIO", "ATTIVO", expected_filename_1)

    # Case 2: Invalid -> 'no scadenza'
    base_cert_data_2 = base_cert_data.copy()
    base_cert_data_2["data_scadenza"] = "invalid-date"
    # Same filename expectation as None

    with patch("os.path.isfile") as mock_isfile:
        mock_isfile.side_effect = lambda x: x == path_1

        # Run Case 1
        result = find_document(mock_db_path, base_cert_data)
        assert result == path_1

        # Run Case 2
        mock_isfile.side_effect = lambda x: x == path_1
        result_2 = find_document(mock_db_path, base_cert_data_2)
        assert result_2 == path_1

def test_find_document_in_error_folders(mock_db_path, base_cert_data):
    """Test finding a document in the ERRORI ANALISI structure."""
    expected_filename = "ROSSI MARIO (12345) - ANTINCENDIO - 31_12_2025.pdf"
    # Structure: ERRORI ANALISI / <ErrCategory> / <EmployeeFolder> / <Category> / <Status> / <Filename>
    # Note: Logic iterates error_categories. Let's place it in "ASSENZA MATRICOLE"
    target_path = os.path.join(mock_db_path, "ERRORI ANALISI", "ASSENZA MATRICOLE", "ROSSI MARIO (12345)", "ANTINCENDIO", "ATTIVO", expected_filename)

    with patch("os.path.isfile") as mock_isfile:
        mock_isfile.side_effect = lambda x: x == target_path

        result = find_document(mock_db_path, base_cert_data)
        assert result == target_path

def test_find_document_not_found(mock_db_path, base_cert_data):
    """Test return None when file exists nowhere."""
    with patch("os.path.isfile") as mock_isfile:
        mock_isfile.return_value = False

        result = find_document(mock_db_path, base_cert_data)
        assert result is None

def test_find_document_empty_inputs():
    """Test robust handling of empty inputs."""
    assert find_document(None, {}) is None
    assert find_document("/path", None) is None
    assert find_document("", {}) is None
