import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models import Dipendente, Corso, Certificato, ValidationStatus
from datetime import date

def seed_master_courses(db: Session):
    """Helper to seed master courses for tests."""
    corsi = [
        {"nome_corso": "ANTINCENDIO", "validita_mesi": 60, "categoria_corso": "ANTINCENDIO"},
        {"nome_corso": "PRIMO SOCCORSO", "validita_mesi": 36, "categoria_corso": "PRIMO SOCCORSO"},
        {"nome_corso": "VISITA MEDICA", "validita_mesi": 0, "categoria_corso": "VISITA MEDICA"},
        {"nome_corso": "ALTRO", "validita_mesi": 0, "categoria_corso": "ALTRO"},
        {"nome_corso": "General", "validita_mesi": 12, "categoria_corso": "General"},
    ]
    for corso_data in corsi:
        if not db.query(Corso).filter_by(nome_corso=corso_data["nome_corso"]).first():
            db.add(Corso(**corso_data))
    db.commit()

def test_create_certificato(test_client: TestClient, db_session: Session):
    """Tests successful certificate creation."""
    seed_master_courses(db_session)
    db_session.add(Dipendente(nome="Mario", cognome="Rossi"))
    db_session.commit()
    cert_data = {
        "nome": "Mario Rossi", "corso": "ANTINCENDIO", "categoria": "ANTINCENDIO",
        "data_rilascio": "14/11/2025", "data_scadenza": "14/11/2030"
    }
    response = test_client.post("/certificati/", json=cert_data)
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Rossi Mario"
    cert_db = db_session.get(Certificato, data["id"])
    assert cert_db and cert_db.stato_validazione == ValidationStatus.AUTOMATIC

def test_validate_certificato(test_client: TestClient, db_session: Session):
    """Tests manual validation of a certificate."""
    seed_master_courses(db_session)
    cert = Certificato(
        dipendente=Dipendente(nome="Jane", cognome="Doe"),
        corso=db_session.query(Corso).filter_by(nome_corso="PRIMO SOCCORSO").one(),
        data_rilascio=date(2025, 11, 14), stato_validazione=ValidationStatus.AUTOMATIC
    )
    db_session.add(cert)
    db_session.commit()
    response = test_client.put(f"/certificati/{cert.id}/valida")
    assert response.status_code == 200
    db_session.refresh(cert)
    assert cert.stato_validazione == ValidationStatus.MANUAL

def test_update_certificato(test_client: TestClient, db_session: Session):
    """Tests updating an existing certificate."""
    seed_master_courses(db_session)
    cert = Certificato(
        dipendente=Dipendente(nome="Test", cognome="User"),
        corso=db_session.query(Corso).filter_by(nome_corso="General").one(),
        data_rilascio=date(2025, 1, 1), stato_validazione=ValidationStatus.MANUAL
    )
    db_session.add(cert)
    db_session.commit()
    update_payload = {
        "nome": "Test User", "corso": "Updated Course", "categoria": "General",
        "data_rilascio": "01/02/2025", "data_scadenza": "01/02/2026"
    }
    response = test_client.put(f"/certificati/{cert.id}", json=update_payload)
    assert response.status_code == 200
    db_session.refresh(cert)
    assert cert.corso.nome_corso == "Updated Course"

def test_update_certificato_disassociates_employee(test_client: TestClient, db_session: Session):
    """Tests that updating a certificate with a non-existent employee disassociates it."""
    seed_master_courses(db_session)
    cert = Certificato(
        dipendente=Dipendente(nome="Old", cognome="Employee"),
        corso=db_session.query(Corso).filter_by(nome_corso="General").one(),
        data_rilascio=date(2025, 1, 1)
    )
    db_session.add(cert)
    db_session.commit()
    update_data = {
        "nome": "Non Existent Employee", "corso": "New Course", "categoria": "General",
        "data_rilascio": "01/03/2025", "data_scadenza": "01/03/2026"
    }
    response = test_client.put(f"/certificati/{cert.id}", json=update_data)
    assert response.status_code == 200
    db_session.refresh(cert)
    assert cert.dipendente_id is None
    assert db_session.query(Corso).filter_by(nome_corso="New Course").one()

