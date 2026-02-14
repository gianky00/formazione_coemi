from datetime import date

import pytest

from app.db.models import Certificato, Corso, Dipendente, ValidationStatus
from app.services.chat_service import ChatService


@pytest.fixture
def chat_svc():
    return ChatService()


def test_get_rag_context_with_employee_match(db_session, chat_svc):
    # Setup
    e1 = Dipendente(nome="MARIO", cognome="ROSSI", matricola="123")
    c1 = Corso(nome_corso="ANTINCENDIO", categoria_corso="FORMAZIONE", validita_mesi=60)
    db_session.add_all([e1, c1])
    db_session.flush()

    cert = Certificato(
        dipendente_id=e1.id,
        corso_id=c1.id,
        data_rilascio=date(2020, 1, 1),
        stato_validazione=ValidationStatus.MANUAL,
    )
    db_session.add(cert)
    db_session.commit()

    context = chat_svc.get_rag_context(db_session, MagicUser(), query="Mario Rossi")
    assert "ROSSI M." in context or "ROSSI MARIO" in context


class MagicUser:
    username = "admin"
    is_admin = True
