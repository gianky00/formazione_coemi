import os
from datetime import datetime

from app.db.models import Certificato, Corso, Dipendente, ValidationStatus


def test_realtime_archiving_on_create(test_client, db_session, test_dirs):
    # Setup Data
    cat = "ANTINCENDIO"
    dip = Dipendente(nome="Mario", cognome="Rossi", matricola="123")
    corso = Corso(nome_corso="Corso A", categoria_corso=cat, validita_mesi=60)

    # Old cert (Valid but old)
    cert_old = Certificato(
        dipendente=dip,
        corso=corso,
        data_rilascio=datetime.strptime("01/01/2020", "%d/%m/%Y").date(),
        data_scadenza_calcolata=datetime.strptime("01/01/2025", "%d/%m/%Y").date(),
        stato_validazione=ValidationStatus.MANUAL,
    )
    db_session.add(dip)
    db_session.add(corso)
    db_session.add(cert_old)
    db_session.commit()

    # Create dummy file for old cert
    # Structure must match find_document expectations or the manual file_path
    docs_dir = test_dirs / "DOCUMENTI DIPENDENTI" / "Rossi Mario (123)" / "ANTINCENDIO" / "attivo"
    docs_dir.mkdir(parents=True, exist_ok=True)
    file_path = docs_dir / "old_cert.pdf"
    file_path.write_bytes(b"%PDF-1.4 old content")
    cert_old.file_path = str(file_path)
    db_session.commit()

    # 2. Create NEW certificate for same person and course via API
    payload = {
        "nome": "Mario Rossi",
        "corso": "Corso A",
        "categoria": cat,
        "data_rilascio": "01/01/2024",
        "data_scadenza": "01/01/2029",
    }
    response = test_client.post("/certificati/", json=payload)
    assert response.status_code == 200

    # 3. Verify old file was MOVED to 'STORICO'
    # We check if the file still exists in the original location
    # Note: archive_certificate_file in sync_service might move it or just rename it.
    # Currently it moves to construct_certificate_path(status="STORICO")
    assert not os.path.exists(str(file_path))

    # Verify the new file location (STORICO)
    # The actual folder should be .../ANTINCENDIO/STORICO/...
    storico_dir = (
        test_dirs / "DOCUMENTI DIPENDENTI" / "Rossi Mario (123)" / "ANTINCENDIO" / "STORICO"
    )
    assert storico_dir.exists()
    assert len(list(storico_dir.glob("*.pdf"))) >= 1


def test_realtime_archiving_on_update(test_client, db_session, test_dirs):
    # Setup similar to create
    pass
