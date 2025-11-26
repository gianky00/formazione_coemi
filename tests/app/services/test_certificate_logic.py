from datetime import date, datetime, timedelta
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from app.db.models import Certificato, Dipendente, Corso
from app.services.certificate_logic import calculate_expiration_date, get_certificate_status, serialize_certificato
from app.schemas.schemas import CertificatoSchema

def test_calculate_expiration_date_logic():
    """Test the core logic of expiration date calculation."""
    issue_date = date(2025, 1, 1)
    assert calculate_expiration_date(issue_date, 12) == date(2026, 1, 1)
    assert calculate_expiration_date(issue_date, 0) is None
    assert calculate_expiration_date(issue_date, 3) == date(2025, 4, 1)

def test_calculate_expiration_date_handles_datetime_input():
    """Test that the function correctly handles a datetime object as input, returning a date object."""
    issue_datetime = datetime(2022, 5, 10, 14, 30, 0)
    expiration_date = calculate_expiration_date(issue_datetime, 24)
    assert isinstance(expiration_date, date)
    assert expiration_date == date(2024, 5, 10)

def test_get_certificate_status_active_and_expired(db_session: Session):
    """Test basic 'attivo' and 'scaduto' statuses for different employees."""
    dipendente1 = Dipendente(nome="Test", cognome="User", matricola="001")
    dipendente2 = Dipendente(nome="Expired", cognome="User", matricola="001_E")
    corso = Corso(nome_corso="Test Corso", validita_mesi=12, categoria_corso="Test Categoria")
    db_session.add_all([dipendente1, dipendente2, corso])
    db_session.commit()

    cert_attivo = Certificato(
        dipendente_id=dipendente1.id,
        corso_id=corso.id,
        data_rilascio=date.today(),
        data_scadenza_calcolata=date.today() + timedelta(days=365)
    )
    # This certificate is for a DIFFERENT employee, so it should not be "archiviato"
    cert_scaduto = Certificato(
        dipendente_id=dipendente2.id,
        corso_id=corso.id,
        data_rilascio=date(2020, 1, 1),
        data_scadenza_calcolata=date(2021, 1, 1)
    )
    db_session.add_all([cert_attivo, cert_scaduto])
    db_session.commit()

    assert get_certificate_status(db_session, cert_attivo) == "attivo"
    assert get_certificate_status(db_session, cert_scaduto) == "scaduto"

def test_get_certificate_status_in_scadenza(db_session: Session):
    """Test 'in_scadenza' status based on thresholds using timedelta."""
    dipendente = Dipendente(nome="Soon", cognome="Expiring", matricola="002")
    corso_standard = Corso(nome_corso="Standard", validita_mesi=12, categoria_corso="Standard")
    corso_medico = Corso(nome_corso="Visita", validita_mesi=24, categoria_corso="VISITA MEDICA")
    db_session.add_all([dipendente, corso_standard, corso_medico])
    db_session.commit()

    with patch('app.services.certificate_logic.settings') as mock_settings:
        mock_settings.ALERT_THRESHOLD_DAYS = 60
        mock_settings.ALERT_THRESHOLD_DAYS_VISITE = 30

        # Standard course expiring in 50 days
        cert_standard = Certificato(
            dipendente_id=dipendente.id,
            corso_id=corso_standard.id,
            data_rilascio=date.today() - timedelta(days=300),
            data_scadenza_calcolata=date.today() + timedelta(days=50)
        )
        # Medical visit expiring in 25 days
        cert_medico = Certificato(
            dipendente_id=dipendente.id,
            corso_id=corso_medico.id,
            data_rilascio=date.today() - timedelta(days=700),
            data_scadenza_calcolata=date.today() + timedelta(days=25)
        )
        db_session.add_all([cert_standard, cert_medico])
        db_session.commit()

        assert get_certificate_status(db_session, cert_standard) == "in_scadenza"
        assert get_certificate_status(db_session, cert_medico) == "in_scadenza"

