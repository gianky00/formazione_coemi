import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from app.db.seeding import seed_database, migrate_schema
from app.db.session import get_db
from app.db.models import User, Corso
from app.core import security

def test_seed_database_new_admin(db_session):
    # Ensure no admin
    db_session.query(User).delete()
    db_session.commit()

    with patch("app.db.seeding.SessionLocal", return_value=db_session):
        seed_database()

    admin = db_session.query(User).filter_by(username="admin").first()
    assert admin is not None
    assert admin.is_admin

def test_seed_database_update_admin_password(db_session):
    # Create admin with old password
    old_pw = security.get_password_hash("old")
    admin = User(username="admin", hashed_password=old_pw, is_admin=True)
    db_session.add(admin)
    db_session.commit()

    # Configure new password in settings
    with patch("app.db.seeding.settings") as mock_settings, \
         patch("app.db.seeding.SessionLocal", return_value=db_session):

         mock_settings.FIRST_RUN_ADMIN_USERNAME = "admin"
         mock_settings.FIRST_RUN_ADMIN_PASSWORD = "new_secret_pw"

         # Pass db_session explicitly to avoid closure
         seed_database(db=db_session)

    db_session.refresh(admin)
    assert security.verify_password("new_secret_pw", admin.hashed_password)

def test_seed_database_courses(db_session):
    # Pass db_session explicitly
    seed_database(db=db_session)

    courses = db_session.query(Corso).all()
    assert len(courses) > 0
    assert any(c.nome_corso == "ANTINCENDIO" for c in courses)

def test_migrate_schema_columns():
    mock_db = MagicMock()
    # Mock table_info returning list of existing columns (but missing 'previous_login')
    # Format: (cid, name, type, notnull, dflt_value, pk)
    mock_db.execute.return_value.fetchall.return_value = [
        (0, 'id', 'INTEGER', 1, None, 1),
        (1, 'username', 'VARCHAR', 1, None, 0)
    ]

    migrate_schema(mock_db)

    # Verify ALTER TABLE calls
    sql_executed = []
    for call in mock_db.execute.mock_calls:
        if call.args:
            sql_executed.append(str(call.args[0]))

    assert any("previous_login" in sql for sql in sql_executed)

def test_get_db_yields_session():
    # Verify the generator
    gen = get_db()
    session = next(gen)
    assert session is not None
    try:
        next(gen)
    except StopIteration:
        pass
    session.close()
