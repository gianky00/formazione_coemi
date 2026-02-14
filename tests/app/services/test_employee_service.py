from datetime import date

import pytest
from fastapi import HTTPException

from app.db.models import Certificato, Corso, Dipendente, ValidationStatus
from app.services import employee_service


def test_validate_unique_constraints_no_change(db_session):
    emp = Dipendente(nome="Mario", cognome="Rossi", matricola="123", email="mario@test.com")
    db_session.add(emp)
    db_session.commit()

    # No changes in update_dict
    employee_service.validate_unique_constraints(db_session, emp, {})
    # Should not raise


def test_validate_unique_constraints_duplicate_matricola(db_session):
    emp1 = Dipendente(nome="Mario", cognome="Rossi", matricola="123")
    emp2 = Dipendente(nome="Luigi", cognome="Verdi", matricola="456")
    db_session.add_all([emp1, emp2])
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        employee_service.validate_unique_constraints(db_session, emp1, {"matricola": "456"})
    assert exc.value.status_code == 400
    assert "Matricola già esistente" in exc.value.detail


def test_validate_unique_constraints_duplicate_email(db_session):
    emp1 = Dipendente(nome="Mario", cognome="Rossi", email="mario@test.com")
    emp2 = Dipendente(nome="Luigi", cognome="Verdi", email="luigi@test.com")
    db_session.add_all([emp1, emp2])
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        employee_service.validate_unique_constraints(db_session, emp1, {"email": "luigi@test.com"})
    assert exc.value.status_code == 400
    assert "Email già esistente" in exc.value.detail


def test_validate_unique_constraints_empty_matricola(db_session):
    emp = Dipendente(nome="Mario", cognome="Rossi", matricola="123")
    db_session.add(emp)
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        employee_service.validate_unique_constraints(db_session, emp, {"matricola": "  "})
    assert exc.value.status_code == 400
    assert "La matricola non può essere vuota" in exc.value.detail


def test_process_csv_row_new_employee(db_session):
    row = {
        "Nome": "Mario",
        "Cognome": "Rossi",
        "Badge": "B001",
        "Data di nascita": "01/01/1980",
        "Data di assunzione": "01/01/2020",
    }
    warnings = []
    employee_service.process_csv_row(row, db_session, warnings)
    db_session.commit()

    emp = db_session.query(Dipendente).filter_by(matricola="B001").first()
    assert emp is not None
    assert emp.nome == "Mario"
    assert emp.cognome == "Rossi"
    assert emp.data_nascita == date(1980, 1, 1)
    assert emp.data_assunzione == date(2020, 1, 1)
    assert not warnings


def test_process_csv_row_update_by_identity(db_session):
    # Existing employee without matricola
    emp = Dipendente(nome="Mario", cognome="Rossi", data_nascita=date(1980, 1, 1))
    db_session.add(emp)
    db_session.commit()

    row = {"nome": "Mario", "cognome": "Rossi", "badge": "B002", "Data_nascita": "01/01/1980"}
    warnings = []
    employee_service.process_csv_row(row, db_session, warnings)
    db_session.commit()

    db_session.refresh(emp)
    assert emp.matricola == "B002"
    assert any("Aggiornata matricola" in w for w in warnings)


def test_process_csv_row_ambiguity(db_session):
    # Two employees with same name and DOB
    emp1 = Dipendente(nome="Mario", cognome="Rossi", data_nascita=date(1980, 1, 1), matricola="M1")
    emp2 = Dipendente(nome="Mario", cognome="Rossi", data_nascita=date(1980, 1, 1), matricola="M2")
    db_session.add_all([emp1, emp2])
    db_session.commit()

    row = {"Nome": "Mario", "Cognome": "Rossi", "Badge": "M3", "Data di nascita": "01/01/1980"}
    warnings = []
    employee_service.process_csv_row(row, db_session, warnings)

    assert any("Ambiguità trovata" in w for w in warnings)
    assert emp1.matricola == "M1"
    assert emp2.matricola == "M2"


def test_process_csv_row_matricola_identity_update(db_session):
    # Existing employee with matricola B001 named Luigi Verdi
    emp1 = Dipendente(nome="Luigi", cognome="Verdi", matricola="B001")
    db_session.add(emp1)
    db_session.commit()

    # Import row with same matricola B001 but named Mario Rossi
    row = {"Nome": "Mario", "Cognome": "Rossi", "Badge": "B001"}

    warnings = []
    employee_service.process_csv_row(row, db_session, warnings)

    # Check if emp1 was updated
    db_session.flush()
    db_session.refresh(emp1)
    assert emp1.nome == "Mario"
    assert emp1.cognome == "Rossi"
    assert not warnings


def test_link_orphaned_certificates(db_session):
    # Setup: orphan cert and matching employee
    corso = Corso(nome_corso="Sicurezza", validita_mesi=12, categoria_corso="Generale")
    db_session.add(corso)
    db_session.flush()

    cert = Certificato(
        nome_dipendente_raw="Mario Rossi",
        data_nascita_raw="01/01/1980",
        corso_id=corso.id,
        data_rilascio=date(2023, 1, 1),
        stato_validazione=ValidationStatus.AUTOMATIC,
    )
    db_session.add(cert)

    emp = Dipendente(nome="Mario", cognome="Rossi", data_nascita=date(1980, 1, 1), matricola="M100")
    db_session.add(emp)
    db_session.commit()

    # Run link
    count = employee_service.link_orphaned_certificates_after_import(db_session)
    assert count == 1

    db_session.commit()  # Flush and commit changes
    db_session.refresh(cert)
    assert cert.dipendente_id == emp.id
