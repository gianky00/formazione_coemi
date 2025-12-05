from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from app.db.seeding import migrate_schema
from app.db.models import Base

def test_migrate_schema_adds_column():
    # 1. Setup in-memory DB
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    db = Session()

    # 2. Create 'users' table manually WITHOUT 'previous_login'
    # Mimic the old schema
    db.execute(text("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username VARCHAR NOT NULL,
            hashed_password VARCHAR NOT NULL,
            account_name VARCHAR,
            is_admin BOOLEAN,
            last_login DATETIME,
            created_at DATETIME
        )
    """))
    # Also create 'audit_logs' table (even if empty) because migrate_schema runs backfill queries on it
    db.execute(text("""
        CREATE TABLE audit_logs (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            username VARCHAR,
            action VARCHAR,
            details VARCHAR,
            timestamp DATETIME
        )
    """))
    db.commit()

    # Verify column is missing
    result = db.execute(text("PRAGMA table_info(users)"))
    columns = [row[1] for row in result.fetchall()]
    assert 'previous_login' not in columns

    # 3. Run Migration
    migrate_schema(db)

    # 4. Verify column exists
    result = db.execute(text("PRAGMA table_info(users)"))
    columns = [row[1] for row in result.fetchall()]
    assert 'previous_login' in columns

    db.close()

def test_smart_backfill_categories():
    # 1. Setup
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    db = Session()

    # Create audit_logs table OLD schema (no category)
    db.execute(text("""
        CREATE TABLE audit_logs (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            username VARCHAR,
            action VARCHAR,
            details VARCHAR,
            timestamp DATETIME
        )
    """))

    # Insert historical data
    db.execute(text("INSERT INTO audit_logs (action, username) VALUES ('CERTIFICATE_CREATE', 'admin')"))
    db.execute(text("INSERT INTO audit_logs (action, username) VALUES ('LOGIN', 'admin')"))
    db.execute(text("INSERT INTO audit_logs (action, username) VALUES ('UNKNOWN_ACTION', 'admin')"))
    db.commit()

    # 2. Run Migration
    migrate_schema(db)

    # 3. Verify Backfill
    rows = db.execute(text("SELECT action, category FROM audit_logs")).fetchall()
    # Convert to dict for easy checking
    data = {row[0]: row[1] for row in rows}

    assert data['CERTIFICATE_CREATE'] == 'CERTIFICATE'
    assert data['LOGIN'] == 'AUTH'
    assert data['UNKNOWN_ACTION'] == 'GENERAL'

    db.close()
