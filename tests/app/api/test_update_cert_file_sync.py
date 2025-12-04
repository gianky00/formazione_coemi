import pytest
import os
from datetime import datetime
from app.db.models import Certificato, Corso, Dipendente
from app.utils.file_security import sanitize_filename

def test_update_certificate_moves_file(test_client, db_session, test_dirs):
    # Setup
    cat = "ANTINCENDIO"
    dip = Dipendente(nome="Mario", cognome="Rossi", matricola="123")
    dip2 = Dipendente(nome="Luigi", cognome="Verdi", matricola="456")
    corso = Corso(nome_corso="Corso A", categoria_corso=cat)
    # Use future date to ensure status is ATTIVO
    cert = Certificato(
        dipendente=dip,
        corso=corso,
        data_rilascio=datetime.strptime("01/01/2020", "%d/%m/%Y").date(),
        data_scadenza_calcolata=datetime.strptime("01/01/2030", "%d/%m/%Y").date()
    )
    db_session.add(dip); db_session.add(dip2); db_session.add(corso); db_session.add(cert)
    db_session.commit(); db_session.refresh(cert)

    # Create File for Mario
    nome_fs = sanitize_filename("Rossi Mario")
    matr_fs = sanitize_filename("123")
    cat_fs = sanitize_filename(cat)
    folder = os.path.join(str(test_dirs), "DOCUMENTI DIPENDENTI", f"{nome_fs} ({matr_fs})", cat_fs, "ATTIVO")
    os.makedirs(folder, exist_ok=True)
    filename = f"{nome_fs} ({matr_fs}) - {cat_fs} - 01_01_2030.pdf"
    old_path = os.path.join(folder, filename)
    with open(old_path, "w") as f: f.write("content")

    # Update cert to point to Luigi
    payload = {"nome": "Verdi Luigi"}
    response = test_client.put(f"/certificati/{cert.id}", json=payload)
    assert response.status_code == 200

    # Check File Moved
    assert not os.path.exists(old_path), "Old file should be gone"

    # Check New File
    new_folder = os.path.join(str(test_dirs), "DOCUMENTI DIPENDENTI", "Verdi Luigi (456)", cat_fs, "ATTIVO")
    new_filename = f"Verdi Luigi (456) - {cat_fs} - 01_01_2030.pdf"
    new_path = os.path.join(new_folder, new_filename)

    if not os.path.exists(new_path):
        import subprocess
        print("\n--- DEBUG FILE STRUCTURE ---")
        root = os.path.join(str(test_dirs), "DOCUMENTI DIPENDENTI")
        for dirpath, dirnames, filenames in os.walk(root):
            for f in filenames:
                print(os.path.join(dirpath, f))
        print("----------------------------\n")

    assert os.path.exists(new_path), f"New file not found at {new_path}"
