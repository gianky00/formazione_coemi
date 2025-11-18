from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class ValidationStatus(str, enum.Enum):
    """
    An enumeration for the validation status of a certificate.
    - AUTOMATIC: The certificate was created automatically from a PDF.
    - MANUAL: The certificate has been manually validated by a user.
    """
    AUTOMATIC = "AUTOMATIC"
    MANUAL = "MANUAL"

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
    id = Column(Integer, primary_key=True, index=True)
    dipendente_id = Column(Integer, ForeignKey('dipendenti.id'), nullable=True)
    corso_id = Column(Integer, ForeignKey('corsi.id'))
    data_rilascio = Column(Date)
    data_scadenza_calcolata = Column(Date)
    file_path = Column(String)
    stato_validazione = Column(Enum(ValidationStatus))
    dipendente = relationship("Dipendente", back_populates="certificati")
    corso = relationship("Corso", back_populates="certificati")