def test_create_duplicate_certificato_fails(test_client: TestClient, db_session: Session):
    """Tests that creating a duplicate certificate fails."""
    seed_master_courses(db_session)
    cert_data = {
        "nome": "Mario Rossi", "corso": "Corso Duplicato", "categoria": "ALTRO",
        "data_rilascio": "01/01/2025", "data_scadenza": "01/01/2026"
    }
    assert test_client.post("/certificati/", json=cert_data).status_code == 200
    response = test_client.post("/certificati/", json=cert_data)
    assert response.status_code == 409

def test_upload_pdf_visita_medica(test_client: TestClient, db_session: Session, mocker):
    """Tests PDF upload for a 'VISITA MEDICA' with a direct expiration date."""
    seed_master_courses(db_session)
    mocker.patch("app.api.main.ai_extraction.extract_entities_with_ai", return_value={
        "nome": "Mario Rossi", "corso": "Giudizio di idoneità", "categoria": "VISITA MEDICA",
        "data_rilascio": "10-10-2025", "data_scadenza": "10-10-2026"
    })
    # Must include %PDF- header to pass signature check
    response = test_client.post("/upload-pdf/", files={"file": ("v.pdf", b"%PDF-1.4 fake content", "application/pdf")})
    assert response.status_code == 200
    assert response.json()["entities"]["data_scadenza"] == "10/10/2026"

@pytest.mark.parametrize("payload_override, expected_status, detail", [
    ({"data_rilascio": ""}, 422, "La data di rilascio non può essere vuota."),
    ({"data_rilascio": "14-11-2025"}, 422, "Formato data non valido"),
    ({"nome": ""}, 422, "String should have at least 1 character"),
    ({"nome": "Mario"}, 400, "Formato nome non valido"),
])
def test_create_certificato_invalid_payload(test_client: TestClient, db_session: Session, payload_override, expected_status, detail):
    """Tests that creating a certificate with invalid data fails as expected."""
    seed_master_courses(db_session)
    payload = {
        "nome": "Mario Rossi", "corso": "Corso Base", "categoria": "ANTINCENDIO",
        "data_rilascio": "14/11/2025", "data_scadenza": "14/11/2030"
    }
    payload.update(payload_override)
    response = test_client.post("/certificati/", json=payload)
    assert response.status_code == expected_status
    assert detail in str(response.json().get("detail", ""))

@pytest.mark.parametrize("scadenza_in, db_out, resp_out", [
    ("15/12/2030", date(2030, 12, 15), "15/12/2030"), (None, None, None),
    ("", None, None), ("None", None, None), ("none", None, None)
])
def test_update_data_scadenza_variations(test_client: TestClient, db_session: Session, scadenza_in, db_out, resp_out):
    """Tests updating the expiration date with various null-like values."""
    seed_master_courses(db_session)
    cert = Certificato(
        dipendente=Dipendente(nome="Jane", cognome="Doe"),
        corso=db_session.query(Corso).filter_by(nome_corso="General").one(),
        data_rilascio=date(2025, 1, 1)
    )
    db_session.add(cert)
    db_session.commit()
    payload = {
        "nome": "Jane Doe", "corso": "Test Course", "categoria": "General",
        "data_rilascio": "01/01/2025", "data_scadenza": scadenza_in
    }
    response = test_client.put(f"/certificati/{cert.id}", json=payload)
    assert response.status_code == 200
    db_session.refresh(cert)
    assert cert.data_scadenza_calcolata == db_out
    assert response.json()["data_scadenza"] == resp_out

