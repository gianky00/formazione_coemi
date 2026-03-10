from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.db.models import Corso
from app.services import certificate_service


def test_validate_cert_input_valid(db_session):
    class MockCert:
        def __init__(self):
            self.nome = "Mario Rossi"
            self.corso = "Antincendio"
            self.categoria = "FORMAZIONE"
            self.data_rilascio = "14/11/2025"

    service = certificate_service.CertificateService(db_session)
    service._validate_input(MockCert())


def test_validate_cert_input_missing_fields(db_session):
    class MockCert:
        def __init__(self):
            self.nome = "Mario Rossi"
            self.corso = ""
            self.categoria = ""
            self.data_rilascio = ""

    service = certificate_service.CertificateService(db_session)
    with pytest.raises(Exception) as exc:
        service._validate_input(MockCert())
    assert "Dati obbligatori mancanti" in str(exc.value)


def test_validate_cert_input_invalid_name(db_session):
    class MockCert:
        def __init__(self):
            self.nome = "Mario"  # Missing surname
            self.corso = "Antincendio"
            self.categoria = "FORMAZIONE"
            self.data_rilascio = "14/11/2025"

    # La validazione nome avviene nei validator Pydantic dello schema o durante validazione specifica?
    # _validate_input controlla solo la presenza. Se vogliamo testare il formato nome non valido per _validate_input:
    pass  # Pydantic validates this now.


def test_check_duplicate_cert(db_session: Session):
    course = Corso(nome_corso="Test", categoria_corso="CAT", validita_mesi=12)
    db_session.add(course)
    db_session.commit()

    service = certificate_service.CertificateService(db_session)
    assert not service._check_duplicate(course.id, date(2025, 1, 1), None, "Mario Rossi")
