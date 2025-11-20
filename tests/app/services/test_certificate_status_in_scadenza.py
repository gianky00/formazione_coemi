from datetime import date, timedelta
from app.services.certificate_logic import get_certificate_status
from app.db.models import Certificato, Corso, Dipendente
from app.core.config import settings

def test_certificate_status_in_scadenza(db_session):
    # Create a course
    course = Corso(nome_corso="General Course", validita_mesi=60, categoria_corso="General")
    db_session.add(course)
    db_session.commit()

    # Threshold is 60 days for General
    threshold = settings.ALERT_THRESHOLD_DAYS

    # Create certificate expiring in threshold - 1 days
    expiry_date = date.today() + timedelta(days=threshold - 1)

    cert = Certificato(
        corso_id=course.id,
        data_rilascio=date.today() - timedelta(days=100),
        data_scadenza_calcolata=expiry_date,
        stato_validazione="AUTOMATIC"
    )
    db_session.add(cert)
    db_session.commit()

    status = get_certificate_status(db_session, cert)
    assert status == "in_scadenza"

def test_certificate_status_attivo_outside_threshold(db_session):
    course = Corso(nome_corso="General Course 2", validita_mesi=60, categoria_corso="General")
    db_session.add(course)
    db_session.commit()

    threshold = settings.ALERT_THRESHOLD_DAYS

    # Expiring in threshold + 1 days
    expiry_date = date.today() + timedelta(days=threshold + 1)

    cert = Certificato(
        corso_id=course.id,
        data_rilascio=date.today() - timedelta(days=100),
        data_scadenza_calcolata=expiry_date,
        stato_validazione="AUTOMATIC"
    )
    db_session.add(cert)
    db_session.commit()

    status = get_certificate_status(db_session, cert)
    assert status == "attivo"

def test_certificate_status_visita_medica_threshold(db_session):
    course = Corso(nome_corso="Visita Medica", validita_mesi=12, categoria_corso="VISITA MEDICA")
    db_session.add(course)
    db_session.commit()

    # Threshold is 30 days for VISITA MEDICA
    threshold = settings.ALERT_THRESHOLD_DAYS_VISITE

    # Expiring in 45 days (outside 30 but inside 60)
    # Should be "attivo" because threshold is 30
    expiry_date = date.today() + timedelta(days=45)

    cert = Certificato(
        corso_id=course.id,
        data_rilascio=date.today() - timedelta(days=100),
        data_scadenza_calcolata=expiry_date,
        stato_validazione="AUTOMATIC"
    )
    db_session.add(cert)
    db_session.commit()

    status = get_certificate_status(db_session, cert)
    assert status == "attivo"

    # Expiring in 20 days (inside 30)
    cert.data_scadenza_calcolata = date.today() + timedelta(days=20)
    db_session.commit()

    status = get_certificate_status(db_session, cert)
    assert status == "in_scadenza"
