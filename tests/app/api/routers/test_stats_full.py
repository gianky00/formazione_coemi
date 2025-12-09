import pytest
from unittest.mock import MagicMock
from app.db.models import User

# We will implement real tests using the DB session rather than mocking everything,
# as it's more robust for "integration" style router tests.

from app.db.models import Certificato, Dipendente, Corso, ValidationStatus
from datetime import date, timedelta
from app.core.config import settings

def create_stats_data(db):
    # Dipendenti
    d1 = Dipendente(nome="D1", cognome="C1", matricola="1")
    d2 = Dipendente(nome="D2", cognome="C2", matricola="2")
    db.add_all([d1, d2])
    db.commit()

    # Corso
    c1 = Corso(nome_corso="C1", categoria_corso="CAT1", validita_mesi=12)
    db.add(c1)
    db.commit()

    # Certificati
    today = date.today()
    threshold = today + timedelta(days=settings.ALERT_THRESHOLD_DAYS)

    # 1. Valid (Active)
    cert1 = Certificato(
        dipendente_id=d1.id, corso_id=c1.id,
        data_rilascio=date(2023, 1, 1),
        data_scadenza_calcolata=today + timedelta(days=365),
        stato_validazione=ValidationStatus.MANUAL
    )

    # 2. Expiring (In Scadenza)
    cert2 = Certificato(
        dipendente_id=d2.id, corso_id=c1.id,
        data_rilascio=date(2023, 1, 1),
        data_scadenza_calcolata=today + timedelta(days=5),
        stato_validazione=ValidationStatus.MANUAL
    )

    # 3. Expired (Scaduto)
    cert3 = Certificato(
        dipendente_id=d1.id, corso_id=c1.id,
        data_rilascio=date(2020, 1, 1),
        data_scadenza_calcolata=today - timedelta(days=1),
        stato_validazione=ValidationStatus.MANUAL
    )

    db.add_all([cert1, cert2, cert3])
    db.commit()

def test_get_stats_summary_logic(test_client, db_session, admin_token_headers):
    create_stats_data(db_session)

    response = test_client.get("/stats/summary", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total_dipendenti"] == 2
    assert data["total_certificati"] == 3
    assert data["scaduti"] == 1
    assert data["in_scadenza"] == 1
    assert data["validi"] == 1 # cert1
    # Compliance: (3 - 1) / 3 = 66%
    assert data["compliance_percent"] == 66

def test_get_compliance_by_category_logic(test_client, db_session, admin_token_headers):
    create_stats_data(db_session)

    response = test_client.get("/stats/compliance", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    cat = data[0]
    assert cat["category"] == "CAT1"
    assert cat["total"] == 3
    assert cat["expired"] == 1  # Updated field name
    assert "active" in cat  # New field
    assert "expiring" in cat  # New field
    assert cat["compliance"] >= 0
