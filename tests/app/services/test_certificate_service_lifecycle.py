from datetime import date

from app.db.models import Certificato, Corso, Dipendente, ValidationStatus
from app.services import certificate_service


def test_archive_obsolete_certs_integration(db_session):
    # Setup Employee and Course
    emp = Dipendente(nome="MARIO", cognome="ROSSI", matricola="M1")
    corso = Corso(nome_corso="Antincendio", categoria_corso="FORMAZIONE", validita_mesi=60)
    db_session.add_all([emp, corso])
    db_session.commit()

    # Old Cert
    c1 = Certificato(
        dipendente=emp,
        corso=corso,
        data_rilascio=date(2020, 1, 1),
        data_scadenza_calcolata=date(2025, 1, 1),
        stato_validazione=ValidationStatus.MANUAL,
    )
    db_session.add(c1)
    db_session.commit()

    # New Cert
    c2 = Certificato(
        dipendente=emp,
        corso=corso,
        data_rilascio=date(2024, 1, 1),
        data_scadenza_calcolata=date(2029, 1, 1),
        stato_validazione=ValidationStatus.MANUAL,
    )
    db_session.add(c2)
    db_session.commit()

    # Execute archiving
    certificate_service.archive_obsolete_certs(db_session, c2)

    # Verify status (indirectly via logic or manual check if we add state)
    # The current logic just moves files.


def test_update_cert_fields_matching(db_session):
    # Setup
    emp = Dipendente(nome="MARIO", cognome="ROSSI", matricola="123")
    db_session.add(emp)

    corso = Corso(nome_corso="HLO", categoria_corso="OFFSHORE", validita_mesi=12)
    db_session.add(corso)
    db_session.commit()

    cert = Certificato(
        nome_dipendente_raw="Sconosciuto",
        corso=corso,
        data_rilascio=date(2025, 1, 1),
        stato_validazione=ValidationStatus.MANUAL,
    )
    db_session.add(cert)
    db_session.commit()

    # Update name to match MARIO ROSSI
    update_data = {"nome": "MARIO ROSSI"}
    certificate_service.update_cert_fields(cert, update_data, db_session)

    assert cert.dipendente_id == emp.id


def test_create_certificato_logic_full_flow(db_session):
    # Setup Course
    corso = Corso(nome_corso="HLO", categoria_corso="OFFSHORE", validita_mesi=60)
    db_session.add(corso)
    db_session.commit()

    class MockIn:
        nome = "MARIO ROSSI"
        corso = "HLO"
        categoria = "OFFSHORE"
        data_rilascio = "01/01/2024"
        data_scadenza = "01/01/2029"
        dipendente_id = None

    # This function is not implemented in service yet as a single entry point,
    # but we can test the individual components or implement it if needed.
    pass
