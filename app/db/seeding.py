from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.models import Corso, User, Certificato
from app.db.session import SessionLocal
from app.core.security import get_password_hash
from app.core.config import settings

def migrate_schema(db: Session):
    """
    Checks for missing columns in existing tables (due to lack of migrations)
    and adds them using raw SQL. Specifically handles 'previous_login'.
    """
    try:
        # Check columns in users table
        # PRAGMA table_info returns: (cid, name, type, notnull, dflt_value, pk)
        result = db.execute(text("PRAGMA table_info(users)"))
        # Accessing by index because RowProxy behavior depends on SQLAlchemy version
        columns = [row[1] for row in result.fetchall()]

        if columns and 'previous_login' not in columns:
            # Add the column if missing
            print("Migrating schema: Adding previous_login to users table...")
            db.execute(text("ALTER TABLE users ADD COLUMN previous_login DATETIME"))
            db.commit()

        if columns and 'last_login' not in columns:
            print("Migrating schema: Adding last_login to users table...")
            db.execute(text("ALTER TABLE users ADD COLUMN last_login DATETIME"))
            db.commit()

        if columns and 'gender' not in columns:
            print("Migrating schema: Adding gender to users table...")
            db.execute(text("ALTER TABLE users ADD COLUMN gender VARCHAR"))
            db.commit()

        # Check columns in audit_logs table
        result = db.execute(text("PRAGMA table_info(audit_logs)"))
        audit_columns = [row[1] for row in result.fetchall()]

        if audit_columns and 'category' not in audit_columns:
            print("Migrating schema: Adding category to audit_logs table...")
            db.execute(text("ALTER TABLE audit_logs ADD COLUMN category VARCHAR"))
            db.commit()

        if audit_columns and 'ip_address' not in audit_columns:
            print("Migrating schema: Adding security columns to audit_logs table...")
            try:
                db.execute(text("ALTER TABLE audit_logs ADD COLUMN ip_address VARCHAR"))
                db.execute(text("ALTER TABLE audit_logs ADD COLUMN user_agent VARCHAR"))
                db.execute(text("ALTER TABLE audit_logs ADD COLUMN geolocation VARCHAR"))
                db.execute(text("ALTER TABLE audit_logs ADD COLUMN severity VARCHAR DEFAULT 'LOW'"))
                db.commit()
            except Exception as e:
                print(f"Error adding security columns: {e}")
                db.rollback()

            # Update existing rows to have LOW severity if needed (though DEFAULT handles new inserts, existing rows get NULL usually unless DEFAULT is supported in ALTER which varies by DB, SQLite supports it)
            db.execute(text("UPDATE audit_logs SET severity = 'LOW' WHERE severity IS NULL"))
            db.commit()

        if audit_columns and 'device_id' not in audit_columns:
            print("Migrating schema: Adding extended security columns (device_id, changes) to audit_logs table...")
            try:
                db.execute(text("ALTER TABLE audit_logs ADD COLUMN device_id VARCHAR"))
                db.execute(text("ALTER TABLE audit_logs ADD COLUMN changes VARCHAR"))
                db.commit()
            except Exception as e:
                print(f"Error adding extended security columns: {e}")
                db.rollback()

        # Check columns in dipendenti table
        result = db.execute(text("PRAGMA table_info(dipendenti)"))
        dipendenti_columns = [row[1] for row in result.fetchall()]

        if dipendenti_columns and 'email' not in dipendenti_columns:
            print("Migrating schema: Adding email to dipendenti table...")
            try:
                db.execute(text("ALTER TABLE dipendenti ADD COLUMN email VARCHAR"))
                db.execute(text("CREATE UNIQUE INDEX ix_dipendenti_email ON dipendenti (email)"))
                db.commit()
            except Exception as e:
                print(f"Error adding email column: {e}")
                db.rollback()

        if dipendenti_columns and 'data_assunzione' not in dipendenti_columns:
            print("Migrating schema: Adding data_assunzione to dipendenti table...")
            try:
                db.execute(text("ALTER TABLE dipendenti ADD COLUMN data_assunzione DATE"))
                db.commit()
            except Exception as e:
                print(f"Error adding data_assunzione column: {e}")
                db.rollback()

        # Ensure indexes exist for performance (Brute force detection queries timestamp and ip_address)
        try:
            db.execute(text("CREATE INDEX IF NOT EXISTS ix_audit_logs_timestamp ON audit_logs (timestamp)"))
            db.execute(text("CREATE INDEX IF NOT EXISTS ix_audit_logs_ip_address ON audit_logs (ip_address)"))
            db.commit()
        except Exception as e:
            print(f"Error creating indexes: {e}")
            # Non-fatal, might already exist or DB doesn't support IF NOT EXISTS (SQLite does)
            db.rollback()

        # Backfill existing logs with 'GENERAL' category if null
        db.execute(text("UPDATE audit_logs SET category = 'GENERAL' WHERE category IS NULL"))

        # Smart Backfill: Fix 'GENERAL' categories based on Action content for historical data
        # CERTIFICATE
        db.execute(text("UPDATE audit_logs SET category = 'CERTIFICATE' WHERE category = 'GENERAL' AND action LIKE 'CERTIFICATE_%'"))

        # AUTH
        db.execute(text("UPDATE audit_logs SET category = 'AUTH' WHERE category = 'GENERAL' AND (action = 'LOGIN' OR action = 'LOGOUT')"))

        # USER_MGMT
        db.execute(text("UPDATE audit_logs SET category = 'USER_MGMT' WHERE category = 'GENERAL' AND (action LIKE 'USER_%' OR action = 'PASSWORD_CHANGE')"))

        # DATA
        db.execute(text("UPDATE audit_logs SET category = 'DATA' WHERE category = 'GENERAL' AND action = 'DIPENDENTI_IMPORT'"))

        # SYSTEM
        db.execute(text("UPDATE audit_logs SET category = 'SYSTEM' WHERE category = 'GENERAL' AND action = 'SYSTEM_ALERT'"))

        # CONFIG
        db.execute(text("UPDATE audit_logs SET category = 'CONFIG' WHERE category = 'GENERAL' AND action = 'CONFIG_UPDATE'"))

        db.commit()

    except Exception as e:
        print(f"Schema migration check failed: {e}")
        db.rollback()

