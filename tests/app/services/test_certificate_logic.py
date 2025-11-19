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
        data_scadenza_calcolata=date.today() + date.resolution * 30
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
        data_scadenza_calcolata=date.today() + date.resolution * 30 # Scadenza futura
    )
    db_session.add_all([cert_vecchio, cert_nuovo])
    db_session.commit()

    assert get_certificate_status(db_session, cert_vecchio) == "rinnovato"
    assert get_certificate_status(db_session, cert_nuovo) == "attivo"
