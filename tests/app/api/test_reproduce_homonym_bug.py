from datetime import date
from app.db.models import Dipendente, Certificato, Corso
from app.schemas.schemas import CertificatoSchema

def test_update_certificato_homonym_linking(test_client, db_session):
    # 1. Setup Employees (Homonyms)
    emp1 = Dipendente(nome="Mario", cognome="Rossi", matricola="001", data_nascita=date(1980, 1, 1))
    emp2 = Dipendente(nome="Mario", cognome="Rossi", matricola="002", data_nascita=date(1990, 1, 1))
    db_session.add_all([emp1, emp2])

    # Create a Course
    course = Corso(nome_corso="Test Course", categoria_corso="General", validita_mesi=12)
    db_session.add(course)
    db_session.commit()

    # 2. Create Orphan Certificate
    # Typo in name ("Mario Ross"), but correct DOB for emp1 ("01/01/1980")
    cert = Certificato(
        nome_dipendente_raw="Mario Ross",
        data_nascita_raw="01/01/1980",
        corso_id=course.id,
        data_rilascio=date(2023, 1, 1),
        dipendente_id=None # Orphan
    )
    db_session.add(cert)
    db_session.commit()

    # Verify initial state
    assert cert.dipendente_id is None

    # 3. Update Name to "Mario Rossi"
    # This should trigger the matcher. Since there are 2 matches for "Mario Rossi",
    # it MUST use data_nascita_raw (01/01/1980) to disambiguate and link to emp1.
    payload = {"nome": "Mario Rossi"}
    response = test_client.put(f"/certificati/{cert.id}", json=payload)

    assert response.status_code == 200
    data = response.json()

    # Assert it linked to emp1 (Born 1980)
    assert data["matricola"] == "001"
    assert data["nome"] == "Rossi Mario" # or "Mario Rossi" depending on schema format

    # Double check via DB
    db_session.refresh(cert)
    assert cert.dipendente_id == emp1.id

def test_update_certificato_data_nascita(test_client, db_session):
    # 1. Setup
    course = Corso(nome_corso="Test Course", categoria_corso="General", validita_mesi=12)
    db_session.add(course)
    db_session.commit()

    cert = Certificato(
        nome_dipendente_raw="Test User",
        data_nascita_raw="01/01/2000",
        corso_id=course.id,
        data_rilascio=date(2023, 1, 1),
        dipendente_id=None
    )
    db_session.add(cert)
    db_session.commit()

    # 2. Update data_nascita
    new_dob = "05/05/1995"
    payload = {"data_nascita": new_dob}

    response = test_client.put(f"/certificati/{cert.id}", json=payload)

    # This might fail with 422 if data_nascita is extra field forbidden,
    # or just ignore it if schema allows extra but doesn't use it.
    # Current Pydantic config (v2) usually ignores extras by default unless configured otherwise.
    # If ignored, status 200 but value not changed.

    if response.status_code == 200:
        db_session.refresh(cert)
        # Verify if updated (Expected: FAIL currently)
        assert cert.data_nascita_raw == new_dob
    else:
        # If it fails validation (unexpected field), that's also a fail for the requirement
        assert False, f"Update failed with status {response.status_code}: {response.text}"
