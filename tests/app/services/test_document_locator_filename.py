import os
from unittest.mock import patch

from app.services.document_locator import find_document


def test_find_document_sanitizes_path():
    """
    This test verifies that document_locator correctly sanitizes input data
    to match the file system naming conventions.
    """
    db_path = "/mock/db"
    # Ensure consistent path format across OS
    db_path = os.path.normpath(db_path)

    cert_data = {
        "nome": "De/Rossi Mario",
        "matricola": "123",
        "categoria": "ANTINCENDIO",
        "data_scadenza": "01/01/2025",
    }

    sanitized_folder = "De_Rossi Mario (123)"
    sanitized_filename = "De_Rossi Mario (123) - ANTINCENDIO - 01_01_2025.pdf"

    expected_path = os.path.join(
        db_path,
        "DOCUMENTI DIPENDENTI",
        sanitized_folder,
        "ANTINCENDIO",
        "ATTIVO",
        sanitized_filename,
    )
    expected_path = os.path.normpath(expected_path)

    with patch("os.path.isfile") as mock_isfile:
        mock_isfile.side_effect = lambda p: os.path.normpath(p) == expected_path

        result = find_document(db_path, cert_data)

        # This assertion will fail until the bug is fixed
        assert result == expected_path
