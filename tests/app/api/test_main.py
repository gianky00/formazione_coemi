import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models import Dipendente, Corso, Certificato
from datetime import date

# The test_client fixture is now imported from conftest.py
# It comes pre-configured with a clean DB, mocked settings, and auth overrides.

@pytest.fixture(autouse=True)
def seed_master_courses(db_session: Session):
    """Fixture to auto-seed necessary courses for all tests in this file."""
    corsi = [
        {"nome_corso": "ANTINCENDIO", "validita_mesi": 60, "categoria_corso": "ANTINCENDIO"},
        {"nome_corso": "PRIMO SOCCORSO", "validita_mesi": 36, "categoria_corso": "PRIMO SOCCORSO"},
        {"nome_corso": "VISITA MEDICA", "validita_mesi": 0, "categoria_corso": "VISITA MEDICA"},
        {"nome_corso": "General", "validita_mesi": 12, "categoria_corso": "General"},
    ]
    for corso_data in corsi:
        if not db_session.query(Corso).filter_by(categoria_corso=corso_data["categoria_corso"]).first():
            db_session.add(Corso(**corso_data))
    db_session.commit()

def test_create_and_get_certificato(test_client: TestClient, db_session: Session):
    """Tests successful creation and retrieval of a linked certificate."""
    db_session.add(Dipendente(nome="Mario", cognome="Rossi", matricola="M01"))
    db_session.commit()
    
    cert_data = {
        "nome": "Mario Rossi", "corso": "Test Antincendio", "categoria": "ANTINCENDIO",
        "data_rilascio": "14/11/2025"
    }
    response = test_client.post("/api/v1/certificati/", json=cert_data)
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Rossi Mario"
    assert data["matricola"] == "M01"
    assert data["corso"] == "Test Antincendio"
    assert data["validated"] is False

    # Verify it can be retrieved
    response_get = test_client.get(f"/api/v1/certificati/{data['id']}")
    assert response_get.status_code == 200
    assert response_get.json()["nome"] == "Rossi Mario"

def test_get_certificati_filtering(test_client: TestClient, db_session: Session):
    """Tests filtering certificates by validation status."""
    corso = db_session.query(Corso).filter_by(categoria_corso="General").one()
    
    # Create one validated and one unvalidated certificate
    db_session.add(Certificato(corso_id=corso.id, data_rilascio=date(2023,1,1), validated=True))
    db_session.add(Certificato(corso_id=corso.id, data_rilascio=date(2023,1,2), validated=False))
    db_session.commit()

    # Get validated
    response_true = test_client.get("/api/v1/certificati/?validated=true")
    assert response_true.status_code == 200
    assert len(response_true.json()) == 1
    assert response_true.json()[0]["validated"] is True

    # Get unvalidated
    response_false = test_client.get("/api/v1/certificati/?validated=false")
    assert response_false.status_code == 200
    assert len(response_false.json()) == 1
    assert response_false.json()[0]["validated"] is False

def test_update_certificato(test_client: TestClient, db_session: Session):
    """Tests updating an existing certificate's course and validation status."""
    cert = Certificato(
        dipendente=Dipendente(nome="Test", cognome="User", matricola="T01"),
        corso=db_session.query(Corso).filter_by(categoria_corso="General").one(),
        data_rilascio=date(2025, 1, 1), validated=False
    )
    db_session.add(cert)
    db_session.commit()

    update_payload = {"corso": "Updated Course Name"}
    response = test_client.put(f"/api/v1/certificati/{cert.id}", json=update_payload)
    assert response.status_code == 200
    
    db_session.refresh(cert)
    assert cert.corso.nome_corso == "Updated Course Name"
    assert cert.validated is True # Updates should automatically validate

def test_create_duplicate_certificato_fails(test_client: TestClient, db_session: Session):
    """Tests that creating a duplicate certificate for the same employee fails."""
    dipendente = Dipendente(nome="Duplicate", cognome="Test", matricola="D01")
    db_session.add(dipendente)
    db_session.commit()

    cert_data = {
        "nome": "Duplicate Test", "corso": "Duplicate Course", "categoria": "General",
        "data_rilascio": "01/01/2025"
    }
    # First creation should succeed
    assert test_client.post("/api/v1/certificati/", json=cert_data).status_code == 200
    # Second attempt should fail
    response = test_client.post("/api/v1/certificati/", json=cert_data)
    assert response.status_code == 409

def test_upload_pdf_and_ai_mocking(test_client: TestClient, mocker):
    """Tests PDF upload with a mocked AI response."""
    mock_ai = mocker.patch("app.api.main.ai_extraction.extract_entities_with_ai")
    mock_ai.return_value = {
        "nome": "Mario Rossi", "corso": "Corso Sicurezza Mock", "categoria": "ANTINCENDIO",
        "data_rilascio": "10-10-2025"
    }
    
    response = test_client.post("/api/v1/upload-pdf/", files={"file": ("mock.pdf", b"%PDF-mock", "application/pdf")})
    assert response.status_code == 200
    entities = response.json()["entities"]
    assert entities["corso"] == "Corso Sicurezza Mock"
    # Check that date format was corrected
    assert entities["data_rilascio"] == "10/10/2025"
    # Check that expiration date was calculated
    assert "data_scadenza" in entities
