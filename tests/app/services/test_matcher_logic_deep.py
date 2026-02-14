from app.db.models import Dipendente
from app.services.matcher import find_employee_by_name


def test_find_employee_triple_name(db_session):
    # Setup
    e1 = Dipendente(nome="MARIO GIUSEPPE", cognome="ROSSI")
    db_session.add(e1)
    db_session.flush()

    # Test exact match
    assert find_employee_by_name(db_session, "MARIO GIUSEPPE ROSSI").id == e1.id
    # Test reversed match
    assert find_employee_by_name(db_session, "ROSSI MARIO GIUSEPPE").id == e1.id
    # Test partial split (MARIO | GIUSEPPE ROSSI)
    assert find_employee_by_name(db_session, "MARIO GIUSEPPE ROSSI") is not None


def test_find_employee_with_apostrophe(db_session):
    e1 = Dipendente(nome="GIANLUIGI", cognome="D'ALESSANDRO")
    db_session.add(e1)
    db_session.flush()

    assert find_employee_by_name(db_session, "GIANLUIGI D'ALESSANDRO").id == e1.id
    assert find_employee_by_name(db_session, "D'ALESSANDRO GIANLUIGI").id == e1.id


def test_find_employee_ambiguity_no_dob(db_session):
    e1 = Dipendente(nome="MARIO", cognome="ROSSI", matricola="M1")
    e2 = Dipendente(nome="MARIO", cognome="ROSSI", matricola="M2")
    db_session.add_all([e1, e2])
    db_session.flush()

    # Ambiguous - should return None
    assert find_employee_by_name(db_session, "MARIO ROSSI") is None


def test_find_employee_ambiguity_resolved_by_dob(db_session):
    from datetime import date

    dob1 = date(1980, 1, 1)
    dob2 = date(1990, 5, 20)
    e1 = Dipendente(nome="MARIO", cognome="ROSSI", data_nascita=dob1)
    e2 = Dipendente(nome="MARIO", cognome="ROSSI", data_nascita=dob2)
    db_session.add_all([e1, e2])
    db_session.flush()

    # Ambiguous without DOB
    assert find_employee_by_name(db_session, "MARIO ROSSI") is None
    # Resolved with DOB
    assert find_employee_by_name(db_session, "MARIO ROSSI", data_nascita=dob1).id == e1.id
    # No match with wrong DOB
    assert find_employee_by_name(db_session, "MARIO ROSSI", data_nascita=date(2000, 1, 1)) is None


def test_find_employee_invalid_inputs(db_session):
    assert find_employee_by_name(db_session, "Mario") is None  # Only one part
    assert find_employee_by_name(db_session, "   ") is None
    assert find_employee_by_name(db_session, None) is None
