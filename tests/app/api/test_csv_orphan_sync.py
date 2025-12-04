import pytest
import os
import shutil
from datetime import datetime
from app.db.models import Certificato, Corso, Dipendente
from app.utils.file_security import sanitize_filename

def test_csv_import_moves_orphan_file(test_client, db_session, test_dirs):
    # 1. Setup Orphan Cert
    cat = "ANTINCENDIO"
    orphan_name = "Bianchi Mario"
    corso = Corso(nome_corso="Corso A", categoria_corso=cat)
    cert = Certificato(
        dipendente_id=None,
        nome_dipendente_raw=orphan_name,
        corso=corso,
        data_rilascio=datetime.strptime("01/01/2020", "%d/%m/%Y").date(),
        data_scadenza_calcolata=datetime.strptime("01/01/2030", "%d/%m/%Y").date()
    )
    db_session.add(corso)
    db_session.add(cert)
    db_session.commit()
    db_session.refresh(cert)

    # 2. Setup Orphan File
    # Folder: Bianchi Mario (N-A)
    # Filename: Bianchi Mario (N-A) - ANTINCENDIO - 01_01_2030.pdf
    safe_name = sanitize_filename(orphan_name)
    folder = os.path.join(str(test_dirs), "DOCUMENTI DIPENDENTI", f"{safe_name} (N-A)", cat, "ATTIVO")
    os.makedirs(folder, exist_ok=True)
    filename = f"{safe_name} (N-A) - {cat} - 01_01_2030.pdf"
    orphan_path = os.path.join(folder, filename)

    with open(orphan_path, "w") as f:
        f.write("content")

    assert os.path.exists(orphan_path)

    # 3. Create CSV Content
    # Cognome;Nome;Data_nascita;Badge;Data_assunzione
    csv_content = "Cognome;Nome;Data_nascita;Badge;Data_assunzione\nBianchi;Mario;;999;"

    # 4. Upload CSV
    response = test_client.post(
        "/dipendenti/import-csv",
        files={"file": ("test.csv", csv_content, "text/csv")}
    )
    assert response.status_code == 200
    assert "1 certificati orfani collegati" in response.json()["message"]

    # 5. Verify DB Link
    db_session.refresh(cert)
    assert cert.dipendente_id is not None
    assert cert.dipendente.matricola == "999"

    # 6. Verify File Move
    # Old path should be gone
    assert not os.path.exists(orphan_path), "Old orphan file should be moved"

    # New path should exist
    # Bianchi Mario (999)
    new_folder = os.path.join(str(test_dirs), "DOCUMENTI DIPENDENTI", "Bianchi Mario (999)", cat, "ATTIVO")
    new_filename = f"Bianchi Mario (999) - {cat} - 01_01_2030.pdf"
    new_path = os.path.join(new_folder, new_filename)

    assert os.path.exists(new_path), f"New file not found at {new_path}"
