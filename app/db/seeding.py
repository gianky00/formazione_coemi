from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.models import Corso, User, Certificato
from app.db.session import SessionLocal
from app.core.security import get_password_hash
from app.core.config import settings, get_user_data_dir
from app.services.document_locator import find_document
from app.services.sync_service import remove_empty_folders
import os
import shutil
from datetime import datetime

def _add_column_if_missing(db, table, column, sql_type, index=False):
    """Helper to add a column if it doesn't exist."""
    result = db.execute(text(f"PRAGMA table_info({table})"))
    columns = [row[1] for row in result.fetchall()]

    if columns and column not in columns:
        print(f"Migrating schema: Adding {column} to {table} table...")
        try:
            db.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}"))
            if index:
                db.execute(text(f"CREATE UNIQUE INDEX ix_{table}_{column} ON {table} ({column})"))
            db.commit()
        except Exception as e:
            print(f"Error adding {column} column: {e}")
            db.rollback()
            raise # Critical

def migrate_schema(db: Session):
    """
    Checks for missing columns in existing tables (due to lack of migrations)
    and adds them using raw SQL. Specifically handles 'previous_login'.
    """
    # S3776: Refactored to reduce complexity
    try:
        # Users table
        _add_column_if_missing(db, "users", "previous_login", "DATETIME")
        _add_column_if_missing(db, "users", "last_login", "DATETIME")
        _add_column_if_missing(db, "users", "gender", "VARCHAR")

        # Audit logs table
        _add_column_if_missing(db, "audit_logs", "category", "VARCHAR")

        # Security columns (Batch check logic kept for simplicity in helper usage)
        # Actually splitting them is cleaner
        _add_column_if_missing(db, "audit_logs", "ip_address", "VARCHAR")
        _add_column_if_missing(db, "audit_logs", "user_agent", "VARCHAR")
        _add_column_if_missing(db, "audit_logs", "geolocation", "VARCHAR")
        _add_column_if_missing(db, "audit_logs", "severity", "VARCHAR DEFAULT 'LOW'")

        # Ensure default severity
        db.execute(text("UPDATE audit_logs SET severity = 'LOW' WHERE severity IS NULL"))
        db.commit()

        _add_column_if_missing(db, "audit_logs", "device_id", "VARCHAR")
        _add_column_if_missing(db, "audit_logs", "changes", "VARCHAR")

        # Dipendenti table
        _add_column_if_missing(db, "dipendenti", "email", "VARCHAR", index=True)
        _add_column_if_missing(db, "dipendenti", "data_assunzione", "DATE")
        _add_column_if_missing(db, "dipendenti", "mansione", "VARCHAR")

        # Ensure indexes exist
        try:
            db.execute(text("CREATE INDEX IF NOT EXISTS ix_audit_logs_timestamp ON audit_logs (timestamp)"))
            db.execute(text("CREATE INDEX IF NOT EXISTS ix_audit_logs_ip_address ON audit_logs (ip_address)"))
            db.commit()
        except Exception as e:
            print(f"Error creating indexes: {e}")
            db.rollback()

        # Backfill
        db.execute(text("UPDATE audit_logs SET category = 'GENERAL' WHERE category IS NULL"))
        db.execute(text("UPDATE audit_logs SET category = 'CERTIFICATE' WHERE category = 'GENERAL' AND action LIKE 'CERTIFICATE_%'"))
        db.execute(text("UPDATE audit_logs SET category = 'AUTH' WHERE category = 'GENERAL' AND (action = 'LOGIN' OR action = 'LOGOUT')"))
        db.execute(text("UPDATE audit_logs SET category = 'USER_MGMT' WHERE category = 'GENERAL' AND (action LIKE 'USER_%' OR action = 'PASSWORD_CHANGE')"))
        db.execute(text("UPDATE audit_logs SET category = 'DATA' WHERE category = 'GENERAL' AND action = 'DIPENDENTI_IMPORT'"))
        db.execute(text("UPDATE audit_logs SET category = 'SYSTEM' WHERE category = 'GENERAL' AND action = 'SYSTEM_ALERT'"))
        db.execute(text("UPDATE audit_logs SET category = 'CONFIG' WHERE category = 'GENERAL' AND action = 'CONFIG_UPDATE'"))
        db.commit()

    except Exception as e:
        print(f"Schema migration check failed: {e}")
        db.rollback()
        raise # Critical failure

