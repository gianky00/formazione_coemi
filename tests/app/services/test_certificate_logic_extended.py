from datetime import date, timedelta

from app.db.models import Certificato, Corso, Dipendente
from app.services.certificate_logic import get_bulk_certificate_statuses


def test_get_bulk_certificate_statuses_basic(db_session):
    # Setup
    emp = Dipendente(nome="Mario", cognome="Rossi")
    course = Corso(nome_corso="Sicurezza", validita_mesi=12, categoria_corso="GEN")
    db_session.add_all([emp, course])
    db_session.commit()

    today = date.today()

    # 1. Active cert
    cert1 = Certificato(
        dipendente_id=emp.id,
        corso_id=course.id,
        data_rilascio=today,
        data_scadenza_calcolata=today + timedelta(days=365),
    )
    # 2. Expired but archived (because cert1 is newer)
    cert2 = Certificato(
        dipendente_id=emp.id,
        corso_id=course.id,
        data_rilascio=today - timedelta(days=500),
        data_scadenza_calcolata=today - timedelta(days=135),
    )
    # 3. In expiration threshold (e.g. 10 days left)
    cert3 = Certificato(
        dipendente_id=emp.id,
        corso_id=course.id,
        data_rilascio=today - timedelta(days=350),
        data_scadenza_calcolata=today + timedelta(days=10),
    )

    db_session.add_all([cert1, cert2, cert3])
    db_session.commit()

    certs = [cert1, cert2, cert3]
    status_map = get_bulk_certificate_statuses(db_session, certs)

    assert status_map[cert1.id] == "attivo"
    assert status_map[cert2.id] == "archiviato"
    assert status_map[cert3.id] == "in_scadenza"


def test_get_bulk_certificate_statuses_multiple_employees(db_session):
    course = Corso(nome_corso="Privacy", validita_mesi=12, categoria_corso="PRIV")
    emp1 = Dipendente(nome="User1", cognome="One")
    emp2 = Dipendente(nome="User2", cognome="Two")
    db_session.add_all([course, emp1, emp2])
    db_session.commit()

    today = date.today()

    # Emp 1 has an expired cert (no newer)
    c1 = Certificato(
        dipendente_id=emp1.id,
        corso_id=course.id,
        data_rilascio=today - timedelta(days=500),
        data_scadenza_calcolata=today - timedelta(days=100),
    )

    # Emp 2 has an expired cert AND a newer active cert
    c2_old = Certificato(
        dipendente_id=emp2.id,
        corso_id=course.id,
        data_rilascio=today - timedelta(days=500),
        data_scadenza_calcolata=today - timedelta(days=100),
    )
    c2_new = Certificato(
        dipendente_id=emp2.id,
        corso_id=course.id,
        data_rilascio=today,
        data_scadenza_calcolata=today + timedelta(days=365),
    )

    db_session.add_all([c1, c2_old, c2_new])
    db_session.commit()

    status_map = get_bulk_certificate_statuses(db_session, [c1, c2_old, c2_new])

    assert status_map[c1.id] == "scaduto"
    assert status_map[c2_old.id] == "archiviato"
    assert status_map[c2_new.id] == "attivo"


def test_get_bulk_certificate_statuses_empty(db_session):
    assert get_bulk_certificate_statuses(db_session, []) == {}


def test_get_bulk_certificate_statuses_visita_medica(db_session):
    course_med = Corso(nome_corso="Visita", validita_mesi=12, categoria_corso="VISITA MEDICA")
    emp = Dipendente(nome="Doc", cognome="Who")
    db_session.add_all([course_med, emp])
    db_session.commit()

    today = date.today()
    # 45 days left -> "attivo" for VISITA MEDICA (threshold 30), but would be "in_scadenza" for GEN (threshold 60)
    c_med = Certificato(
        dipendente_id=emp.id,
        corso_id=course_med.id,
        data_rilascio=today - timedelta(days=300),
        data_scadenza_calcolata=today + timedelta(days=45),
    )

    db_session.add(c_med)
    db_session.commit()

    status_map = get_bulk_certificate_statuses(db_session, [c_med])
    assert status_map[c_med.id] == "attivo"
