from datetime import date, datetime
from unittest.mock import patch
from sqlalchemy.orm import Session
from app.db.models import Certificato, Dipendente, Corso
from app.services.certificate_logic import calculate_expiration_date, get_certificate_status

def test_calculate_expiration_date():
    """
    Testa la funzione di calcolo della data di scadenza.
    """
    issue_date = date(2025, 1, 1)
    assert calculate_expiration_date(issue_date, 12) == date(2026, 1, 1)
    assert calculate_expiration_date(issue_date, 0) is None

def test_calculate_expiration_date_returns_date_object():
    """
    Tests that calculate_expiration_date returns a date object, not a datetime object,
    even when a datetime object is passed as input.
    """
    # Using a datetime object to expose the bug
    issue_date = datetime(2022, 1, 1, 8, 30, 0)
    validity_months = 12
    expiration_date = calculate_expiration_date(issue_date, validity_months)
    # This assertion should fail before the fix because it will return a datetime object
    assert type(expiration_date) == date

def test_calculate_expiration_none():
    """
    Bug 1: calculate_expiration_date crashes if issue_date is None.
    Expectation: Return None.
    """
    assert calculate_expiration_date(None, 12) is None

def test_get_certificate_status(db_session: Session):
    """
    Testa gli stati 'attivo' e 'scaduto'.
    """
    dipendente = Dipendente(nome="Test", cognome="User")
    corso = Corso(nome_corso="Test Corso", validita_mesi=12, categoria_corso="Test Categoria")
    scaduto_dipendente = Dipendente(nome="Scaduto", cognome="User")
    db_session.add_all([dipendente, corso, scaduto_dipendente])
    db_session.commit()

    # Certificato attivo
    cert_attivo = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date.today(),
        data_scadenza_calcolata=date.today() + date.resolution * 100
    )
    # Certificato scaduto (senza rinnovi)
    cert_scaduto = Certificato(
        dipendente_id=scaduto_dipendente.id,
        corso_id=corso.id,
        data_rilascio=date(2020, 1, 1),
        data_scadenza_calcolata=date(2021, 1, 1)
    )
    # Certificato senza scadenza
    cert_no_scadenza = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date(2020, 1, 1),
        data_scadenza_calcolata=None
    )
    db_session.add_all([cert_attivo, cert_scaduto, cert_no_scadenza])
    db_session.commit()

    assert get_certificate_status(db_session, cert_attivo) == "attivo"
    assert get_certificate_status(db_session, cert_scaduto) == "scaduto"
    assert get_certificate_status(db_session, cert_no_scadenza) == "attivo"

def test_get_certificate_status_archiviato(db_session: Session):
    """
    Testa che lo stato di un certificato scaduto sia 'archiviato' se ne esiste uno più recente.
    """
    dipendente = Dipendente(nome="Rinnovato", cognome="User")
    corso = Corso(nome_corso="Corso Rinnovabile", validita_mesi=12, categoria_corso="Rinnovabile")
    db_session.add_all([dipendente, corso])
    db_session.commit()

    # Certificato vecchio (scaduto)
    cert_vecchio = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date(2020, 1, 1),
        data_scadenza_calcolata=date(2021, 1, 1)
    )
    # Certificato nuovo (attivo)
    cert_nuovo = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date(2021, 1, 1),
        data_scadenza_calcolata=date.today() + date.resolution * 100 # Scadenza futura
    )
    db_session.add_all([cert_vecchio, cert_nuovo])
    db_session.commit()

    assert get_certificate_status(db_session, cert_vecchio) == "archiviato"
    assert get_certificate_status(db_session, cert_nuovo) == "attivo"

