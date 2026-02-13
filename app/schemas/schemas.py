import re
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

DATE_FORMAT_DMY: str = "%d/%m/%Y"
DATE_ERROR_MSG: str = "Formato data non valido. Usare DD/MM/YYYY."


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


class CertificatoSchema(BaseModel):
    id: int
    nome: str
    data_nascita: str | None = None
    matricola: str | None = None
    corso: str
    categoria: str
    data_rilascio: str
    data_scadenza: str | None = None
    stato_certificato: str
    assegnazione_fallita_ragione: str | None = None


class DipendenteDetailSchema(DipendenteSchema):
    certificati: list[CertificatoSchema] = []


class CertificatoCreazioneSchema(BaseModel):
    nome: str = Field(..., min_length=1, description="Nome e cognome del dipendente")
    data_nascita: str | None = None
    corso: str = Field(..., min_length=1, description="Nome del corso")
    categoria: str = Field(..., min_length=1, description="Categoria del corso")
    data_rilascio: str
    data_scadenza: str | None = None
    dipendente_id: int | None = None

    @field_validator("data_rilascio")
    @classmethod
    def validate_data_rilascio(cls, v: str) -> str:
        if not v:
            raise ValueError("La data di rilascio non può essere vuota.")
        try:
            datetime.strptime(v, DATE_FORMAT_DMY)
        except ValueError:
            raise ValueError(DATE_ERROR_MSG)
        return v

    @field_validator("data_scadenza")
    @classmethod
    def validate_data_scadenza(cls, v: str | None) -> str | None:
        if v is None or not v.strip() or v.strip().lower() == "none":
            return None
        try:
            datetime.strptime(v, DATE_FORMAT_DMY)
        except ValueError:
            raise ValueError(DATE_ERROR_MSG)
        return v


class CertificatoAggiornamentoSchema(BaseModel):
    nome: str | None = None
    data_nascita: str | None = None
    corso: str | None = None
    categoria: str | None = None
    data_rilascio: str | None = None
    data_scadenza: str | None = None

    @field_validator("data_rilascio")
    @classmethod
    def validate_data_rilascio(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            datetime.strptime(v, DATE_FORMAT_DMY)
        except ValueError:
            raise ValueError(DATE_ERROR_MSG)
        return v

    @field_validator("data_scadenza")
    @classmethod
    def validate_data_scadenza(cls, v: str | None) -> str | None:
        if v is None or not v.strip() or v.strip().lower() == "none":
            return None
        try:
            datetime.strptime(v, DATE_FORMAT_DMY)
        except ValueError:
            raise ValueError(DATE_ERROR_MSG)
        return v


# --- User Schemas ---


class UserBase(BaseModel):
    username: str
    account_name: str | None = None
    gender: str | None = None  # 'M', 'F', or None
    is_admin: bool = False


class UserCreateSchema(UserBase):
    password: str | None = None


class UserPasswordUpdateSchema(BaseModel):
    old_password: str
    new_password: str


class UserUpdateSchema(BaseModel):
    username: str | None = None
    account_name: str | None = None
    password: str | None = None
    gender: str | None = None
    is_admin: bool | None = None


class UserSchema(UserBase):
    id: int
    last_login: datetime | None = None
    previous_login: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    account_name: str | None = None
    gender: str | None = None
    is_admin: bool
    previous_login: datetime | None = None
    read_only: bool = False
    lock_owner: dict[str, Any] | None = None
    require_password_change: bool = False


class TokenData(BaseModel):
    username: str | None = None


class AuditLogSchema(BaseModel):
    id: int
    user_id: int | None = None
    username: str
    action: str
    category: str | None = None
    details: str | None = None
    timestamp: datetime
    ip_address: str | None = None
    user_agent: str | None = None
    geolocation: str | None = None
    severity: str | None = "LOW"
    device_id: str | None = None
    changes: str | None = None  # JSON string

    model_config = ConfigDict(from_attributes=True)
