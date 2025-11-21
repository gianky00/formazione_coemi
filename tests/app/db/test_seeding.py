from app.db.seeding import seed_database
from app.db.models import Corso

def test_seed_database(db_session):
    # Run seeding
    seed_database(db_session)

    # Verify total count (approximate based on known list, at least 30)
    count = db_session.query(Corso).count()
    assert count >= 30

    # Verify specific courses
    antincendio = db_session.query(Corso).filter_by(nome_corso="ANTINCENDIO").first()
    assert antincendio is not None
    assert antincendio.validita_mesi == 60
    assert antincendio.categoria_corso == "ANTINCENDIO"

    blsd = db_session.query(Corso).filter_by(nome_corso="BLSD").first()
    assert blsd is not None
    assert blsd.validita_mesi == 12

def test_seed_idempotency(db_session):
    """Verify that running seed twice doesn't duplicate data."""
    seed_database(db_session)
    count_1 = db_session.query(Corso).count()

    seed_database(db_session)
    count_2 = db_session.query(Corso).count()

    assert count_1 == count_2
