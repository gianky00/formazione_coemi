import os

import pytest

from app.services.document_locator import find_document
from app.utils.file_security import sanitize_filename


@pytest.fixture
def base_cert_data():
    return {
        "nome": "ROSSI MARIO",
        "matricola": "12345",
        "categoria": "ANTINCENDIO",
        "data_scadenza": "31/12/2025",
    }


def test_find_document_success_active(tmp_path, base_cert_data):
    mock_db_path = str(tmp_path)
    nome_fs = sanitize_filename("ROSSI MARIO")
    cat_fs = sanitize_filename("ANTINCENDIO")
    expected_filename = f"{nome_fs} (12345) - {cat_fs} - 31_12_2025.pdf"

    expected_path = os.path.join(
        mock_db_path,
        "DOCUMENTI DIPENDENTI",
        f"{nome_fs} (12345)",
        cat_fs,
        "ATTIVO",
        expected_filename,
    )
    os.makedirs(os.path.dirname(expected_path), exist_ok=True)
    with open(expected_path, "w") as f:
        f.write("dummy")


    result = find_document(mock_db_path, base_cert_data)
    assert result == expected_path


def test_find_document_success_fallback_status(tmp_path, base_cert_data):
    mock_db_path = str(tmp_path)
    nome_fs = sanitize_filename("ROSSI MARIO")
    cat_fs = sanitize_filename("ANTINCENDIO")
    expected_filename = f"{nome_fs} (12345) - {cat_fs} - 31_12_2025.pdf"

    target_path = os.path.join(
        mock_db_path,
        "DOCUMENTI DIPENDENTI",
        f"{nome_fs} (12345)",
        cat_fs,
        "STORICO",
        expected_filename,
    )
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w") as f:
        f.write("dummy")


    result = find_document(mock_db_path, base_cert_data)
    assert result == target_path


def test_find_document_missing_matricola(tmp_path):
    mock_db_path = str(tmp_path)
    cert_data = {
        "nome": "VERDI LUIGI",
        "matricola": None,
        "categoria": "VISITA MEDICA",
        "data_scadenza": "01/01/2024",
    }
    nome_fs = sanitize_filename("VERDI LUIGI")
    cat_fs = sanitize_filename("VISITA MEDICA")

    expected_filename = f"{nome_fs} (N-A) - {cat_fs} - 01_01_2024.pdf"
    expected_path = os.path.join(
        mock_db_path,
        "DOCUMENTI DIPENDENTI",
        f"{nome_fs} (N-A)",
        cat_fs,
        "ATTIVO",
        expected_filename,
    )
    os.makedirs(os.path.dirname(expected_path), exist_ok=True)
    with open(expected_path, "w") as f:
        f.write("dummy")


    result = find_document(mock_db_path, cert_data)
    assert result == expected_path


def test_find_document_date_parsing_formats(tmp_path, base_cert_data):
    mock_db_path = str(tmp_path)
    base_cert_data["data_scadenza"] = None
    nome_fs = sanitize_filename("ROSSI MARIO")
    cat_fs = sanitize_filename("ANTINCENDIO")

    expected_filename_1 = f"{nome_fs} (12345) - {cat_fs} - no scadenza.pdf"
    path_1 = os.path.join(
        mock_db_path,
        "DOCUMENTI DIPENDENTI",
        f"{nome_fs} (12345)",
        cat_fs,
        "ATTIVO",
        expected_filename_1,
    )
    os.makedirs(os.path.dirname(path_1), exist_ok=True)
    with open(path_1, "w") as f:
        f.write("dummy")


    result = find_document(mock_db_path, base_cert_data)
    assert result == path_1


def test_find_document_in_error_folders(tmp_path, base_cert_data):
    mock_db_path = str(tmp_path)
    nome_fs = sanitize_filename("ROSSI MARIO")
    cat_fs = sanitize_filename("ANTINCENDIO")
    expected_filename = f"{nome_fs} (12345) - {cat_fs} - 31_12_2025.pdf"

    target_path = os.path.join(
        mock_db_path,
        "ERRORI ANALISI",
        "ASSENZA MATRICOLE",
        f"{nome_fs} (12345)",
        cat_fs,
        "ATTIVO",
        expected_filename,
    )
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w") as f:
        f.write("dummy")


    result = find_document(mock_db_path, base_cert_data)
    assert result == target_path


def test_find_document_not_found(tmp_path, base_cert_data):
    result = find_document(str(tmp_path), base_cert_data)
    assert result is None
