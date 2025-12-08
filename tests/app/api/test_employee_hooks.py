import pytest
import os
from datetime import datetime
from app.db.models import Certificato, Corso, Dipendente
from app.utils.file_security import sanitize_filename
from unittest.mock import patch

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
    payload = {
        "nome": "Mario",
        "cognome": "Rossi",
        "matricola": "123"
    }
    
    # Patch shutil.move
    with patch("shutil.move") as mock_move:
        response = test_client.post("/dipendenti/", json=payload)
    
    assert response.status_code == 200

    # Verify Link
    db_session.refresh(cert)
    assert cert.dipendente_id is not None
    assert cert.dipendente.matricola == "123"

    # Since we mocked move, we verify move was called.
    mock_move.assert_called()
    
    # We can inspect call args to ensure correct paths.
    args = mock_move.call_args[0]
    src, dst = args[0], args[1]
    assert "Mario Rossi (N-A)" in src or "Mario Rossi (N-A)" in os.path.normpath(src) # Depending on normalization
    assert "Rossi Mario (123)" in dst
