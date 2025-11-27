import io
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models import Certificato, Corso
from datetime import date

def test_csv_import_links_orphaned_certificates(test_client: TestClient, db_session: Session):
    """
    Tests that importing a CSV of employees will successfully link existing
    orphaned certificates to the newly imported employees.
    """
    # 1. Create a course and an orphaned certificate via the API
    course = Corso(nome_corso="Orphan Test Course", validita_mesi=24, categoria_corso="ORPHAN")
    db_session.add(course)
    db_session.commit()

    cert_payload = {
        "nome": "Luigi Verdi",
        "corso": "Orphan Test Course",
        "categoria": "ORPHAN",
        "data_rilascio": "15/05/2023",
    }
    response = test_client.post("/api/v1/certificati/", json=cert_payload)
    assert response.status_code == 200
    cert_id = response.json()["id"]

    # Verify the certificate is initially orphaned
    cert = db_session.get(Certificato, cert_id)
    assert cert is not None
    assert cert.dipendente_id is None
    assert cert.nome_dipendente_raw == "Luigi Verdi"

    # 2. Import a CSV file containing the employee's data
    csv_content = (
        "Cognome;Nome;Data_nascita;Badge\n"
        "Verdi;Luigi;01/01/1990;LV001"
    ).encode('utf-8')
    
    files = {"file": ("employees.csv", io.BytesIO(csv_content), "text/csv")}
    response = test_client.post("/api/v1/dipendenti/import-csv", files=files)
    
    # 3. Verify the import was successful and the orphan was linked
    assert response.status_code == 200
    assert "1 certificati orfani collegati" in response.json()["message"]

    # 4. Verify the certificate in the database is now linked to the new employee
    db_session.refresh(cert)
    assert cert.dipendente_id is not None
    assert cert.dipendente.matricola == "LV001"
    assert cert.dipendente.nome == "Luigi"
    assert cert.dipendente.cognome == "Verdi"
