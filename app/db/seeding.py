import logging
import shutil
from pathlib import Path
from typing import Any

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.db.models import Corso, User
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


def _add_column_if_missing(
    db: Session, table: str, column: str, sql_type: str, index: bool = False
) -> None:
    """Helper to add a column via raw SQL if not exists (SQLite only)."""
    inspector = inspect(db.get_bind())
    try:
        columns_info = inspector.get_columns(table)
        columns = [c["name"] for c in columns_info]
    except Exception:
        # Table probably doesn't exist
        return

    if column not in columns:
        logger.info(f"Migration: Adding column {column} to table {table}...")
        try:
            db.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}"))
            if index:
                db.execute(
                    text(f"CREATE INDEX IF NOT EXISTS idx_{table}_{column} ON {table}({column})")
                )
            db.commit()
        except Exception as e:
            logger.error(f"Migration failed for {table}.{column}: {e}")
            db.rollback()


def migrate_schema(db: Session) -> None:
    """
    Performs basic schema migrations for SQLite (adds missing columns).
    Used for safe upgrades without full Alembic.
    """
    # 1. Add Columns (granular try-except to allow partial migration)
    tables_configs = [
        ("users", "previous_login", "DATETIME", False),
        ("users", "last_login", "DATETIME", False),
        ("users", "gender", "VARCHAR", False),
        ("audit_logs", "category", "VARCHAR", False),
        ("audit_logs", "ip_address", "VARCHAR", False),
        ("audit_logs", "user_agent", "VARCHAR", False),
        ("audit_logs", "geolocation", "VARCHAR", False),
        ("audit_logs", "severity", "VARCHAR DEFAULT 'LOW'", True),
        ("audit_logs", "device_id", "VARCHAR", False),
        ("audit_logs", "changes", "VARCHAR", False),
        ("dipendenti", "email", "VARCHAR", True),
        ("dipendenti", "data_assunzione", "DATE", False),
        ("dipendenti", "mansione", "VARCHAR", False),
        ("dipendenti", "categoria_reparto", "VARCHAR", False),
    ]

    for table, col, col_type, is_idx in tables_configs:
        try:
            _add_column_if_missing(db, table, col, col_type, is_idx)
        except Exception as e:
            logger.debug(f"Migration skip for {table}.{col}: {e}")

    # 2. Smart Backfill for Audit Categories
    try:
        db.execute(
            text(
                "UPDATE audit_logs SET category = 'AUTH' WHERE category IS NULL AND action IN ('LOGIN', 'LOGIN_SUCCESS', 'LOGIN_FAILED', 'LOGOUT')"
            )
        )
        db.execute(
            text(
                "UPDATE audit_logs SET category = 'CERTIFICATE' WHERE category IS NULL AND action LIKE 'CERT%'"
            )
        )
        db.execute(
            text(
                "UPDATE audit_logs SET category = 'EMPLOYEE' WHERE category IS NULL AND action LIKE 'DIPENDENTE%'"
            )
        )
        db.execute(text("UPDATE audit_logs SET category = 'GENERAL' WHERE category IS NULL"))
        db.commit()
    except Exception as e:
        logger.debug(f"Backfill skipped: {e}")


