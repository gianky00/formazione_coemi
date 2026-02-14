import os
from datetime import datetime

from app.db.models import Certificato, Corso, ValidationStatus


def test_csv_import_moves_orphan_file(test_client, db_session, test_dirs):
    # 1. Setup Orphan Cert
    cat = "ANTINCENDIO"
    orphan_name = "Bianchi Mario"
    corso = Corso(nome_corso="Corso A", categoria_corso=cat, validita_mesi=0)
    cert = Certificato(
        dipendente_id=None,
        nome_dipendente_raw=orphan_name,
        corso=corso,
        data_rilascio=datetime.strptime("01/01/2020", "%d/%m/%Y").date(),
        data_scadenza_calcolata=datetime.strptime("01/01/2030", "%d/%m/%Y").date(),
        stato_validazione=ValidationStatus.MANUAL,
    )
    db_session.add(corso)
    db_session.add(cert)
    db_session.commit()

    # 2. Setup Physical File in 'DOCUMENTI DIPENDENTI' (where document_locator looks)
    # We use a path that find_document can find via deep search
    docs_dir = test_dirs / "DOCUMENTI DIPENDENTI" / "Bianchi Mario (N-A)" / "ANTINCENDIO" / "attivo"
    docs_dir.mkdir(parents=True, exist_ok=True)

    file_name = "Bianchi Mario (N-A) - ANTINCENDIO - 01012030.pdf"
    file_path = docs_dir / file_name
    file_path.write_bytes(b"%PDF-1.4 dummy")

    # Update cert with this path
    cert.file_path = str(file_path)
    db_session.commit()

    # 3. Import Employee via CSV (matches orphan)
    csv_content = "Cognome;Nome;Data_nascita;Badge\nBianchi;Mario;01/01/1980;M999"
    files = {"file": ("test.csv", csv_content.encode("utf-8"), "text/csv")}

    response = test_client.post("/dipendenti/import-csv", files=files)
    assert response.status_code == 200

    # 4. Verify DB Link
    db_session.refresh(cert)
    assert cert.dipendente_id is not None
    assert cert.dipendente.matricola == "M999"

    # 5. Verify File Move
    # In the current implementation of handle_file_rename, it moves to database_path / status
    # status for 2030 is 'attivo'
    new_name = "M999_Bianchi_Mario_ANTINCENDIO_01012030.pdf"
    expected_new_path = test_dirs / "attivo" / new_name

    assert os.path.exists(str(expected_new_path)), f"Expected file at {expected_new_path} not found"
    assert not os.path.exists(str(file_path))
