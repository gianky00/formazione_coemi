import pytest
import os
from datetime import datetime
from app.db.models import Certificato, Corso, Dipendente
from app.utils.file_security import sanitize_filename
from unittest.mock import patch

def test_delete_certificate_deletes_file(test_client, db_session, test_dirs):
    # 1. Setup Data in DB
    cat = "ANTINCENDIO"
    dip = Dipendente(nome="Mario", cognome="Rossi", matricola="123")
    corso = Corso(nome_corso="Corso A", categoria_corso=cat)
    cert = Certificato(
        dipendente=dip,
        corso=corso,
        data_rilascio=datetime.strptime("01/01/2020", "%d/%m/%Y").date(),
        data_scadenza_calcolata=datetime.strptime("01/01/2025", "%d/%m/%Y").date()
    )

    db_session.add(dip)
    db_session.add(corso)
    db_session.add(cert)
    db_session.commit()
    db_session.refresh(cert)

    cert_id = cert.id

    # 2. Setup File on Disk
    # Full name: Rossi Mario
    nome_fs = sanitize_filename("Rossi Mario")
    matr_fs = sanitize_filename("123")
    cat_fs = sanitize_filename(cat)

    # Assuming "ATTIVO" status. document_locator searches all statuses so exact folder matters less,
    # but let's put it in ATTIVO for realism.
    folder = os.path.join(str(test_dirs), "DOCUMENTI DIPENDENTI", f"{nome_fs} ({matr_fs})", cat_fs, "ATTIVO")
    os.makedirs(folder, exist_ok=True)

    filename = f"{nome_fs} ({matr_fs}) - {cat_fs} - 01_01_2025.pdf"
    file_path = os.path.join(folder, filename)

    with open(file_path, "w") as f:
        f.write("dummy content")

    assert os.path.exists(file_path)

    # 3. Call Delete API
    # Patch shutil.move (since deletion implies moving to trash in this system)
    with patch("shutil.move") as mock_move:
        response = test_client.delete(f"/certificati/{cert_id}")
    
    assert response.status_code == 200

    # 4. Verify DB deletion
    assert db_session.get(Certificato, cert_id) is None

    # 5. Verify File Move to Trash
    mock_move.assert_called()
    args = mock_move.call_args[0]
    # Check that destination has CESTINO
    assert "CESTINO" in args[1]
