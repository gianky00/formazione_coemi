import os
from datetime import datetime

from app.db.models import Certificato, Corso, Dipendente, ValidationStatus


def test_update_certificate_moves_file(test_client, db_session, test_dirs):
    # Setup
    cat = "ANTINCENDIO"
    dip = Dipendente(nome="Mario", cognome="Rossi", matricola="123")
    dip2 = Dipendente(nome="Luigi", cognome="Verdi", matricola="456")
    corso = Corso(nome_corso="Corso A", categoria_corso=cat, validita_mesi=60)

    # Use future date to ensure status is ATTIVO
    cert = Certificato(
        dipendente=dip,
        corso=corso,
        data_rilascio=datetime.strptime("01/01/2020", "%d/%m/%Y").date(),
        data_scadenza_calcolata=datetime.strptime("01/01/2030", "%d/%m/%Y").date(),
        stato_validazione=ValidationStatus.MANUAL,
    )
    db_session.add(dip)
    db_session.add(dip2)
    db_session.add(corso)
    db_session.add(cert)
    db_session.commit()

    # 2. Setup Physical File
    # EXACT name and path constructed by construct_certificate_path for Rossi Mario (123)
    # Note: _format_file_scadenza produces '01012030'
    docs_dir = test_dirs / "DOCUMENTI DIPENDENTI" / "Rossi Mario (123)" / "ANTINCENDIO" / "ATTIVO"
    docs_dir.mkdir(parents=True, exist_ok=True)

    file_name = "Rossi Mario (123) - ANTINCENDIO - 01012030.pdf"
    file_path = docs_dir / file_name
    file_path.write_bytes(b"%PDF-1.4 dummy content")

    cert.file_path = str(file_path)
    db_session.commit()

    # 3. Update Certificate (Change Employee to Luigi Verdi)
    update_payload = {
        "nome": "Luigi Verdi",
        "corso": "Corso A",
        "categoria": cat,
        "data_rilascio": "01/01/2020",
        "data_scadenza": "01/01/2030",
    }
    response = test_client.put(f"/certificati/{cert.id}", json=update_payload)
    assert response.status_code == 200

    # 4. Verify DB Link changed
    db_session.refresh(cert)
    assert cert.dipendente_id == dip2.id

    # 5. Verify File Move
    # Name built by handle_file_rename: parts [456, "Verdi Luigi", "ANTINCENDIO", "01012030"]
    # Separator is "_"
    new_name = "456_Verdi_Luigi_ANTINCENDIO_01012030.pdf"
    expected_new_path = (
        test_dirs
        / "DOCUMENTI DIPENDENTI"
        / "Verdi Luigi (456)"
        / "ANTINCENDIO"
        / "ATTIVO"
        / new_name
    )

    if not os.path.exists(str(expected_new_path)):
        # List all files in test_dirs to see what actually happened
        all_files = []
        for root, _dirs, files in os.walk(str(test_dirs)):
            all_files.extend(os.path.join(root, f) for f in files)
        raise AssertionError(
            f"Expected file not found at {expected_new_path}. Actual files in system: {all_files}"
        )

    assert not os.path.exists(str(file_path))


def test_update_certificate_rollback_on_db_error(test_client, db_session, test_dirs, mocker):
    pass
