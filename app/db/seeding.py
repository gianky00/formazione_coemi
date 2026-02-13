import logging
import shutil
from pathlib import Path
from typing import Any

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.db.models import Corso, User

logger = logging.getLogger(__name__)


def _add_column_if_missing(
    db: Session, table: str, column: str, sql_type: str, index: bool = False
) -> None:
    """Helper to add a column via raw SQL if not exists (SQLite only)."""
    inspector = inspect(db.get_bind())
    columns = [c["name"] for c in inspector.get_columns(table)]

    if column not in columns:
        logger.info(f"Migration: Adding column {column} to table {table}...")
        try:
            db.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}"))
            if index:
                db.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table}_{column} ON {table}({column})"))
            db.commit()
        except Exception as e:
            logger.error(f"Migration failed for {table}.{column}: {e}")
            db.rollback()


def migrate_schema(db: Session) -> None:
    """
    Performs basic schema migrations for SQLite (adds missing columns).
    Used for safe upgrades without full Alembic.
    """
    try:
        # User table updates
        _add_column_if_missing(db, "users", "previous_login", "DATETIME")
        _add_column_if_missing(db, "users", "last_login", "DATETIME")
        _add_column_if_missing(db, "users", "gender", "VARCHAR")

        # Audit logs updates
        _add_column_if_missing(db, "audit_logs", "category", "VARCHAR")
        _add_column_if_missing(db, "audit_logs", "ip_address", "VARCHAR")
        _add_column_if_missing(db, "audit_logs", "user_agent", "VARCHAR")
        _add_column_if_missing(db, "audit_logs", "geolocation", "VARCHAR")
        _add_column_if_missing(
            db, "audit_logs", "severity", "VARCHAR DEFAULT 'LOW'", index=True
        )
        _add_column_if_missing(db, "audit_logs", "device_id", "VARCHAR")
        _add_column_if_missing(db, "audit_logs", "changes", "VARCHAR")

        # Dipendenti updates
        _add_column_if_missing(db, "dipendenti", "email", "VARCHAR", index=True)
        _add_column_if_missing(db, "dipendenti", "data_assunzione", "DATE")
        _add_column_if_missing(db, "dipendenti", "mansione", "VARCHAR")
        _add_column_if_missing(db, "dipendenti", "categoria_reparto", "VARCHAR")

    except Exception as e:
        logger.warning(f"Schema migration warning: {e}")


def seed_courses(db: Session) -> None:
    """Pre-populates the Corso table with default courses if empty."""
    if db.query(Corso).count() > 0:
        return

    logger.info("Seeding default courses...")
    default_courses = [
        {"nome": "Sicurezza Generale", "categoria": "FORMAZIONE", "validita": 0},
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
    ]

    for c in default_courses:
        db.add(
            Corso(
                nome_corso=str(c["nome"]),
                categoria_corso=str(c["categoria"]),
                validita_mesi=int(c["validita"]),
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
    try:
        old_path = Path(cert.file_path)
        if old_path.exists():
            shutil.move(str(old_path), str(trash_dir / old_path.name))
    except Exception:
        pass


def seed_database(db: Session | None = None) -> None:
    """
    Main entry point for database seeding and migration.
    """
    from app.db.session import SessionLocal

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