def test_get_certificate_status_archiviato(db_session: Session):
    """Test that a renewed certificate is correctly marked as 'archiviato'."""
    dipendente = Dipendente(nome="Rinnovato", cognome="User", matricola="003")
    corso = Corso(nome_corso="Corso Rinnovabile", validita_mesi=12, categoria_corso="Rinnovabile")
    db_session.add_all([dipendente, corso])
    db_session.commit()

    cert_vecchio = Certificato(
        dipendente_id=dipendente.id, corso_id=corso.id,
        data_rilascio=date(2020, 1, 1), data_scadenza_calcolata=date(2021, 1, 1)
    )
    cert_nuovo = Certificato(
        dipendente_id=dipendente.id, corso_id=corso.id,
        data_rilascio=date(2021, 1, 1), data_scadenza_calcolata=date.today().replace(year=date.today().year + 1)
    )
    db_session.add_all([cert_vecchio, cert_nuovo])
    db_session.commit()

    assert get_certificate_status(db_session, cert_vecchio) == "archiviato"
    assert get_certificate_status(db_session, cert_nuovo) == "attivo"

def test_serialize_certificato_with_linked_employee(db_session: Session):
    """Test serialization of a certificate that is properly linked to an employee."""
    dipendente = Dipendente(
        nome="Mario", cognome="Rossi", matricola="12345", data_nascita=date(1990, 5, 15)
    )
    corso = Corso(nome_corso="Sicurezza Base", validita_mesi=60, categoria_corso="Sicurezza")
    db_session.add_all([dipendente, corso])
    db_session.commit()

    cert = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date(2024, 1, 1),
        data_scadenza_calcolata=date(2029, 1, 1),
        validated=True
    )
    db_session.add(cert)
    db_session.commit()

    serialized_data = serialize_certificato(db_session, cert)

    assert isinstance(serialized_data, CertificatoSchema)
    assert serialized_data.nome == "Rossi Mario"
    assert serialized_data.matricola == "12345"
    assert serialized_data.data_nascita == date(1990, 5, 15)
    assert serialized_data.stato_certificato == "attivo"
    assert serialized_data.corso == "Sicurezza Base"
    assert serialized_data.validated is True

def test_serialize_certificato_with_orphan_employee(db_session: Session):
    """Test serialization of an 'orphaned' certificate with no linked employee."""
    corso = Corso(nome_corso="Primo Soccorso", validita_mesi=36, categoria_corso="Emergenza")
    db_session.add(corso)
    db_session.commit()

    cert = Certificato(
        dipendente_id=None,
        corso_id=corso.id,
        nome_dipendente_raw="Luigi Verdi",
        data_nascita_raw=date(1985, 10, 20),
        data_rilascio=date(2023, 6, 1),
        data_scadenza_calcolata=date(2026, 6, 1),
        validated=False,
        assegnazione_fallita_ragione="Test Reason"
    )
    db_session.add(cert)
    db_session.commit()

    serialized_data = serialize_certificato(db_session, cert)

    assert isinstance(serialized_data, CertificatoSchema)
    assert serialized_data.nome == "Luigi Verdi"
    assert serialized_data.matricola is None
    assert serialized_data.data_nascita == date(1985, 10, 20)
    assert serialized_data.stato_certificato == "attivo"
    assert serialized_data.assegnazione_fallita_ragione == "Test Reason"
    assert serialized_data.validated is False

def test_status_logic_with_null_dates(db_session: Session):
    """Test that status logic is robust to certificates with null dates."""
    dipendente = Dipendente(nome="Null", cognome="Date", matricola="999")
    corso = Corso(nome_corso="SenzaData", validita_mesi=12, categoria_corso="Speciale")
    db_session.add_all([dipendente, corso])
    db_session.commit()

    # Certificate with no release date but an expiration date
    cert_no_release = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=None,
        data_scadenza_calcolata=date(2020, 1, 1) # Expired
    )
    db_session.add(cert_no_release)
    db_session.commit()

    # Even if another cert existed, this one can't be 'archiviato' because we can't compare release dates
    assert get_certificate_status(db_session, cert_no_release) == "scaduto"

    # Test serialization of a certificate with missing dates
    serialized = serialize_certificato(db_session, cert_no_release)
    assert serialized.data_rilascio is None
    assert serialized.stato_certificato == "scaduto"