def test_orphan_certificates_not_renewed_by_others(db_session: Session):
    """
    Test that an expired orphaned certificate for one person is NOT marked as 'archiviato'
    just because there is a newer orphaned certificate for ANOTHER person.
    """
    # Create a course
    corso = Corso(nome_corso="Safety First", validita_mesi=12, categoria_corso="SAFETY")
    db_session.add(corso)
    db_session.commit()

    # Create expired orphan certificate for "Alice"
    cert_alice = Certificato(
        dipendente_id=None,
        nome_dipendente_raw="Alice",
        corso_id=corso.id,
        data_rilascio=date(2020, 1, 1),
        data_scadenza_calcolata=date(2021, 1, 1)
    )

    # Create newer valid orphan certificate for "Bob"
    cert_bob = Certificato(
        dipendente_id=None,
        nome_dipendente_raw="Bob",
        corso_id=corso.id,
        data_rilascio=date(2024, 1, 1),
        data_scadenza_calcolata=date(2030, 1, 1)
    )

    db_session.add_all([cert_alice, cert_bob])
    db_session.commit()

    # Check status of Alice's certificate
    # It should be "scaduto" because Bob's certificate has nothing to do with Alice
    # And orphans cannot renew other orphans
    status = get_certificate_status(db_session, cert_alice)

    assert status == "scaduto", f"Expected 'scaduto' but got '{status}'. Orphaned certificates are being mixed up!"

def test_infinite_validity_status(db_session: Session):
    """
    Testa che i certificati con validità infinita (data_scadenza_calcolata=None)
    siano sempre 'attivo' se non c'è una scadenza esplicita, anche se sono vecchi.
    """
    dipendente = Dipendente(nome="Infinite", cognome="User")
    corso = Corso(nome_corso="Nomina", validita_mesi=0, categoria_corso="NOMINE")
    db_session.add_all([dipendente, corso])
    db_session.commit()

    # Certificato vecchio (2010) ma validità infinita
    cert_vecchio = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date(2010, 1, 1),
        data_scadenza_calcolata=None
    )
    db_session.add(cert_vecchio)
    db_session.commit()

    assert get_certificate_status(db_session, cert_vecchio) == "attivo"

    # Aggiungiamo un certificato PIÙ NUOVO (2020), sempre infinito
    cert_nuovo = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date(2020, 1, 1),
        data_scadenza_calcolata=None
    )
    db_session.add(cert_nuovo)
    db_session.commit()

    assert get_certificate_status(db_session, cert_vecchio) == "attivo"
    assert get_certificate_status(db_session, cert_nuovo) == "attivo"


def test_get_certificate_status_archiviato_by_expired(db_session: Session):
    """
    Testa che lo stato di un certificato scaduto sia 'archiviato' anche se quello
    più recente che lo sostituisce è anch'esso scaduto.
    """
    dipendente = Dipendente(nome="RinnovatoHistory", cognome="User")
    corso = Corso(nome_corso="Corso Storico", validita_mesi=12, categoria_corso="Storico")
    db_session.add_all([dipendente, corso])
    db_session.commit()

    # Certificato A (2020-2021) - Scaduto
    cert_a = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date(2020, 1, 1),
        data_scadenza_calcolata=date(2021, 1, 1)
    )
    # Certificato B (2021-2022) - Scaduto (ma più recente di A)
    cert_b = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date(2021, 1, 1),
        data_scadenza_calcolata=date(2022, 1, 1)
    )

    db_session.add_all([cert_a, cert_b])
    db_session.commit()

    # A dovrebbe essere 'archiviato' perché esiste B (anche se scaduto)
    assert get_certificate_status(db_session, cert_a) == "archiviato"
    # B dovrebbe essere 'scaduto' perché è l'ultimo
    assert get_certificate_status(db_session, cert_b) == "scaduto"


