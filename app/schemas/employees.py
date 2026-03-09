import re
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .certificates import CertificatoSchema


class DipendenteSchema(BaseModel):
    id: int
    matricola: str | None = None
    nome: str
    cognome: str
    data_nascita: date | None = None
    email: str | None = None
    mansione: str | None = None
    categoria_reparto: str | None = None
    data_assunzione: date | None = None

    model_config = ConfigDict(from_attributes=True)


class DipendenteDetailSchema(DipendenteSchema):
    certificati: list[CertificatoSchema] = []


class DipendenteCreateSchema(BaseModel):
    matricola: str | None = Field(None, min_length=1)
    nome: str = Field(..., min_length=1)
    cognome: str = Field(..., min_length=1)
    data_nascita: date | None = None
    email: str | None = None
    mansione: str | None = None
    categoria_reparto: str | None = None
    data_assunzione: date | None = None

    @field_validator("nome", "cognome")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if v and not re.match(r"^[a-zA-Z\s']+$", v):
            raise ValueError("Nome e cognome possono contenere solo lettere, spazi e apostrofi.")
        return v


class DipendenteUpdateSchema(BaseModel):
    matricola: str | None = Field(None, min_length=1)
    nome: str | None = Field(None, min_length=1)
    cognome: str | None = Field(None, min_length=1)
    data_nascita: date | None = None
    email: str | None = None
    mansione: str | None = None
    categoria_reparto: str | None = None
    data_assunzione: date | None = None

    @field_validator("nome", "cognome")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if v and not re.match(r"^[a-zA-Z\s']+$", v):
            raise ValueError("Nome e cognome possono contenere solo lettere, spazi e apostrofi.")
        return v
