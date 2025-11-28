
import pytest
from app.db.models import Certificato, ValidationStatus, Corso, Dipendente
import datetime

def test_orphans_visibility(test_client, db_session):
    """
    Test that orphaned certificates (no dipendente_id) are visible in the unvalidated list.
    """
    # 1. Create a course
    course = Corso(nome_corso="ATEX", categoria_corso="ATEX", validita_mesi=60)
    db_session.add(course)
    db_session.commit()

    # 2. Create an orphan certificate
    orphan_cert = Certificato(
        dipendente_id=None,
        nome_dipendente_raw="GIUSEPPE ROSSI",
        data_nascita_raw="01/01/1980",
        corso_id=course.id,
        data_rilascio=datetime.date(2023, 1, 1),
        stato_validazione=ValidationStatus.AUTOMATIC
    )
    db_session.add(orphan_cert)
    db_session.commit()

    # 3. Call GET /certificati/?validated=false
    # Note: test_client base_url includes /api/v1
    response = test_client.get("/certificati/?validated=false")
    assert response.status_code == 200
    data = response.json()

    # 4. Verify the orphan is in the list
    assert len(data) > 0
    found = False
    for cert in data:
        if cert["nome"] == "GIUSEPPE ROSSI" and cert["matricola"] is None:
            found = True
            assert cert["assegnazione_fallita_ragione"] == "Non trovato in anagrafica (matricola mancante)."
            assert cert["categoria"] == "ATEX"

    assert found, "Orphan certificate not found in validated=false list"

def test_csv_import_links_orphans(test_client, db_session):
    """
    Test that CSV import automatically links existing orphans to the new employee.
    """
    # 1. Create a course
    course = Corso(nome_corso="HLO", categoria_corso="HLO", validita_mesi=24)
    db_session.add(course)
    db_session.commit()

    # 2. Create an orphan certificate for "BIANCHI PAOLO"
    orphan = Certificato(
        dipendente_id=None,
        nome_dipendente_raw="BIANCHI PAOLO",
        data_nascita_raw="15/05/1985",
        corso_id=course.id,
        data_rilascio=datetime.date(2022, 5, 15),
        stato_validazione=ValidationStatus.AUTOMATIC
    )
    db_session.add(orphan)
    db_session.commit()

    # Verify it is orphan
    assert orphan.dipendente_id is None

    # 3. Import CSV with BIANCHI PAOLO
    csv_content = (
        "Cognome;Nome;Badge;Data_nascita\n"
        "Bianchi;Paolo;B001;15/05/1985\n"
    )
    content_bytes = csv_content.encode('utf-8')
    files = {"file": ("dipendenti.csv", content_bytes, "text/csv")}
    response = test_client.post("/dipendenti/import-csv", files=files)
    assert response.status_code == 200
    assert "1 certificati orfani collegati" in response.json()["message"]

    # 4. Verify the certificate is now linked
    # Reload the object from session
    db_session.refresh(orphan)
    assert orphan.dipendente_id is not None
    assert orphan.dipendente.matricola == "B001"

def test_csv_import_upsert(test_client, db_session):
    """
    Test that CSV import updates existing employees and doesn't delete them.
    """
    # 1. Create an existing employee
    emp = Dipendente(nome="Mario", cognome="Rossi", matricola="001", data_nascita=datetime.date(1980, 1, 1))
    db_session.add(emp)
    db_session.commit()

    # 2. Prepare CSV with updated name for 001 and a new employee 002
    csv_content = (
        "Cognome;Nome;Badge;Data_nascita\n"
        "Rossi;Mario Updated;001;01/01/1980\n"
        "Verdi;Luigi;002;02/02/1990\n"
    )
    content_bytes = csv_content.encode('utf-8')

    # 3. Upload CSV
    files = {"file": ("test.csv", content_bytes, "text/csv")}
    response = test_client.post("/dipendenti/import-csv", files=files)
    assert response.status_code == 200

    # 4. Verify 001 is updated and 002 is created
    u_emp = db_session.query(Dipendente).filter_by(matricola="001").first()
    assert u_emp.nome == "Mario Updated"

    n_emp = db_session.query(Dipendente).filter_by(matricola="002").first()
    assert n_emp is not None
    assert n_emp.cognome == "Verdi"