def cleanup_deprecated_data(db: Session):
    """
    Removes data related to deprecated categories like 'MEDICO COMPETENTE'.
    """
    # S3776: Refactored to reduce complexity
    deprecated_category = "MEDICO COMPETENTE"

    try:
        courses = db.query(Corso).filter(Corso.categoria_corso == deprecated_category).all()
        course_ids = [c.id for c in courses]

        if not course_ids:
            return

        certs_to_delete = db.query(Certificato).filter(Certificato.corso_id.in_(course_ids)).all()
        database_path = settings.DATABASE_PATH or str(get_user_data_dir())
        trash_dir = os.path.join(database_path, "DOCUMENTI DIPENDENTI", "CESTINO") if database_path else None

        if trash_dir:
            os.makedirs(trash_dir, exist_ok=True)

        for cert in certs_to_delete:
            _move_deprecated_file(cert, database_path, trash_dir)
            db.delete(cert)

        if certs_to_delete:
            print(f"Cleanup: Deleted {len(certs_to_delete)} certificates for deprecated category '{deprecated_category}'.")

        deleted_courses = db.query(Corso).filter(Corso.id.in_(course_ids)).delete(synchronize_session=False)
        if deleted_courses > 0:
             print(f"Cleanup: Deleted {deleted_courses} deprecated courses.")

        db.commit()
    except Exception as e:
        print(f"Error during cleanup of deprecated data: {e}")
        db.rollback()

