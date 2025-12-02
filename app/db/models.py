from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, UniqueConstraint, DateTime, Boolean
from sqlalchemy.orm import relationship, declarative_base
import enum
from datetime import datetime, timezone

Base = declarative_base()

def utc_now():
    return datetime.now(timezone.utc)

class ValidationStatus(str, enum.Enum):
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
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    account_name = Column(String, nullable=True) # Visible name (e.g. "Mario Rossi")
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    previous_login = Column(DateTime, nullable=True)
    gender = Column(String, nullable=True) # 'M', 'F', or None
    created_at = Column(DateTime, default=utc_now)

class BlacklistedToken(Base):
    """
    Stores tokens that have been invalidated (e.g. via logout).
    """
    __tablename__ = 'blacklisted_tokens'
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    blacklisted_on = Column(DateTime, default=utc_now)

class AuditLog(Base):
    """
    Records security-critical actions for compliance and auditing.
    """
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    username = Column(String, index=True) # Store snapshot of username in case user is deleted
    action = Column(String, index=True, nullable=False) # e.g. "PASSWORD_CHANGE", "USER_CREATE"
    category = Column(String, index=True, nullable=True) # e.g. "LOGIN", "USER", "CERTIFICATE"
    details = Column(String, nullable=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    ip_address = Column(String, nullable=True, index=True)
    user_agent = Column(String, nullable=True)
    geolocation = Column(String, nullable=True)
    severity = Column(String, default="LOW") # LOW, MEDIUM, CRITICAL
    device_id = Column(String, nullable=True)
    changes = Column(String, nullable=True) # JSON string

class Dipendente(Base):
    """
    Represents an employee in the database.
    Each employee has a unique ID, a name, a surname, and an optional email
    and department category. It holds a relationship to all certificates
    issued to them.
    """
    __tablename__ = 'dipendenti'
    id = Column(Integer, primary_key=True, index=True)
    matricola = Column(String, unique=True, index=True)
    nome = Column(String, index=True)
    cognome = Column(String, index=True)
    data_nascita = Column(Date)
    email = Column(String, unique=True, index=True)
    categoria_reparto = Column(String)
    data_assunzione = Column(Date, nullable=True)
    certificati = relationship("Certificato", back_populates="dipendente")

class Corso(Base):
    """
    Represents a training course in the database.
    Each course has a unique name, a validity period in months, and a category.
    A course's uniqueness is defined by the combination of its name and category.
    It holds a relationship to all certificates issued for this course.
    """
    __tablename__ = 'corsi'
    __table_args__ = (UniqueConstraint('nome_corso', 'categoria_corso', name='_nome_categoria_uc'),)

    id = Column(Integer, primary_key=True, index=True)
    nome_corso = Column(String, index=True)
    validita_mesi = Column(Integer)
    categoria_corso = Column(String, index=True)
    certificati = relationship("Certificato", back_populates="corso")

class Certificato(Base):
    """
    Represents a training certificate, linking an employee to a course.
    It stores the issue date, the calculated expiration date, an optional
    file path to the certificate PDF, and its validation status.
    """
    __tablename__ = 'certificati'
    __table_args__ = (
        UniqueConstraint('dipendente_id', 'corso_id', 'data_rilascio', name='_cert_unique_uc'),
    )

    id = Column(Integer, primary_key=True, index=True)
    dipendente_id = Column(Integer, ForeignKey('dipendenti.id'), nullable=True)
    nome_dipendente_raw = Column(String, nullable=True)  # Store the raw name from AI
    data_nascita_raw = Column(String, nullable=True)  # Store the raw birth date from AI
    corso_id = Column(Integer, ForeignKey('corsi.id'))
    data_rilascio = Column(Date)
    data_scadenza_calcolata = Column(Date)
    file_path = Column(String)
    stato_validazione = Column(Enum(ValidationStatus))
    dipendente = relationship("Dipendente", back_populates="certificati")
    corso = relationship("Corso", back_populates="certificati")
