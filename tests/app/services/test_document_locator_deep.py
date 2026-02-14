import os

from app.services.document_locator import find_document


def test_find_document_partial_match(tmp_path):
    # Setup: a file that doesn't follow the exact filename convention but contains name and category
    db_path = str(tmp_path)
    # Current logic: nome_fs will have spaces if input has spaces.
    # We must use spaces in filename to match current glob implementation.
    emp_folder = os.path.join(db_path, "DOCUMENTI DIPENDENTI", "MARIO ROSSI (123)")
    cat_folder = os.path.join(emp_folder, "SICUREZZA", "ATTIVO")
    os.makedirs(cat_folder, exist_ok=True)

    # Filename with spaces to match nome_fs
    filename = "MARIO ROSSI - SICUREZZA - random stuff.pdf"
    file_path = os.path.join(cat_folder, filename)
    with open(file_path, "w") as f:
        f.write("dummy")

    cert_data = {
        "nome": "MARIO ROSSI",
        "matricola": "123",
        "categoria": "SICUREZZA",
        "data_scadenza": "01/01/2025",
    }

    # Should find it via _search_partial_match (step 4)
    result = find_document(db_path, cert_data)
    assert result is not None
    assert os.path.normpath(result) == os.path.normpath(file_path)


def test_find_document_deep_search(tmp_path):
    # Setup: file hidden deep in the tree in a non-standard subfolder
    db_path = str(tmp_path)
    deep_folder = os.path.join(db_path, "DOCUMENTI DIPENDENTI", "LOST_AND_FOUND", "ROSSI")
    os.makedirs(deep_folder, exist_ok=True)

    filename = "CERT MARIO ROSSI FIRE.pdf"
    file_path = os.path.join(deep_folder, filename)
    with open(file_path, "w") as f:
        f.write("dummy")

    cert_data = {
        "nome": "MARIO ROSSI",
        "matricola": "999",  # Different matricola
        "categoria": "FIRE",
        "data_scadenza": "01/01/2025",
    }

    # Should find it via _search_in_folder_tree (step 5)
    result = find_document(db_path, cert_data)
    assert result is not None
    assert os.path.normpath(result) == os.path.normpath(file_path)


def test_find_document_wrong_extension(tmp_path):
    db_path = str(tmp_path)
    emp_folder = os.path.join(
        db_path, "DOCUMENTI DIPENDENTI", "MARIO ROSSI (123)", "SICUREZZA", "ATTIVO"
    )
    os.makedirs(emp_folder, exist_ok=True)

    # Not a PDF
    file_path = os.path.join(emp_folder, "MARIO ROSSI (123) - SICUREZZA - 01_01_2025.txt")
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

    # Two files for Mario Rossi
    f1 = os.path.join(docs_dir, "MARIO ROSSI General.pdf")
    f2 = os.path.join(docs_dir, "MARIO ROSSI Security.pdf")

    for f in [f1, f2]:
        with open(f, "w") as out:
            out.write("dummy")

    cert_data = {
        "nome": "MARIO ROSSI",
        "matricola": "N-A",
        "categoria": "Security",
        "data_scadenza": None,
    }

    # Deep search should prefer f2 because it contains "Security"
    result = find_document(db_path, cert_data)
    assert result is not None
    assert os.path.basename(result) == "MARIO ROSSI Security.pdf"
