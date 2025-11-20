import io
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models import Certificato, Corso, ValidationStatus
from datetime import date

def test_csv_import_links_orphaned_certificates(test_client: TestClient, db_session: Session):
    # 1. Create an orphaned certificate
    # First ensure the course exists
    course = Corso(nome_corso="Corso Test", validita_mesi=12, categoria_corso="TEST")
    db_session.add(course)
    db_session.commit()

    cert_data = {
        "nome": "Mario Rossi",
        "corso": "Corso Test",
        "categoria": "TEST",
        "data_rilascio": "01/01/2023",
        "data_scadenza": "01/01/2024"
    }
    response = test_client.post("/certificati/", json=cert_data)
    assert response.status_code == 200
    cert_id = response.json()["id"]

    # Verify it is orphaned
    cert = db_session.get(Certificato, cert_id)
    assert cert.dipendente_id is None
    assert cert.nome_dipendente_raw == "Mario Rossi"

    # 2. Import CSV with the employee
    csv_content = b"Cognome;Nome;Data_nascita;Badge\nRossi;Mario;01/01/1980;12345"
    files = {"file": ("dipendenti.csv", io.BytesIO(csv_content), "text/csv")}

    response = test_client.post("/dipendenti/import-csv", files=files)
    assert response.status_code == 200

    # 3. Verify the certificate is now linked
    db_session.refresh(cert)
    assert cert.dipendente_id is not None
    assert cert.dipendente.matricola == "12345"
    assert cert.dipendente.nome == "Mario"
    assert cert.dipendente.cognome == "Rossi"
