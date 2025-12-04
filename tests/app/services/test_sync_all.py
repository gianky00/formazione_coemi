import pytest
import os
import shutil
from unittest import mock
from datetime import datetime
from app.db.models import Certificato, Corso, Dipendente
from app.services.file_maintenance import synchronize_all_files, remove_empty_folders
from app.utils.file_security import sanitize_filename

def test_remove_empty_folders(test_dirs):
    # Create structure: a/b/c
    path_a = os.path.join(str(test_dirs), "a")
    path_b = os.path.join(path_a, "b")
    path_c = os.path.join(path_b, "c")
    os.makedirs(path_c, exist_ok=True)

    assert os.path.isdir(path_c)

    # Remove c
    remove_empty_folders(path_c)
    assert not os.path.exists(path_c)
    assert not os.path.exists(path_b)
    assert not os.path.exists(path_a)

def test_remove_empty_folders_stops_at_content(test_dirs):
    # Create a/b/file
    path_a = os.path.join(str(test_dirs), "a_stuck")
    path_b = os.path.join(path_a, "b")
    os.makedirs(path_b, exist_ok=True)
    with open(os.path.join(path_b, "file.txt"), "w") as f: f.write("x")

    remove_empty_folders(path_b)
    # b should stay because file exists
    assert os.path.exists(path_b)

def test_synchronize_all_files_moves_incorrect_location(db_session, test_dirs):
    # Setup Data
    cat = "ANTINCENDIO"
    dip = Dipendente(nome="Mario", cognome="Rossi", matricola="123")
    corso = Corso(nome_corso="Corso A", categoria_corso=cat)
    cert = Certificato(
        dipendente=dip,
        corso=corso,
        data_rilascio=datetime.strptime("01/01/2020", "%d/%m/%Y").date(),
        data_scadenza_calcolata=datetime.strptime("01/01/2030", "%d/%m/%Y").date()
    )
    db_session.add(dip); db_session.add(corso); db_session.add(cert)
    db_session.commit(); db_session.refresh(cert)

    # Create File in WRONG location (e.g. STORICO but valid)
    nome_fs = sanitize_filename("Rossi Mario")
    matr_fs = sanitize_filename("123")
    cat_fs = sanitize_filename(cat)

    # Expected: .../ATTIVO/...
    # Create in: .../STORICO/...

    folder = os.path.join(str(test_dirs), "DOCUMENTI DIPENDENTI", f"{nome_fs} ({matr_fs})", cat_fs, "STORICO")
    os.makedirs(folder, exist_ok=True)
    filename = f"{nome_fs} ({matr_fs}) - {cat_fs} - 01_01_2030.pdf"
    wrong_path = os.path.join(folder, filename)
    with open(wrong_path, "w") as f: f.write("content")

    # Run Sync
    with mock.patch("app.services.file_maintenance.settings") as mock_settings:
        mock_settings.DATABASE_PATH = str(test_dirs)
        res = synchronize_all_files(db_session)

    assert res["moved"] == 1

    # Verify Moved to ATTIVO
    correct_folder = os.path.join(str(test_dirs), "DOCUMENTI DIPENDENTI", f"{nome_fs} ({matr_fs})", cat_fs, "ATTIVO")
    correct_path = os.path.join(correct_folder, filename)
    assert os.path.exists(correct_path)

    # Verify Old Folder Gone (Cleanup)
    assert not os.path.exists(folder)
