import os
from app.services.document_locator import find_document
from app.utils.file_security import sanitize_filename

def test_find_document_sanitizes_path(tmp_path):
    db_path = str(tmp_path)
    cert_data = {"nome": "De/Rossi Mario", "matricola": "123", "categoria": "ANTINCENDIO", "data_scadenza": "01/01/2025"}
    
    nome_fs = sanitize_filename("De/Rossi Mario")
    cat_fs = sanitize_filename("ANTINCENDIO")
    
    sanitized_folder = f"{nome_fs} (123)"
    sanitized_filename = f"{nome_fs} (123) - {cat_fs} - 01_01_2025.pdf"
    
    expected_path = os.path.join(db_path, "DOCUMENTI DIPENDENTI", sanitized_folder, cat_fs, "ATTIVO", sanitized_filename)
    os.makedirs(os.path.dirname(expected_path), exist_ok=True)
    with open(expected_path, "w") as f: f.write("dummy")
    
    result = find_document(db_path, cert_data)
    assert result == expected_path
