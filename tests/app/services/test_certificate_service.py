from datetime import date

import pytest

from app.db.models import Certificato, Corso
from app.services import certificate_service


def test_validate_cert_input_valid():
    class MockCert:
        def __init__(self):
            self.nome = "Mario Rossi"
            self.data_rilascio = "14/11/2025"

    # Should not raise
    certificate_service.validate_cert_input(MockCert())


def test_validate_cert_input_invalid_name():
    class MockCert:
        def __init__(self):
            self.nome = "Mario"  # Missing surname
            self.data_rilascio = "14/11/2025"

    with pytest.raises(Exception) as exc:
        certificate_service.validate_cert_input(MockCert())
    assert "Formato nome non valido" in str(exc.value)


def test_get_or_create_course(db_session):
    # 1. Create via service
    course = certificate_service.get_or_create_course(db_session, "SICUREZZA", "Corso Base")
    assert course.nome_corso == "Corso Base"
    assert course.categoria_corso == "SICUREZZA"

    # 2. Get existing
    course2 = certificate_service.get_or_create_course(db_session, "SICUREZZA", "Corso Base")
    assert course.id == course2.id


def test_check_duplicate_cert(db_session):
    course = Corso(nome_corso="Test", categoria_corso="CAT", validita_mesi=12)
    db_session.add(course)
    db_session.commit()

    # Not duplicate initially
    assert not certificate_service.check_duplicate_cert(
        db_session, course.id, date(2025, 1, 1), None, "Mario Rossi"
    )

    # Add one
    cert = Certificato(
        corso_id=course.id, data_rilascio=date(2025, 1, 1), nome_dipendente_raw="Mario Rossi"
    )
    db_session.add(cert)
    db_session.commit()

    # Now it's a duplicate
    assert certificate_service.check_duplicate_cert(
        db_session, course.id, date(2025, 1, 1), None, "Mario Rossi"
    )
