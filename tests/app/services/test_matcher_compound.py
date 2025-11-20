import pytest
from app.services.matcher import find_employee_by_name
from app.db.models import Dipendente

def test_matcher_compound_surname_surname_first(db_session):
    # Setup: Employee with compound surname "De Luca" and name "Giovanni"
    emp = Dipendente(cognome="De Luca", nome="Giovanni", matricola="001", email="test@example.com")
    db_session.add(emp)
    db_session.commit()

    # Test: "De Luca Giovanni" (Surname Name)
    # This currently fails because it splits as "De" / "Luca Giovanni"
    result = find_employee_by_name(db_session, "De Luca Giovanni")

    # We expect this to fail BEFORE the fix, but for the purpose of the plan,
    # I will write the assertion that SHOULD pass after the fix.
    # I will run it and expect failure.
    assert result is not None
    assert result.id == emp.id

def test_matcher_compound_surname_name_first(db_session):
    # Setup
    emp = Dipendente(cognome="De Luca", nome="Giovanni", matricola="001", email="test2@example.com")
    db_session.add(emp)
    db_session.commit()

    # Test: "Giovanni De Luca" (Name Surname)
    # This should pass even with current logic because split "Giovanni" / "De Luca" works
    # (part1="Giovanni", part2="De Luca") -> Match
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
