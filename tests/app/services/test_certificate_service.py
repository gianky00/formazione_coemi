from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.db.models import Corso
from app.services import certificate_service


def test_validate_cert_input_valid():
    class MockCert:
        def __init__(self):
            self.nome = "Mario Rossi"
            self.corso = "Antincendio"
            self.categoria = "FORMAZIONE"
            self.data_rilascio = "14/11/2025"

    # Should not raise
    certificate_service.validate_cert_input(MockCert())


def test_validate_cert_input_missing_fields():
    class MockCert:
        def __init__(self):
            self.nome = "Mario Rossi"
            # missing other fields

    with pytest.raises(Exception) as exc:
        certificate_service.validate_cert_input(MockCert())
    assert "Dati obbligatori mancanti" in str(exc.value)


def test_validate_cert_input_invalid_name():
    class MockCert:
        def __init__(self):
            self.nome = "Mario"  # Missing surname
            self.corso = "Antincendio"
            self.categoria = "FORMAZIONE"
            self.data_rilascio = "14/11/2025"

    with pytest.raises(Exception) as exc:
        certificate_service.validate_cert_input(MockCert())
    assert "Formato nome non valido" in str(exc.value)


def test_check_duplicate_cert(db_session: Session):
    course = Corso(nome_corso="Test", categoria_corso="CAT", validita_mesi=12)
    db_session.add(course)
    db_session.commit()

    # Not duplicate initially
    assert not certificate_service.check_duplicate_cert(
        db_session, course.id, date(2025, 1, 1), None, "Mario Rossi"
    )