def test_upload_pdf(test_client: TestClient, db_session: Session, mocker):
    """Tests PDF upload and expiration date calculation."""
    seed_master_courses(db_session)
    mocker.patch("app.api.main.ai_extraction.extract_entities_with_ai", return_value={
        "nome": "Mario Rossi", "corso": "Corso Sicurezza", "categoria": "ANTINCENDIO",
        "data_rilascio": "10-10-2025"
    })
    # Must include %PDF- header to pass signature check
    response = test_client.post("/upload-pdf/", files={"file": ("t.pdf", b"%PDF-1.4 fake content", "application/pdf")})
    assert response.status_code == 200
    assert "data_scadenza" in response.json()["entities"]

def test_get_certificati_includes_orphaned(test_client: TestClient, db_session: Session):
    """Tests that orphaned certificates are returned when validated=false."""
    seed_master_courses(db_session)
    corso = db_session.query(Corso).filter_by(nome_corso="General").one()

    # Create an orphaned certificate
    orphaned_cert = Certificato(
        dipendente_id=None,
        corso_id=corso.id,
        data_rilascio=date(2025, 1, 1),
        stato_validazione=ValidationStatus.AUTOMATIC
    )
    db_session.add(orphaned_cert)
    db_session.commit()

    response = test_client.get("/certificati/?validated=false")
    assert response.status_code == 200
    data = response.json()

    # Check if the orphaned certificate is in the response
    found = any(cert['id'] == orphaned_cert.id and cert['nome'] == "DA ASSEGNARE" for cert in data)
    assert found, "Orphaned certificate not found in the response for unvalidated certificates"

    # Also check that it's NOT in the validated list
    response_validated = test_client.get("/certificati/?validated=true")
    assert response_validated.status_code == 200
    data_validated = response_validated.json()
    found_validated = any(cert['id'] == orphaned_cert.id for cert in data_validated)
    assert not found_validated, "Orphaned certificate should not be in the response for validated certificates"

def test_duplicate_check_for_orphaned_certs(test_client: TestClient, db_session: Session):
    """Tests that duplicate check for orphaned certs is based on the raw name."""
    seed_master_courses(db_session)

    # Create first orphaned certificate
    cert_data1 = {
        "nome": "Orphan One", "corso": "Orphan Course", "categoria": "ALTRO",
        "data_rilascio": "10/10/2025", "data_scadenza": None
    }
    response1 = test_client.post("/certificati/", json=cert_data1)
    assert response1.status_code == 200

    # Create second orphaned certificate for a DIFFERENT person, but same course/date
    cert_data2 = {
        "nome": "Orphan Two", "corso": "Orphan Course", "categoria": "ALTRO",
        "data_rilascio": "10/10/2025", "data_scadenza": None
    }
    response2 = test_client.post("/certificati/", json=cert_data2)
    assert response2.status_code == 200, "Should be able to create certs for different people"

    # Attempt to create a TRUE duplicate of the first certificate
    response3 = test_client.post("/certificati/", json=cert_data1)
    assert response3.status_code == 409, "Should NOT be able to create a true duplicate"

def test_orphaned_certificate_retains_raw_data(test_client: TestClient, db_session: Session):
    """Tests that an orphaned certificate retains and displays the raw extracted data."""
    seed_master_courses(db_session)

    # Data for a person not in the DB
    raw_name = "Francesco Fimmano"
    raw_birth_date = "30/05/1964"

    cert_data = {
        "nome": raw_name,
        "data_nascita": raw_birth_date,
        "corso": "ATEX",
        "categoria": "ATEX",
        "data_rilascio": "18/02/2015",
        "data_scadenza": "18/02/2020"
    }

    # Create the certificate
    response_create = test_client.post("/certificati/", json=cert_data)
    assert response_create.status_code == 200
    created_cert_id = response_create.json()["id"]

    # Verify it is stored correctly in the database
    db_cert = db_session.get(Certificato, created_cert_id)
    assert db_cert is not None
    assert db_cert.dipendente_id is None  # Should be orphaned
    assert db_cert.nome_dipendente_raw == raw_name
    assert db_cert.data_nascita_raw == raw_birth_date

    # Verify the API returns the raw data for the unvalidated list
    response_get = test_client.get("/certificati/?validated=false")
    assert response_get.status_code == 200

    found_cert = None
    for cert in response_get.json():
        if cert["id"] == created_cert_id:
            found_cert = cert
            break

    assert found_cert is not None, "Orphaned certificate not found in API response"
    assert found_cert["nome"] == raw_name
    assert found_cert["data_nascita"] == raw_birth_date

