from datetime import date

from app.db.models import Certificato, Corso, Dipendente, ValidationStatus


def test_csv_rehiring_update_matricola(test_client, db_session):
    # Setup: Existing employee with OLD matricola
    emp = Dipendente(
        nome="Mario", cognome="Rossi", matricola="OLD001", data_nascita=date(1980, 1, 1)
    )
    db_session.add(emp)

    # Setup: Another employee who is NOT in the CSV (should be preserved)
    emp_historical = Dipendente(
        nome="Luigi", cognome="Verdi", matricola="HIST01", data_nascita=date(1950, 1, 1)
    )
    db_session.add(emp_historical)

    db_session.commit()
    emp_id = emp.id

    # CSV Content: Mario Rossi with NEW matricola
    csv_content = """Cognome;Nome;Badge;Data_nascita
Rossi;Mario;NEW001;01/01/1980
"""
    files = {"file": ("import.csv", csv_content, "text/csv")}

    response = test_client.post("/dipendenti/import-csv", files=files)
    assert response.status_code == 200

    # Clean session to ensure refresh gets latest data
    db_session.expire_all()

    updated_emp = db_session.get(Dipendente, emp_id)

    # Assertions
    # 1. Employee ID should remain the same (update, not delete+create)
    assert updated_emp.id == emp_id
    # 2. Matricola should be updated
    assert updated_emp.matricola == "NEW001"
    # 3. Name/Surname/DOB match
    assert updated_emp.nome == "Mario"
    assert updated_emp.cognome == "Rossi"

    # 4. Historical employee should still exist
    historical = db_session.query(Dipendente).filter_by(matricola="HIST01").first()
    assert historical is not None
    assert historical.nome == "Luigi"


def test_csv_duplicate_error(test_client, db_session):
    # Setup: Two employees with SAME details (Duplicate in DB)
    d1 = Dipendente(
        nome="Giovanni", cognome="Bianchi", matricola="DUP01", data_nascita=date(1990, 1, 1)
    )
    d2 = Dipendente(
        nome="Giovanni", cognome="Bianchi", matricola="DUP02", data_nascita=date(1990, 1, 1)
    )
    db_session.add_all([d1, d2])
    db_session.commit()

    # CSV Content: Giovanni Bianchi with NEW matricola
    csv_content = """Cognome;Nome;Badge;Data_nascita
Bianchi;Giovanni;NEW999;01/01/1990
"""
    files = {"file": ("import.csv", csv_content, "text/csv")}

    response = test_client.post("/dipendenti/import-csv", files=files)
    assert response.status_code == 200
    data = response.json()

    # Should contain warning
    assert "warnings" in data
    assert len(data["warnings"]) > 0
    # Check correct order: Cognome Nome
    assert "Bianchi Giovanni" in str(data["warnings"])

    # Assert DB was NOT updated for these duplicates
    db_session.refresh(d1)
    db_session.refresh(d2)
    assert d1.matricola == "DUP01"
    assert d2.matricola == "DUP02"


def test_csv_broad_effect_linking(test_client, db_session):
    # Scenario:
    # 1. Orphan Cert 1 (AUTOMATIC) - "Convalida Dati"
    # 2. Orphan Cert 2 (MANUAL) - "Dashboard" (Manually validated but unlinked? Possible if forced or logic allows)
    # 3. Employee exists (OLD matricola) or is New. Let's assume Employee exists with OLD matricola to test Update+Link.

    # Setup Employee
    emp = Dipendente(nome="Anna", cognome="Neri", matricola="OLD_A", data_nascita=date(1985, 5, 5))
    db_session.add(emp)

    # Setup Course
    course = Corso(nome_corso="Test Course", categoria_corso="General", validita_mesi=12)
    db_session.add(course)
    db_session.commit()

    # Setup Orphans
    # Note: data_nascita_raw must match employee to allow linking
    dob_str = "05/05/1985"

    cert_auto = Certificato(
        nome_dipendente_raw="Anna Neri",
        data_nascita_raw=dob_str,
        corso_id=course.id,
        data_rilascio=date(2023, 1, 1),
        stato_validazione=ValidationStatus.AUTOMATIC,
        dipendente_id=None,
    )

    cert_manual = Certificato(
        nome_dipendente_raw="Anna Neri",
        data_nascita_raw=dob_str,
        corso_id=course.id,
        data_rilascio=date(2023, 2, 1),
        stato_validazione=ValidationStatus.MANUAL,
        dipendente_id=None,
    )

    db_session.add_all([cert_auto, cert_manual])
    db_session.commit()

    # Verify orphans
    assert cert_auto.dipendente_id is None
    assert cert_manual.dipendente_id is None

    # CSV Content: Anna Neri with NEW matricola
    csv_content = """Cognome;Nome;Badge;Data_nascita
Neri;Anna;NEW_A;05/05/1985
"""
    files = {"file": ("import.csv", csv_content, "text/csv")}

    # Execute Import
    response = test_client.post("/dipendenti/import-csv", files=files)
    assert response.status_code == 200

    db_session.expire_all()
    db_session.refresh(emp)
    db_session.refresh(cert_auto)
    db_session.refresh(cert_manual)

    # Verify Employee Updated
    assert emp.matricola == "NEW_A"

    # Verify BOTH certs linked
    assert cert_auto.dipendente_id == emp.id
    assert cert_manual.dipendente_id == emp.id
