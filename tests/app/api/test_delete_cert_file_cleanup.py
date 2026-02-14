import os
from datetime import datetime

from app.db.models import Certificato, Corso, Dipendente, ValidationStatus


def test_delete_certificate_deletes_file(test_client, db_session, test_dirs):
    # 1. Setup Data in DB
    cat = "ANTINCENDIO"
    dip = Dipendente(nome="Mario", cognome="Rossi", matricola="123")
    corso = Corso(nome_corso="Corso A", categoria_corso=cat, validita_mesi=0)
    cert = Certificato(
        dipendente=dip,
        corso=corso,
        data_rilascio=datetime.strptime("01/01/2020", "%d/%m/%Y").date(),
        data_scadenza_calcolata=datetime.strptime("01/01/2025", "%d/%m/%Y").date(),
        stato_validazione=ValidationStatus.MANUAL,
    )

    db_session.add(dip)
    db_session.add(corso)
    db_session.add(cert)
    db_session.commit()

    # 2. Setup Physical File in a place find_document can reach
    # We use the DOCUMENTI DIPENDENTI structure
    docs_dir = test_dirs / "DOCUMENTI DIPENDENTI" / "Rossi Mario (123)" / "ANTINCENDIO"
    docs_dir.mkdir(parents=True, exist_ok=True)

    file_path = docs_dir / "Rossi Mario (123) - ANTINCENDIO - 01012025.pdf"
    file_path.write_bytes(b"%PDF-1.4 dummy content")

    # Update cert with the file path
    cert.file_path = str(file_path)
    db_session.commit()

    # 3. Call Delete API
    response = test_client.delete(f"/certificati/{cert.id}")
    assert response.status_code == 200

    # 4. Verify DB deletion
    deleted_cert = db_session.get(Certificato, cert.id)
    assert deleted_cert is None

    # 5. Verify physical file is GONE from original location
    assert not os.path.exists(str(file_path))