def cleanup_deprecated_data(db: Session):
    """
    Removes data related to deprecated categories like 'MEDICO COMPETENTE'.
    """
    deprecated_category = "MEDICO COMPETENTE"

    try:
        # Find course IDs for this category
        courses = db.query(Corso).filter(Corso.categoria_corso == deprecated_category).all()
        course_ids = [c.id for c in courses]

        if course_ids:
            # Delete Certificates
            deleted_certs = db.query(Certificato).filter(Certificato.corso_id.in_(course_ids)).delete(synchronize_session=False)
            if deleted_certs > 0:
                print(f"Cleanup: Deleted {deleted_certs} certificates for deprecated category '{deprecated_category}'.")

            # Delete Courses
            deleted_courses = db.query(Corso).filter(Corso.id.in_(course_ids)).delete(synchronize_session=False)
            if deleted_courses > 0:
                 print(f"Cleanup: Deleted {deleted_courses} deprecated courses.")

            db.commit()
    except Exception as e:
        print(f"Error during cleanup of deprecated data: {e}")
        db.rollback()

def seed_database(db: Session = None):
    """
    Populates the database with a predefined list of master courses and the default admin user.
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        # --- Run Auto-Migration for missing columns ---
        migrate_schema(db)

        # --- Cleanup Deprecated Data ---
        cleanup_deprecated_data(db)

        # --- Seed Courses ---
        corsi = [
            {"nome_corso": "ANTINCENDIO", "validita_mesi": 60, "categoria_corso": "ANTINCENDIO"}, # 5 anni
            {"nome_corso": "PRIMO SOCCORSO", "validita_mesi": 36, "categoria_corso": "PRIMO SOCCORSO"}, # 3 anni
            {"nome_corso": "ASPP", "validita_mesi": 60, "categoria_corso": "ASPP"}, # 5 anni
            {"nome_corso": "RSPP", "validita_mesi": 60, "categoria_corso": "RSPP"}, # 5 anni
            {"nome_corso": "ATEX", "validita_mesi": 60, "categoria_corso": "ATEX"}, # 5 anni
            {"nome_corso": "BLSD", "validita_mesi": 12, "categoria_corso": "BLSD"}, # 1 anno
            {"nome_corso": "CARROPONTE", "validita_mesi": 60, "categoria_corso": "CARROPONTE"}, # 5 anni
            {"nome_corso": "DIRETTIVA SEVESO", "validita_mesi": 60, "categoria_corso": "DIRETTiva SEVESO"}, # 5 anni
            {"nome_corso": "DIRIGENTI E FORMATORI", "validita_mesi": 60, "categoria_corso": "DIRIGENTI E FORMATORI"}, # 5 anni
            {"nome_corso": "GRU A TORRE E PONTE", "validita_mesi": 60, "categoria_corso": "GRU A TORRE E PONTE"}, # 5 anni
            {"nome_corso": "H2S", "validita_mesi": 60, "categoria_corso": "H2S"}, # 5 anni
            {"nome_corso": "IMBRACATORE", "validita_mesi": 60, "categoria_corso": "IMBRACATORE"}, # 5 anni
            {"nome_corso": "FORMAZIONE GENERICA ART.37", "validita_mesi": 60, "categoria_corso": "FORMAZIONE GENERICA ART.37"}, # 5 anni
            {"nome_corso": "PREPOSTO", "validita_mesi": 24, "categoria_corso": "PREPOSTO"}, # 2 anni
            {"nome_corso": "GRU SU AUTOCARRO", "validita_mesi": 60, "categoria_corso": "GRU SU AUTOCARRO"}, # 5 anni
            {"nome_corso": "PLE", "validita_mesi": 60, "categoria_corso": "PLE"}, # 5 anni
            {"nome_corso": "L5 PES PAV PEI C CANTIERE", "validita_mesi": 60, "categoria_corso": "L5 PES PAV PEI C CANTIERE"}, # 5 anni
            {"nome_corso": "LAVORI IN QUOTA", "validita_mesi": 60, "categoria_corso": "LAVORI IN QUOTA"}, # 5 anni
            {"nome_corso": "MACCHINE OPERATRICI", "validita_mesi": 60, "categoria_corso": "MACCHINE OPERATRICI"}, # 5 anni
            {"nome_corso": "MANITOU P.ROTATIVE", "validita_mesi": 60, "categoria_corso": "MANITOU P.ROTATIVE"}, # 5 anni
            {"nome_corso": "MULETTO CARRELISTI", "validita_mesi": 60, "categoria_corso": "MULETTO CARRELISTI"}, # 5 anni
            {"nome_corso": "SOPRAVVIVENZA E SALVATAGGIO IN MARE", "validita_mesi": 60, "categoria_corso": "SOPRAVVIVENZA E SALVATAGGIO IN MARE"}, # 5 anni
            {"nome_corso": "SPAZI CONFINATI DPI III E AUTORESPIRATORI", "validita_mesi": 60, "categoria_corso": "SPAZI CONFINATI DPI III E AUTORESPIRATORI"}, # 5 anni
            {"nome_corso": "HLO", "validita_mesi": 0, "categoria_corso": "HLO"}, # Sempre valido
            {"nome_corso": "TESSERA HLO", "validita_mesi": 0, "categoria_corso": "TESSERA HLO"}, # Scadenza da PDF
            {"nome_corso": "UNILAV", "validita_mesi": 0, "categoria_corso": "UNILAV"}, # Scadenza da PDF
            {"nome_corso": "PATENTE", "validita_mesi": 0, "categoria_corso": "PATENTE"}, # Scadenza da PDF
            {"nome_corso": "CARTA DI IDENTITA", "validita_mesi": 0, "categoria_corso": "CARTA DI IDENTITA"}, # Scadenza da PDF
            {"nome_corso": "MODULO RECESSO RAPPORTO DI LAVORO", "validita_mesi": 0, "categoria_corso": "MODULO RECESSO RAPPORTO DI LAVORO"}, # Senza scadenza
            {"nome_corso": "NOMINA", "validita_mesi": 0, "categoria_corso": "NOMINA"},
            {"nome_corso": "VISITA MEDICA", "validita_mesi": 0, "categoria_corso": "VISITA MEDICA"},
            {"nome_corso": "ALTRO", "validita_mesi": 0, "categoria_corso": "ALTRO"},
        ]

        for corso_data in corsi:
            db_corso = db.query(Corso).filter(Corso.nome_corso == corso_data["nome_corso"]).first()
            if not db_corso:
                new_corso = Corso(**corso_data)
                db.add(new_corso)

        # --- Seed Default Admin User ---
        admin_username = settings.FIRST_RUN_ADMIN_USERNAME
        admin_user = db.query(User).filter(User.username == admin_username).first()

        admin_password_hash = get_password_hash(settings.FIRST_RUN_ADMIN_PASSWORD)

        if not admin_user:
            admin_user = User(
                username=admin_username,
                hashed_password=admin_password_hash,
                account_name="Amministratore",
                is_admin=True
            )
            db.add(admin_user)
        else:
            # Ensure password is up to date with config
            # This fixes issues where the password was changed in config but DB has old hash
            admin_user.hashed_password = admin_password_hash
            admin_user.is_admin = True # Ensure admin privileges
            db.add(admin_user)

        db.commit()
    finally:
        if close_db:
            db.close()
