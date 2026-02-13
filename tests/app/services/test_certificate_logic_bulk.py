from datetime import date

from sqlalchemy.orm import Session

from app.db.models import Certificato, Corso, Dipendente
from app.services.certificate_logic import get_bulk_certificate_statuses


def test_get_bulk_certificate_statuses(db_session: Session):
    """
    Testa la funzione bulk per il calcolo degli stati.
    """
    dipendente = Dipendente(nome="Bulk", cognome="User")
    corso = Corso(nome_corso="Bulk Corso", validita_mesi=12, categoria_corso="Bulk Cat")
    db_session.add_all([dipendente, corso])
    db_session.commit()

    # 1. Certificato Scaduto (Vecchio) -> Deve essere ARCHIVIATO perché esiste il 2
    cert1 = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date(2020, 1, 1),
        data_scadenza_calcolata=date(2021, 1, 1),
        stato_validazione="AUTOMATIC",
    )

    # 2. Certificato Attivo (Nuovo) -> Deve essere ATTIVO
    cert2 = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date.today(),
        data_scadenza_calcolata=date.today().replace(year=date.today().year + 1),
        stato_validazione="AUTOMATIC",
    )

    # 3. Certificato Orfano Scaduto -> SCADUTO (non può essere archiviato da nessuno)
    cert3 = Certificato(
        dipendente_id=None,
        corso_id=corso.id,
        data_rilascio=date(2019, 1, 1),
        data_scadenza_calcolata=date(2020, 1, 1),
        stato_validazione="AUTOMATIC",
    )

    db_session.add_all([cert1, cert2, cert3])
    db_session.commit()

    # Refresh to ensure relationships are loaded (though logic handles lazy load via joins usually)
    # The function expects 'corso' to be joined or access triggers it.
    # In unit tests with SQLite, eager loading config in API isn't present, so access might trigger lazy load.
    # But get_bulk... query uses join explicitely.

    certs = [cert1, cert2, cert3]

    status_map = get_bulk_certificate_statuses(db_session, certs)

    assert status_map[cert1.id] == "archiviato", (
        f"Cert1 should be archiviato, got {status_map[cert1.id]}"
    )
    assert status_map[cert2.id] == "attivo", f"Cert2 should be attivo, got {status_map[cert2.id]}"
    assert status_map[cert3.id] == "scaduto", f"Cert3 should be scaduto, got {status_map[cert3.id]}"


def test_get_bulk_certificate_statuses_complex_chain(db_session: Session):
    """
    Testa una catena complessa con bulk logic.
    """
    dip = Dipendente(nome="Chain", cognome="Bulk")
    cat = "SICUREZZA"
    corso = Corso(nome_corso="Sicurezza", validita_mesi=12, categoria_corso=cat)
    db_session.add_all([dip, corso])
    db_session.commit()

    # A: 2018 (Scaduto) -> Archiviato
    c1 = Certificato(
        dipendente_id=dip.id,
        corso_id=corso.id,
        data_rilascio=date(2018, 1, 1),
        data_scadenza_calcolata=date(2019, 1, 1),
        stato_validazione="AUTOMATIC",
    )
    # B: 2019 (Scaduto) -> Archiviato
    c2 = Certificato(
        dipendente_id=dip.id,
        corso_id=corso.id,
        data_rilascio=date(2019, 1, 1),
        data_scadenza_calcolata=date(2020, 1, 1),
        stato_validazione="AUTOMATIC",
    )
    # C: 2020 (Scaduto) -> Scaduto (è l'ultimo!)
    c3 = Certificato(
        dipendente_id=dip.id,
        corso_id=corso.id,
        data_rilascio=date(2020, 1, 1),
        data_scadenza_calcolata=date(2021, 1, 1),
        stato_validazione="AUTOMATIC",
    )

    db_session.add_all([c1, c2, c3])
    db_session.commit()

    status_map = get_bulk_certificate_statuses(db_session, [c1, c2, c3])

    assert status_map[c1.id] == "archiviato"
    assert status_map[c2.id] == "archiviato"
    assert status_map[c3.id] == "scaduto"  # Perché è l'ultimo, anche se scaduto.
