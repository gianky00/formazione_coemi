from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class ValidationStatus(str, enum.Enum):
    AUTOMATIC = "AUTOMATIC"
    MANUAL = "MANUAL"

class Dipendente(Base):
    """Rappresenta un dipendente nel database."""
    __tablename__ = 'dipendenti'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    cognome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    categoria_reparto = Column(String)
    certificati = relationship("Certificato", back_populates="dipendente")

class Corso(Base):
    """Rappresenta un corso di formazione nel database."""
    __tablename__ = 'corsi'
    id = Column(Integer, primary_key=True, index=True)
    nome_corso = Column(String, unique=True, index=True)
    validita_mesi = Column(Integer)
    categoria_corso = Column(String)
    certificati = relationship("Certificato", back_populates="corso")

class Certificato(Base):
    """Rappresenta un certificato di formazione che collega un dipendente a un corso."""
    __tablename__ = 'certificati'
    id = Column(Integer, primary_key=True, index=True)
    dipendente_id = Column(Integer, ForeignKey('dipendenti.id'))
    corso_id = Column(Integer, ForeignKey('corsi.id'))
    data_rilascio = Column(Date)
    data_scadenza_calcolata = Column(Date)
    file_path = Column(String)
    stato_validazione = Column(Enum(ValidationStatus))
    dipendente = relationship("Dipendente", back_populates="certificati")
    corso = relationship("Corso", back_populates="certificati")
