from datetime import date

from app.db.models import Certificato, Corso, ValidationStatus
from app.services.notification_service import get_report_data


def test_get_report_data_logic(db_session):
    # Setup Data
    c1 = Corso(nome_corso="Antincendio", categoria_corso="FORMAZIONE", validita_mesi=60)
    c2 = Corso(nome_corso="Visita Medica", categoria_corso="VISITA MEDICA", validita_mesi=12)
    db_session.add_all([c1, c2])
    db_session.commit()

    # Expired cert
    cert = Certificato(
        corso=c1,
        data_rilascio=date(2010, 1, 1),
        data_scadenza_calcolata=date(2015, 1, 1),
        stato_validazione=ValidationStatus.MANUAL,
    )
    db_session.add(cert)
    db_session.commit()

    _exp_visite, _exp_corsi, overdue = get_report_data(db_session)
    assert len(overdue) == 1