def seed_courses(db: Session) -> None:
    """Pre-populates the Corso table with default courses if empty."""
    if db.query(Corso).count() > 0:
        return

    logger.info("Seeding default courses...")
    default_courses = [
        {"nome": "Sicurezza Generale", "categoria": "FORMAZIONE", "validita": 0},
        {"nome": "ANTINCENDIO", "categoria": "ANTINCENDIO", "validita": 60},
        {"nome": "Rischio Specifico Basso", "categoria": "FORMAZIONE", "validita": 60},
        {"nome": "Rischio Specifico Medio", "categoria": "FORMAZIONE", "validita": 60},
        {"nome": "Rischio Specifico Alto", "categoria": "FORMAZIONE", "validita": 60},
        {"nome": "Antincendio Livello 1", "categoria": "FORMAZIONE", "validita": 60},
        {"nome": "Antincendio Livello 2", "categoria": "FORMAZIONE", "validita": 60},
        {"nome": "Primo Soccorso Gr. B/C", "categoria": "FORMAZIONE", "validita": 36},
        {"nome": "Primo Soccorso Gr. A", "categoria": "FORMAZIONE", "validita": 36},
        {"nome": "Lavori in Quota", "categoria": "ADDESTRAMENTO", "validita": 60},
        {"nome": "DPI 3 Categoria", "categoria": "ADDESTRAMENTO", "validita": 60},
        {"nome": "Carrelli Elevatori", "categoria": "ABILITAZIONE", "validita": 60},
        {"nome": "PLE con e senza stabilizzatori", "categoria": "ABILITAZIONE", "validita": 60},
        {"nome": "Visita Medica Periodica", "categoria": "VISITA MEDICA", "validita": 12},
        {"nome": "NOMINA", "categoria": "NOMINA", "validita": 0},
        # Additional courses to reach >= 30
        {"nome": "Escavatori Idraulici", "categoria": "ABILITAZIONE", "validita": 60},
        {"nome": "Gru per Autocarro", "categoria": "ABILITAZIONE", "validita": 60},
        {"nome": "Spazi Confinati", "categoria": "ADDESTRAMENTO", "validita": 60},
        {"nome": "Preposti", "categoria": "FORMAZIONE", "validita": 60},
        {"nome": "Dirigenti", "categoria": "FORMAZIONE", "validita": 0},
        {"nome": "RLS", "categoria": "FORMAZIONE", "validita": 12},
        {"nome": "HACCP", "categoria": "FORMAZIONE", "validita": 24},
        {"nome": "PES/PAV", "categoria": "ABILITAZIONE", "validita": 60},
        {"nome": "Ponteggi (Pi.M.U.S.)", "categoria": "ADDESTRAMENTO", "validita": 48},
        {"nome": "Carroponte", "categoria": "ADDESTRAMENTO", "validita": 60},
        {"nome": "Guida Sicura", "categoria": "FORMAZIONE", "validita": 60},
        {"nome": "Primo Soccorso (Aggiornamento)", "categoria": "FORMAZIONE", "validita": 36},
        {"nome": "Antincendio (Aggiornamento)", "categoria": "FORMAZIONE", "validita": 60},
        {"nome": "Sicurezza Specifica (Aggiornamento)", "categoria": "FORMAZIONE", "validita": 60},
        {"nome": "Corso Formatori", "categoria": "FORMAZIONE", "validita": 36},
        {"nome": "Legge 231", "categoria": "FORMAZIONE", "validita": 0},
        {"nome": "Privacy GDPR", "categoria": "FORMAZIONE", "validita": 0},
        {"nome": "BLSD", "categoria": "FORMAZIONE", "validita": 12},
    ]

    for c in default_courses:
        db.add(
            Corso(
                nome_corso=str(c["nome"]),
                categoria_corso=str(c["categoria"]),
                validita_mesi=int(str(c["validita"])),
            )
        )
    db.commit()


def cleanup_deprecated_data(db: Session) -> None:
    """
    Removes files or records that are no longer supported in the new architecture.
    """
    from app.core.db_security import db_security

    database_path = db_security.data_dir
    trash_dir = database_path / "Deprecated_Files"

    # Example: Move files from old directory structure
    # This is a safe cleanup, doesn't delete from DB
    try:
        from app.db.models import Certificato

        certs = db.query(Certificato).all()
        for cert in certs:
            if cert.file_path and "old_folder" in cert.file_path:
                trash_dir.mkdir(parents=True, exist_ok=True)
                _move_deprecated_file(cert, database_path, trash_dir)
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")


def _move_deprecated_file(cert: Any, database_path: Path, trash_dir: Path) -> None:
    """Helper to move a single file to trash."""
    import contextlib

    with contextlib.suppress(Exception):
        old_path = Path(cert.file_path)
        if old_path.exists():
            shutil.move(str(old_path), str(trash_dir / old_path.name))


def seed_database(db: Session | None = None) -> None:
    """
    Main entry point for database seeding and migration.
    """
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        # 1. Schema Migration
        migrate_schema(db)

        # 2. Default Admin User
        admin_user = (
            db.query(User).filter(User.username == settings.FIRST_RUN_ADMIN_USERNAME).first()
        )
        if not admin_user:
            logger.info(f"Creating default admin user: {settings.FIRST_RUN_ADMIN_USERNAME}")
            new_admin = User(
                username=settings.FIRST_RUN_ADMIN_USERNAME,
                hashed_password=security.get_password_hash(settings.FIRST_RUN_ADMIN_PASSWORD),
                is_admin=True,
                account_name="Amministratore di Sistema",
            )
            db.add(new_admin)
            db.commit()
        elif not security.verify_password(
            settings.FIRST_RUN_ADMIN_PASSWORD, admin_user.hashed_password
        ):
            logger.info(
                f"Updating password for default admin user: {settings.FIRST_RUN_ADMIN_USERNAME}"
            )
            admin_user.hashed_password = security.get_password_hash(
                settings.FIRST_RUN_ADMIN_PASSWORD
            )
            db.commit()

        # 3. Default Courses
        seed_courses(db)

        # 4. Cleanup
        cleanup_deprecated_data(db)

    except Exception as e:
        logger.error(f"Database seeding failed: {e}")
        db.rollback()
    finally:
        if own_session and db:
            db.close()
