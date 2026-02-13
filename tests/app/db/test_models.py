from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.db.models import Certificato, Corso, Dipendente, ValidationStatus


def test_create_dipendente(db_session):
    dip = Dipendente(
        nome="Mario", cognome="Rossi", matricola="12345", data_nascita=date(1980, 1, 1)
    )
    db_session.add(dip)
    db_session.commit()

    assert dip.id is not None
    assert dip.nome == "Mario"


def test_dipendente_matricola_unique(db_session):
    dip1 = Dipendente(nome="A", cognome="B", matricola="U1", data_nascita=date(1990, 1, 1))
    db_session.add(dip1)
    db_session.commit()

    dip2 = Dipendente(nome="C", cognome="D", matricola="U1", data_nascita=date(1991, 1, 1))
    db_session.add(dip2)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_create_corso(db_session):
    corso = Corso(nome_corso="Test Course", validita_mesi=12, categoria_corso="TEST")
    db_session.add(corso)
    db_session.commit()

    assert corso.id is not None
    assert corso.nome_corso == "Test Course"


def test_corso_unique_constraint(db_session):
    """Test composite unique constraint on nome_corso and categoria_corso"""
    c1 = Corso(nome_corso="A", categoria_corso="CAT1", validita_mesi=12)
    db_session.add(c1)
    db_session.commit()

    c2 = Corso(nome_corso="A", categoria_corso="CAT1", validita_mesi=24)
    db_session.add(c2)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_create_certificato(db_session):
    dip = Dipendente(nome="M", cognome="R", matricola="001", data_nascita=date(1980, 1, 1))
    corso = Corso(nome_corso="C1", categoria_corso="CAT1", validita_mesi=12)
    db_session.add_all([dip, corso])
    db_session.commit()

    cert = Certificato(
        dipendente_id=dip.id,
        corso_id=corso.id,
        data_rilascio=date(2023, 1, 1),
        data_scadenza_calcolata=date(2024, 1, 1),
        stato_validazione=ValidationStatus.AUTOMATIC,
    )
    db_session.add(cert)
    db_session.commit()

    assert cert.id is not None
    assert cert.dipendente == dip
    assert cert.corso == corso


def test_orphan_certificato(db_session):
    corso = Corso(nome_corso="C1", categoria_corso="CAT1", validita_mesi=12)
    db_session.add(corso)
    db_session.commit()

    cert = Certificato(
        dipendente_id=None,
        nome_dipendente_raw="John Doe",
        corso_id=corso.id,
        data_rilascio=date(2023, 1, 1),
        stato_validazione=ValidationStatus.MANUAL,
    )
    db_session.add(cert)
    db_session.commit()

    assert cert.id is not None
    assert cert.dipendente is None
    assert cert.nome_dipendente_raw == "John Doe"
