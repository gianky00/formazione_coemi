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
