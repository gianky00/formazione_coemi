from datetime import date, datetime
from unittest.mock import patch
from sqlalchemy.orm import Session
from app.db.models import Certificato, Dipendente, Corso
from app.services.certificate_logic import calculate_expiration_date, get_certificate_status

def test_calculate_expiration_date():
    """
    Testa la funzione di calcolo della data di scadenza.
    """
    issue_date = date(2025, 1, 1)
    assert calculate_expiration_date(issue_date, 12) == date(2026, 1, 1)
    assert calculate_expiration_date(issue_date, 0) is None

def test_calculate_expiration_date_returns_date_object():
    """
    Tests that calculate_expiration_date returns a date object, not a datetime object,
    even when a datetime object is passed as input.
    """
    # Using a datetime object to expose the bug
    issue_date = datetime(2022, 1, 1, 8, 30, 0)
    validity_months = 12
    expiration_date = calculate_expiration_date(issue_date, validity_months)
    # This assertion should fail before the fix because it will return a datetime object
    assert type(expiration_date) == date

def test_get_certificate_status(db_session: Session):
    """
    Testa gli stati 'attivo' e 'scaduto'.
    """
    dipendente = Dipendente(nome="Test", cognome="User")
    corso = Corso(nome_corso="Test Corso", validita_mesi=12, categoria_corso="Test Categoria")
    scaduto_dipendente = Dipendente(nome="Scaduto", cognome="User")
    db_session.add_all([dipendente, corso, scaduto_dipendente])
    db_session.commit()

    # Certificato attivo
    cert_attivo = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date.today(),
        data_scadenza_calcolata=date.today() + date.resolution * 100
    )
    # Certificato scaduto (senza rinnovi)
    cert_scaduto = Certificato(
        dipendente_id=scaduto_dipendente.id,
        corso_id=corso.id,
        data_rilascio=date(2020, 1, 1),
        data_scadenza_calcolata=date(2021, 1, 1)
    )
    # Certificato senza scadenza
    cert_no_scadenza = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date(2020, 1, 1),
        data_scadenza_calcolata=None
    )
    db_session.add_all([cert_attivo, cert_scaduto, cert_no_scadenza])
    db_session.commit()

    assert get_certificate_status(db_session, cert_attivo) == "attivo"
    assert get_certificate_status(db_session, cert_scaduto) == "scaduto"
    assert get_certificate_status(db_session, cert_no_scadenza) == "attivo"

def test_get_certificate_status_rinnovato(db_session: Session):
    """
    Testa che lo stato di un certificato scaduto sia 'rinnovato' se ne esiste uno più recente.
    """
    dipendente = Dipendente(nome="Rinnovato", cognome="User")
    corso = Corso(nome_corso="Corso Rinnovabile", validita_mesi=12, categoria_corso="Rinnovabile")
    db_session.add_all([dipendente, corso])
    db_session.commit()

    # Certificato vecchio (scaduto)
    cert_vecchio = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date(2020, 1, 1),
        data_scadenza_calcolata=date(2021, 1, 1)
    )
    # Certificato nuovo (attivo)
    cert_nuovo = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date(2021, 1, 1),
        data_scadenza_calcolata=date.today() + date.resolution * 100 # Scadenza futura
    )
    db_session.add_all([cert_vecchio, cert_nuovo])
    db_session.commit()

    assert get_certificate_status(db_session, cert_vecchio) == "rinnovato"
    assert get_certificate_status(db_session, cert_nuovo) == "attivo"

def test_orphan_certificates_not_renewed_by_others(db_session: Session):
    """
    Test that an expired orphaned certificate for one person is NOT marked as 'rinnovato'
    just because there is a newer orphaned certificate for ANOTHER person.
    """
    # Create a course
    corso = Corso(nome_corso="Safety First", validita_mesi=12, categoria_corso="SAFETY")
    db_session.add(corso)
    db_session.commit()

    # Create expired orphan certificate for "Alice"
    cert_alice = Certificato(
        dipendente_id=None,
        nome_dipendente_raw="Alice",
        corso_id=corso.id,
        data_rilascio=date(2020, 1, 1),
        data_scadenza_calcolata=date(2021, 1, 1)
    )

    # Create newer valid orphan certificate for "Bob"
    cert_bob = Certificato(
        dipendente_id=None,
        nome_dipendente_raw="Bob",
        corso_id=corso.id,
        data_rilascio=date(2024, 1, 1),
        data_scadenza_calcolata=date(2030, 1, 1)
    )

    db_session.add_all([cert_alice, cert_bob])
    db_session.commit()

    # Check status of Alice's certificate
    # It should be "scaduto" because Bob's certificate has nothing to do with Alice
    # And orphans cannot renew other orphans
    status = get_certificate_status(db_session, cert_alice)

    assert status == "scaduto", f"Expected 'scaduto' but got '{status}'. Orphaned certificates are being mixed up!"

def test_infinite_validity_status(db_session: Session):
    """
    Testa che i certificati con validità infinita (data_scadenza_calcolata=None)
    siano sempre 'attivo' se non c'è una scadenza esplicita, anche se sono vecchi.
    """
    dipendente = Dipendente(nome="Infinite", cognome="User")
    corso = Corso(nome_corso="Nomina", validita_mesi=0, categoria_corso="NOMINE")
    db_session.add_all([dipendente, corso])
    db_session.commit()

    # Certificato vecchio (2010) ma validità infinita
    cert_vecchio = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date(2010, 1, 1),
        data_scadenza_calcolata=None
    )
    db_session.add(cert_vecchio)
    db_session.commit()

    assert get_certificate_status(db_session, cert_vecchio) == "attivo"

    # Aggiungiamo un certificato PIÙ NUOVO (2020), sempre infinito
    cert_nuovo = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date(2020, 1, 1),
        data_scadenza_calcolata=None
    )
    db_session.add(cert_nuovo)
    db_session.commit()

    assert get_certificate_status(db_session, cert_vecchio) == "attivo"
    assert get_certificate_status(db_session, cert_nuovo) == "attivo"
