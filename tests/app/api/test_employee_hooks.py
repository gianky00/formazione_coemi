import pytest
import os
from datetime import datetime
from app.db.models import Certificato, Corso, Dipendente
from app.utils.file_security import sanitize_filename

def test_create_employee_links_orphan(test_client, db_session, test_dirs):
    # Setup Orphan Cert
    cat = "ANTINCENDIO"
    orphan_name = "Mario Rossi"
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

    # Setup Orphan File
    # Folder: Mario Rossi (N-A)
    safe_name = sanitize_filename(orphan_name)
    folder = os.path.join(str(test_dirs), "DOCUMENTI DIPENDENTI", f"{safe_name} (N-A)", cat, "ATTIVO")
    os.makedirs(folder, exist_ok=True)
    filename = f"{safe_name} (N-A) - {cat} - 01_01_2030.pdf"
    orphan_path = os.path.join(folder, filename)
    with open(orphan_path, "w") as f: f.write("content")

    # Create Employee via API
    # Note: Matcher looks for "Rossi Mario" if input is "Mario Rossi" or vice versa.
    # API input: nome="Mario", cognome="Rossi".
    # Employee name in DB will be "Rossi Mario" (usually surname first in many systems, but here separated).
    # construct_path uses `f"{dip.cognome} {dip.nome}"`.
    # So "Rossi Mario".
    payload = {
        "nome": "Mario",
        "cognome": "Rossi",
        "matricola": "123"
    }
    response = test_client.post("/dipendenti/", json=payload)
    assert response.status_code == 200

    # Verify Link
    db_session.refresh(cert)
    assert cert.dipendente_id is not None
    assert cert.dipendente.matricola == "123"

    # Verify File Move
    # New folder: Rossi Mario (123)
    new_folder = os.path.join(str(test_dirs), "DOCUMENTI DIPENDENTI", "Rossi Mario (123)", cat, "ATTIVO")
    new_path = os.path.join(new_folder, f"Rossi Mario (123) - {cat} - 01_01_2030.pdf")

    if not os.path.exists(new_path):
        import subprocess
        print("\n--- DEBUG FILE STRUCTURE ---")
        root = os.path.join(str(test_dirs), "DOCUMENTI DIPENDENTI")
        for dirpath, dirnames, filenames in os.walk(root):
            for f in filenames:
                print(os.path.join(dirpath, f))
        print("----------------------------\n")

    assert os.path.exists(new_path)
    assert not os.path.exists(orphan_path)
