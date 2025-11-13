from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class ValidationStatus(enum.Enum):
    AUTOMATIC = "Automatico"
    MANUAL = "Manuale"

class Dipendenti(Base):
    __tablename__ = 'dipendenti'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    cognome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    categoria_reparto = Column(String)
    attestati = relationship("Attestati", back_populates="dipendente")

class CorsiMaster(Base):
    __tablename__ = 'corsi_master'
    id = Column(Integer, primary_key=True, index=True)
    nome_corso = Column(String, unique=True, index=True)
    validita_mesi = Column(Integer)
    categoria_corso = Column(String)
    attestati = relationship("Attestati", back_populates="corso")

class Attestati(Base):
    __tablename__ = 'attestati'
    id = Column(Integer, primary_key=True, index=True)
    id_dipendente = Column(Integer, ForeignKey('dipendenti.id'))
    id_corso = Column(Integer, ForeignKey('corsi_master.id'))
    data_rilascio = Column(Date)
    data_scadenza_calcolata = Column(Date)
    percorso_file_pdf_archiviato = Column(String)
    stato_validazione = Column(Enum(ValidationStatus))
    dipendente = relationship("Dipendenti", back_populates="attestati")
    corso = relationship("CorsiMaster", back_populates="attestati")