def _move_deprecated_file(cert, database_path, trash_dir):
    try:
        cert_data = {
            'nome': f"{cert.dipendente.cognome} {cert.dipendente.nome}" if cert.dipendente else cert.nome_dipendente_raw,
            'matricola': cert.dipendente.matricola if cert.dipendente else None,
            'categoria': "MEDICO COMPETENTE",
            'data_scadenza': cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else None
        }

        if database_path:
            file_path = find_document(database_path, cert_data)
            if file_path and os.path.exists(file_path):
                filename = os.path.basename(file_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest = os.path.join(trash_dir, f"{os.path.splitext(filename)[0]}_deprecated_{timestamp}.pdf")
                shutil.move(file_path, dest)
                remove_empty_folders(os.path.dirname(file_path))
    except Exception as e:
        print(f"Error moving deprecated file: {e}")

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
        migrate_schema(db)
        cleanup_deprecated_data(db)

        corsi = [
            {"nome_corso": "ANTINCENDIO", "validita_mesi": 60, "categoria_corso": "ANTINCENDIO"},
            {"nome_corso": "PRIMO SOCCORSO", "validita_mesi": 36, "categoria_corso": "PRIMO SOCCORSO"},
            {"nome_corso": "ASPP", "validita_mesi": 60, "categoria_corso": "ASPP"},
            {"nome_corso": "RSPP", "validita_mesi": 60, "categoria_corso": "RSPP"},
            {"nome_corso": "ATEX", "validita_mesi": 60, "categoria_corso": "ATEX"},
            {"nome_corso": "BLSD", "validita_mesi": 12, "categoria_corso": "BLSD"},
            {"nome_corso": "CARROPONTE", "validita_mesi": 60, "categoria_corso": "CARROPONTE"},
            {"nome_corso": "DIRETTIVA SEVESO", "validita_mesi": 60, "categoria_corso": "DIRETTiva SEVESO"},
            {"nome_corso": "DIRIGENTI E FORMATORI", "validita_mesi": 60, "categoria_corso": "DIRIGENTI E FORMATORI"},
            {"nome_corso": "GRU A TORRE E PONTE", "validita_mesi": 60, "categoria_corso": "GRU A TORRE E PONTE"},
            {"nome_corso": "H2S", "validita_mesi": 60, "categoria_corso": "H2S"},
            {"nome_corso": "IMBRACATORE", "validita_mesi": 60, "categoria_corso": "IMBRACATORE"},
            {"nome_corso": "FORMAZIONE GENERICA ART.37", "validita_mesi": 60, "categoria_corso": "FORMAZIONE GENERICA ART.37"},
            {"nome_corso": "PREPOSTO", "validita_mesi": 24, "categoria_corso": "PREPOSTO"},
            {"nome_corso": "GRU SU AUTOCARRO", "validita_mesi": 60, "categoria_corso": "GRU SU AUTOCARRO"},
            {"nome_corso": "PLE", "validita_mesi": 60, "categoria_corso": "PLE"},
            {"nome_corso": "L5 PES PAV PEI C CANTIERE", "validita_mesi": 60, "categoria_corso": "L5 PES PAV PEI C CANTIERE"},
            {"nome_corso": "LAVORI IN QUOTA", "validita_mesi": 60, "categoria_corso": "LAVORI IN QUOTA"},
            {"nome_corso": "MACCHINE OPERATRICI", "validita_mesi": 60, "categoria_corso": "MACCHINE OPERATRICI"},
            {"nome_corso": "MANITOU P.ROTATIVE", "validita_mesi": 60, "categoria_corso": "MANITOU P.ROTATIVE"},
            {"nome_corso": "MULETTO CARRELISTI", "validita_mesi": 60, "categoria_corso": "MULETTO CARRELISTI"},
            {"nome_corso": "SOPRAVVIVENZA E SALVATAGGIO IN MARE", "validita_mesi": 60, "categoria_corso": "SOPRAVVIVENZA E SALVATAGGIO IN MARE"},
            {"nome_corso": "SPAZI CONFINATI DPI III E AUTORESPIRATORI", "validita_mesi": 60, "categoria_corso": "SPAZI CONFINATI DPI III E AUTORESPIRATORI"},
            {"nome_corso": "HLO", "validita_mesi": 0, "categoria_corso": "HLO"},
            {"nome_corso": "TESSERA HLO", "validita_mesi": 0, "categoria_corso": "TESSERA HLO"},
            {"nome_corso": "UNILAV", "validita_mesi": 0, "categoria_corso": "UNILAV"},
            {"nome_corso": "PATENTE", "validita_mesi": 0, "categoria_corso": "PATENTE"},
            {"nome_corso": "CARTA DI IDENTITA", "validita_mesi": 0, "categoria_corso": "CARTA DI IDENTITA"},
            {"nome_corso": "MODULO RECESSO RAPPORTO DI LAVORO", "validita_mesi": 0, "categoria_corso": "MODULO RECESSO RAPPORTO DI LAVORO"},
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

        if not admin_user:
            admin_password_hash = get_password_hash(settings.FIRST_RUN_ADMIN_PASSWORD)
            admin_user = User(
                username=admin_username,
                hashed_password=admin_password_hash,
                account_name="Amministratore",
                is_admin=True
            )
            db.add(admin_user)
        else:
            # Bug 1 Fix: Ensure password matches settings
            current_admin_password = settings.FIRST_RUN_ADMIN_PASSWORD
            # S1940: Boolean inversion fixed
            # S1192: verify_password handles salt comparison correctly
            from app.core.security import verify_password
            if not verify_password(current_admin_password, admin_user.hashed_password):
                 admin_user.hashed_password = get_password_hash(current_admin_password)
            
            # Ensure admin privileges are kept
            admin_user.is_admin = True
            db.add(admin_user)

        db.commit()
    finally:
        if close_db:
            db.close()