def test_api_returns_failure_reason_for_orphaned_certs(test_client: TestClient, db_session: Session):
    """Tests that the API returns a reason for assignment failure for orphaned certs."""
    seed_master_courses(db_session)

    cert_data = {
        "nome": "Orphan With Reason",
        "data_nascita": "01/01/1980",
        "corso": "Failure Reason Test",
        "categoria": "ALTRO",
        "data_rilascio": "01/01/2025"
    }

    # Test create endpoint
    response_create = test_client.post("/certificati/", json=cert_data)
    assert response_create.status_code == 200
    created_data = response_create.json()
    assert created_data["assegnazione_fallita_ragione"] == "Non trovato in anagrafica (matricola mancante)."

    # Test get list endpoint
    response_get = test_client.get("/certificati/?validated=false")
    assert response_get.status_code == 200

    found_cert = None
    for cert in response_get.json():
        if cert["id"] == created_data["id"]:
            found_cert = cert
            break

    assert found_cert is not None
    assert found_cert["assegnazione_fallita_ragione"] == "Non trovato in anagrafica (matricola mancante)."

def test_validate_orphaned_certificate(test_client: TestClient, db_session: Session):
    """Tests that validating an orphaned certificate works and preserves raw data."""
    seed_master_courses(db_session)

    raw_name = "Orphan to Validate"
    raw_birth_date = "15/05/1995"

    # Create an orphaned certificate directly in the DB
    cert = Certificato(
        dipendente_id=None,
        nome_dipendente_raw=raw_name,
        data_nascita_raw=raw_birth_date,
        corso=db_session.query(Corso).filter_by(nome_corso="General").one(),
        data_rilascio=date(2025, 1, 1),
        stato_validazione=ValidationStatus.AUTOMATIC
    )
    db_session.add(cert)
    db_session.commit()

    # Call the validation endpoint
    response = test_client.put(f"/certificati/{cert.id}/valida")
    assert response.status_code == 200

    # Verify the response contains the raw data
    data = response.json()
    assert data["nome"] == raw_name
    assert data["data_nascita"] == raw_birth_date
    assert data["matricola"] is None

    # Verify the state changed in the DB
    db_session.refresh(cert)
    assert cert.stato_validazione == ValidationStatus.MANUAL

def test_get_single_orphaned_certificate(test_client: TestClient, db_session: Session):
    """Tests that GET /certificati/{id} works for an orphaned certificate."""
    seed_master_courses(db_session)

    raw_name = "Single Orphan"
    raw_birth_date = "20/02/2002"

    # Create an orphaned certificate directly in the DB
    cert = Certificato(
        dipendente_id=None,
        nome_dipendente_raw=raw_name,
        data_nascita_raw=raw_birth_date,
        corso=db_session.query(Corso).filter_by(nome_corso="General").one(),
        data_rilascio=date(2025, 1, 1),
        stato_validazione=ValidationStatus.AUTOMATIC
    )
    db_session.add(cert)
    db_session.commit()

    # Call the get single certificate endpoint
    response = test_client.get(f"/certificati/{cert.id}")
    assert response.status_code == 200

    # Verify the response contains the raw data
    data = response.json()
    assert data["nome"] == raw_name
    assert data["data_nascita"] == raw_birth_date
    assert data["matricola"] is None
