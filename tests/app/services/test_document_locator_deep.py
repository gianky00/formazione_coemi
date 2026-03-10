import os

from app.services.document_locator import find_document
from app.utils.file_security import sanitize_filename


def test_find_document_partial_match(tmp_path):
    db_path = str(tmp_path)
    nome_fs = sanitize_filename("MARIO ROSSI")
    cat_fs = sanitize_filename("SICUREZZA")

    emp_folder = os.path.join(db_path, "DOCUMENTI DIPENDENTI", f"{nome_fs} (123)")
    cat_folder = os.path.join(emp_folder, cat_fs, "ATTIVO")
    os.makedirs(cat_folder, exist_ok=True)

    filename = f"{nome_fs} - {cat_fs} - random stuff.pdf"
    file_path = os.path.join(cat_folder, filename)
    with open(file_path, "w") as f:
        f.write("dummy")


    cert_data = {
        "nome": "MARIO ROSSI",
        "matricola": "123",
        "categoria": "SICUREZZA",
        "data_scadenza": "01/01/2025",
    }

    result = find_document(db_path, cert_data)
    assert result is not None
    assert os.path.normpath(result) == os.path.normpath(file_path)


def test_find_document_deep_search(tmp_path):
    db_path = str(tmp_path)
    nome_fs = sanitize_filename("MARIO ROSSI")
    deep_folder = os.path.join(db_path, "DOCUMENTI DIPENDENTI", "LOST_AND_FOUND", "ROSSI")
    os.makedirs(deep_folder, exist_ok=True)

    filename = f"CERT {nome_fs} FIRE.pdf"
    file_path = os.path.join(deep_folder, filename)
    with open(file_path, "w") as f:
        f.write("dummy")


    cert_data = {
        "nome": "MARIO ROSSI",
        "matricola": "999",
        "categoria": "FIRE",
        "data_scadenza": "01/01/2025",
    }

    result = find_document(db_path, cert_data)
    assert result is not None
    assert os.path.normpath(result) == os.path.normpath(file_path)


def test_find_document_wrong_extension(tmp_path):
    db_path = str(tmp_path)
    nome_fs = sanitize_filename("MARIO ROSSI")
    cat_fs = sanitize_filename("SICUREZZA")
    emp_folder = os.path.join(db_path, "DOCUMENTI DIPENDENTI", f"{nome_fs} (123)", cat_fs, "ATTIVO")
    os.makedirs(emp_folder, exist_ok=True)

    file_path = os.path.join(emp_folder, f"{nome_fs} (123) - {cat_fs} - 01_01_2025.txt")
    with open(file_path, "w") as f:
        f.write("dummy")


    cert_data = {
        "nome": "MARIO ROSSI",
        "matricola": "123",
        "categoria": "SICUREZZA",
        "data_scadenza": "01/01/2025",
    }

    result = find_document(db_path, cert_data)
    assert result is None


def test_find_document_prioritize_category_in_deep_search(tmp_path):
    db_path = str(tmp_path)
    docs_dir = os.path.join(db_path, "DOCUMENTI DIPENDENTI")
    os.makedirs(docs_dir, exist_ok=True)

    nome_fs = sanitize_filename("MARIO ROSSI")
    f1 = os.path.join(docs_dir, f"{nome_fs} General.pdf")
    f2 = os.path.join(docs_dir, f"{nome_fs} Security.pdf")

    for f in [f1, f2]:
        with open(f, "w") as out:
            out.write("dummy")


    cert_data = {
        "nome": "MARIO ROSSI",
        "matricola": "N-A",
        "categoria": "Security",
        "data_scadenza": None,
    }

    result = find_document(db_path, cert_data)
    assert result is not None
    assert os.path.basename(result) == f"{nome_fs} Security.pdf"
