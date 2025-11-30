import pytest
from app.services.matcher import find_employee_by_name
from app.db.models import Dipendente
from datetime import date

def test_matcher_compound_surname_surname_first(db_session):
    # Setup: Employee with compound surname "De Luca" and name "Giovanni"
    emp = Dipendente(cognome="De Luca", nome="Giovanni", matricola="001", email="test@example.com")
    db_session.add(emp)
    db_session.commit()

    # Test: "De Luca Giovanni" (Surname Name)
    result = find_employee_by_name(db_session, "De Luca Giovanni")
    assert result is not None
    assert result.id == emp.id

def test_matcher_compound_surname_name_first(db_session):
    # Setup
    emp = Dipendente(cognome="De Luca", nome="Giovanni", matricola="001", email="test2@example.com")
    db_session.add(emp)
    db_session.commit()

    # Test: "Giovanni De Luca" (Name Surname)
    result = find_employee_by_name(db_session, "Giovanni De Luca")

    assert result is not None
    assert result.id == emp.id

def test_matcher_complex_name(db_session):
    # Setup: "Maria Teresa" "Di Giovanna"
    emp = Dipendente(cognome="Di Giovanna", nome="Maria Teresa", matricola="002", email="test3@example.com")
    db_session.add(emp)
    db_session.commit()

    # Test: "Di Giovanna Maria Teresa"
    result = find_employee_by_name(db_session, "Di Giovanna Maria Teresa")
    assert result is not None
    assert result.id == emp.id

    # Test: "Maria Teresa Di Giovanna"
    result = find_employee_by_name(db_session, "Maria Teresa Di Giovanna")
    assert result is not None
    assert result.id == emp.id

def test_matcher_short_name(db_session):
    assert find_employee_by_name(db_session, "") is None
    assert find_employee_by_name(db_session, "Mario") is None

def test_matcher_no_match(db_session):
    assert find_employee_by_name(db_session, "Mario Rossi") is None

def test_matcher_homonyms_ambiguity(db_session):
    d1 = Dipendente(nome="Mario", cognome="Rossi", data_nascita=date(1990,1,1), matricola="1")
    d2 = Dipendente(nome="Mario", cognome="Rossi", data_nascita=date(1995,1,1), matricola="2")
    db_session.add_all([d1, d2])
    db_session.commit()

    # Without DOB -> Ambiguous -> None
    assert find_employee_by_name(db_session, "Mario Rossi") is None

def test_matcher_homonyms_resolution(db_session):
    d1 = Dipendente(nome="Mario", cognome="Bianchi", data_nascita=date(1990,1,1), matricola="3")
    d2 = Dipendente(nome="Mario", cognome="Bianchi", data_nascita=date(1995,1,1), matricola="4")
    db_session.add_all([d1, d2])
    db_session.commit()

    # With DOB -> Resolved
    res = find_employee_by_name(db_session, "Mario Bianchi", data_nascita=date(1995,1,1))
    assert res is not None
    assert res.id == d2.id

def test_matcher_homonyms_dob_mismatch(db_session):
    d1 = Dipendente(nome="Luigi", cognome="Verdi", data_nascita=date(1990,1,1), matricola="5")
    db_session.add(d1)
    db_session.commit()

    # Name match, Date mismatch -> None
    res = find_employee_by_name(db_session, "Luigi Verdi", data_nascita=date(2000,1,1))
    assert res is None
