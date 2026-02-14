from datetime import datetime

from app.db.models import Certificato, Corso, ValidationStatus


def test_create_employee_links_orphan(test_client, db_session, test_dirs):
    # 1. Setup Orphan Cert in DB
    cat = "ANTINCENDIO"
    orphan_name = "Mario Rossi"
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

    # 2. Create Employee via API (triggers hook/logic in router)
    payload = {
        "nome": "Mario",
        "cognome": "Rossi",
        "matricola": "M123",
        "data_nascita": "1980-01-01",
    }
    response = test_client.post("/dipendenti", json=payload)
    assert response.status_code == 200
    emp_id = response.json()["id"]

    # 3. Verify cert is linked
    db_session.refresh(cert)
    assert cert.dipendente_id == emp_id
    assert cert.dipendente.matricola == "M123"
