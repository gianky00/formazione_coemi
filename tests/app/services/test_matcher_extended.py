from datetime import date

from app.db.models import Dipendente
from app.services.matcher import find_employee_by_name


def test_matcher_triple_name_complex_split(db_session):
    # Setup: "Gian Luca" "Della Valle"
    emp = Dipendente(nome="Gian Luca", cognome="Della Valle", matricola="X1", email="gian@test.com")
    db_session.add(emp)
    db_session.commit()

    # Full name in various order
    assert find_employee_by_name(db_session, "Gian Luca Della Valle").id == emp.id
    assert find_employee_by_name(db_session, "Della Valle Gian Luca").id == emp.id

    # Mixed parts
    # "Della Valle Gian Luca" -> split at index 1: "Della" / "Valle Gian Luca" (No)
    # split at index 2: "Della Valle" / "Gian Luca" (YES)
    assert find_employee_by_name(db_session, "Della Valle Gian Luca").id == emp.id


def test_matcher_extra_spaces(db_session):
    emp = Dipendente(nome="Mario", cognome="Rossi", matricola="X2")
    db_session.add(emp)
    db_session.commit()

    # Leading/trailing and internal extra spaces
    assert find_employee_by_name(db_session, "  Mario   Rossi  ").id == emp.id


def test_matcher_dob_no_ambiguity(db_session):
    # Test that providing a DOB doesn't break simple matches
    emp = Dipendente(nome="Anna", cognome="Neri", data_nascita=date(1985, 5, 5), matricola="X3")
    db_session.add(emp)
    db_session.commit()

    # Correct DOB
    assert (
        find_employee_by_name(db_session, "Anna Neri", data_nascita=date(1985, 5, 5)).id == emp.id
    )

    # Wrong DOB (even if only one Anna Neri exists) -> Should return None according to current logic
    # Logic in matcher.py:
    # if data_nascita:
    #     filtered_by_dob = [e for e in found_employees.values() if e.data_nascita == data_nascita]
    #     if len(filtered_by_dob) == 0: return None
    assert find_employee_by_name(db_session, "Anna Neri", data_nascita=date(1990, 1, 1)) is None


def test_matcher_case_insensitive_ilike(db_session):
    emp = Dipendente(nome="MARIO", cognome="ROSSI", matricola="X4")
    db_session.add(emp)
    db_session.commit()

    # Search with lowercase
    assert find_employee_by_name(db_session, "mario rossi").id == emp.id


def test_matcher_middle_name_ambiguity(db_session):
    # "Marco" "Antonio Rossi" vs "Marco Antonio" "Rossi"
    emp1 = Dipendente(nome="Marco", cognome="Antonio Rossi", matricola="X5")
    db_session.add(emp1)
    db_session.commit()

    # Searching "Marco Antonio Rossi" should find emp1
    assert find_employee_by_name(db_session, "Marco Antonio Rossi").id == emp1.id

    # Add a second one that could match
    emp2 = Dipendente(nome="Marco Antonio", cognome="Rossi", matricola="X6")
    db_session.add(emp2)
    db_session.commit()

    # Now it's ambiguous
    assert find_employee_by_name(db_session, "Marco Antonio Rossi") is None
