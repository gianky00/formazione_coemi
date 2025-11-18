from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime

class DipendenteSchema(BaseModel):
    id: int
    matricola: Optional[str] = None
    nome: str
    cognome: str
    data_nascita: Optional[date] = None

    class Config:
        from_attributes = True

class CertificatoSchema(BaseModel):
    id: int
    nome: str
    matricola: Optional[str] = None
    corso: str
    categoria: str
    data_rilascio: str
    data_scadenza: Optional[str] = None
    stato_certificato: str

class CertificatoCreazioneSchema(BaseModel):
    nome: str = Field(..., min_length=1, description="Nome e cognome del dipendente")
    corso: str = Field(..., min_length=1, description="Nome del corso")
    categoria: str = Field(..., min_length=1, description="Categoria del corso")
    data_rilascio: str
    data_scadenza: Optional[str] = None

    @field_validator('nome')
    def validate_nome(cls, v):
        if not v:
            raise ValueError("String should have at least 1 character")
        return v

    @field_validator('data_rilascio')
    def validate_data_rilascio(cls, v):
        if not v:
            raise ValueError("La data di rilascio non può essere vuota.")
        try:
            datetime.strptime(v, '%d/%m/%Y')
        except ValueError:
            raise ValueError("Formato data non valido. Usare DD/MM/YYYY.")
        return v

    @field_validator('data_scadenza')
    def validate_data_scadenza(cls, v):
        if v is None or not v.strip() or v.strip().lower() == 'none':
            return None
        try:
            datetime.strptime(v, '%d/%m/%Y')
        except ValueError:
            raise ValueError("Formato data non valido. Usare DD/MM/YYYY.")
        return v

class CertificatoAggiornamentoSchema(BaseModel):
    nome: Optional[str] = None
    corso: Optional[str] = None
    categoria: Optional[str] = None
    data_rilascio: Optional[str] = None
    data_scadenza: Optional[str] = None

    @field_validator('data_rilascio')
    def validate_data_rilascio(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, '%d/%m/%Y')
        except ValueError:
            raise ValueError("Formato data non valido. Usare DD/MM/YYYY.")
        return v

    @field_validator('data_scadenza')
    def validate_data_scadenza(cls, v):
        if v is None or not v.strip() or v.strip().lower() == 'none':
            return None
        try:
            datetime.strptime(v, '%d/%m/%Y')
        except ValueError:
            raise ValueError("Formato data non valido. Usare DD/MM/YYYY.")
        return v
