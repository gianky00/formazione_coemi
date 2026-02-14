import enum
from datetime import UTC, date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models using SQLAlchemy 2.0 style."""

    pass


def utc_now() -> datetime:
    """Returns the current UTC time."""
    return datetime.now(UTC)


class ValidationStatus(enum.StrEnum):
    """
    An enumeration for the validation status of a certificate.
    - AUTOMATIC: The certificate was created automatically from a PDF.
    - MANUAL: The certificate has been manually validated by a user.
    """

    AUTOMATIC = "AUTOMATIC"
    MANUAL = "MANUAL"


class User(Base):
    """
    Represents a user of the application.
    Stores authentication details and metadata.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    account_name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    previous_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    gender: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class BlacklistedToken(Base):
    """
    Stores tokens that have been invalidated (e.g. via logout).
    """

    __tablename__ = "blacklisted_tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    blacklisted_on: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class AuditLog(Base):
    """
    Records security-critical actions for compliance and auditing.
    """

    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    username: Mapped[str | None] = mapped_column(String, index=True)
    action: Mapped[str] = mapped_column(String, index=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    details: Mapped[str | None] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=utc_now, index=True)
    ip_address: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    user_agent: Mapped[str | None] = mapped_column(String, nullable=True)
    geolocation: Mapped[str | None] = mapped_column(String, nullable=True)
    severity: Mapped[str] = mapped_column(String, default="LOW")
    device_id: Mapped[str | None] = mapped_column(String, nullable=True)
    changes: Mapped[str | None] = mapped_column(String, nullable=True)


class Dipendente(Base):
    """
    Represents an employee in the database.
    """

    __tablename__ = "dipendenti"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    matricola: Mapped[str | None] = mapped_column(String, unique=True, index=True)
    nome: Mapped[str] = mapped_column(String, index=True)
    cognome: Mapped[str] = mapped_column(String, index=True)
    data_nascita: Mapped[date | None] = mapped_column(Date, nullable=True)
    email: Mapped[str | None] = mapped_column(String, unique=True, index=True)
    mansione: Mapped[str | None] = mapped_column(String, nullable=True)
    categoria_reparto: Mapped[str | None] = mapped_column(String, nullable=True)
    data_assunzione: Mapped[date | None] = mapped_column(Date, nullable=True)
    certificati: Mapped[list["Certificato"]] = relationship(
        "Certificato", back_populates="dipendente"
    )


class Corso(Base):
    """
    Represents a training course in the database.
    """

    __tablename__ = "corsi"
    __table_args__ = (UniqueConstraint("nome_corso", "categoria_corso", name="_nome_categoria_uc"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome_corso: Mapped[str] = mapped_column(String, index=True)
    validita_mesi: Mapped[int] = mapped_column(Integer)
    categoria_corso: Mapped[str] = mapped_column(String, index=True)
    certificati: Mapped[list["Certificato"]] = relationship("Certificato", back_populates="corso")


class Certificato(Base):
    """
    Represents a training certificate, linking an employee to a course.
    """

    __tablename__ = "certificati"
    __table_args__ = (
        UniqueConstraint("dipendente_id", "corso_id", "data_rilascio", name="_cert_unique_uc"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dipendente_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("dipendenti.id"), nullable=True
    )
    nome_dipendente_raw: Mapped[str | None] = mapped_column(String, nullable=True)
    data_nascita_raw: Mapped[str | None] = mapped_column(String, nullable=True)
    corso_id: Mapped[int] = mapped_column(Integer, ForeignKey("corsi.id"))
    data_rilascio: Mapped[date] = mapped_column(Date)
    data_scadenza_manuale: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_scadenza_calcolata: Mapped[date | None] = mapped_column(Date, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String, nullable=True)
    stato_validazione: Mapped[ValidationStatus] = mapped_column(
        Enum(ValidationStatus), default=ValidationStatus.AUTOMATIC
    )

    dipendente: Mapped["Dipendente"] = relationship("Dipendente", back_populates="certificati")
    corso: Mapped["Corso"] = relationship("Corso", back_populates="certificati")