def test_user_scenario_chain_ending_valid(db_session: Session):
    """
    Scenario 1: Catena di certificati dove l'ultimo è valido.
    Tutti i precedenti devono essere 'archiviato' (Archiviato).
    L'ultimo deve essere 'attivo'.
    """
    dipendente = Dipendente(nome="Mario", cognome="Rossi_Valid")
    corso = Corso(nome_corso="Antincendio", validita_mesi=24, categoria_corso="Sicurezza")
    db_session.add_all([dipendente, corso])
    db_session.commit()

    years = [2015, 2017, 2019, 2021, 2023]
    certs = []

    # Crea certificati scaduti (storico)
    for year in years:
        cert = Certificato(
            dipendente_id=dipendente.id,
            corso_id=corso.id,
            data_rilascio=date(year, 1, 1),
            data_scadenza_calcolata=date(year + 2, 1, 1)
        )
        certs.append(cert)

    # Crea ultimo certificato valido (es. 2025, scade 2027)
    # Assumiamo che 'oggi' sia prima del 2027.
    # Per sicurezza, usiamo date relative a 'today' per il test robusto,
    # ma per seguire lo scenario utente usiamo date fisse future per l'ultimo.
    today_year = date.today().year
    # Se siamo nel 2025 o dopo, questo funziona. Se siamo nel 2024, 2025 è futuro.
    # Forziamo date relative per garantire il test passi sempre.

    # Simuliamo la catena storica
    # ... 2015, 2017 ...
    # L'ultimo deve essere VALIDO (data scadenza > oggi).

    valid_cert = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date.today(), # Rilasciato oggi
        data_scadenza_calcolata=date.today().replace(year=date.today().year + 2) # Scade tra 2 anni
    )
    certs.append(valid_cert)

    db_session.add_all(certs)
    db_session.commit()

    # Verifica: Tutti tranne l'ultimo devono essere 'archiviato'
    for i, cert in enumerate(certs[:-1]):
        status = get_certificate_status(db_session, cert)
        assert status == "archiviato", f"Il certificato {i} ({cert.data_rilascio}) dovrebbe essere 'archiviato', invece è '{status}'"

    # Verifica: L'ultimo deve essere 'attivo'
    last_status = get_certificate_status(db_session, certs[-1])
    assert last_status == "attivo", f"L'ultimo certificato dovrebbe essere 'attivo', invece è '{last_status}'"


def test_user_scenario_chain_ending_expired(db_session: Session):
    """
    Scenario 2: Catena di certificati dove anche l'ultimo è scaduto.
    Tutti i precedenti devono essere 'archiviato' (Archiviato).
    L'ultimo deve essere 'scaduto'.
    """
    dipendente = Dipendente(nome="Mario", cognome="Rossi_Expired")
    corso = Corso(nome_corso="Antincendio B", validita_mesi=24, categoria_corso="Sicurezza B")
    db_session.add_all([dipendente, corso])
    db_session.commit()

    # Creiamo una catena dove TUTTI sono scaduti rispetto ad oggi
    # Assumiamo oggi = 2025 (o reale).
    # Creiamo certificati nel passato remoto.

    today = date.today()
    base_year = today.year - 12 # 12 anni fa

    certs = []
    for i in range(5):
        release_year = base_year + (i * 2) # es. 2013, 2015, 2017, 2019, 2021
        cert = Certificato(
            dipendente_id=dipendente.id,
            corso_id=corso.id,
            data_rilascio=date(release_year, 1, 1),
            data_scadenza_calcolata=date(release_year + 2, 1, 1)
        )
        certs.append(cert)

    # Assicuriamoci che l'ultimo sia effettivamente scaduto
    assert certs[-1].data_scadenza_calcolata < today, "Errore nel setup del test: l'ultimo certificato deve essere scaduto"

    db_session.add_all(certs)
    db_session.commit()

    # Verifica: Tutti tranne l'ultimo devono essere 'archiviato'
    for i, cert in enumerate(certs[:-1]):
        status = get_certificate_status(db_session, cert)
        assert status == "archiviato", f"Il certificato {i} ({cert.data_rilascio}) dovrebbe essere 'archiviato', invece è '{status}'"

    # Verifica: L'ultimo deve essere 'scaduto'
    last_status = get_certificate_status(db_session, certs[-1])
    assert last_status == "scaduto", f"L'ultimo certificato dovrebbe essere 'scaduto', invece è '{last_status}'"
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
