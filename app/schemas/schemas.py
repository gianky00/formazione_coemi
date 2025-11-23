from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import date, datetime

class DipendenteSchema(BaseModel):
    id: int
    matricola: Optional[str] = None
    nome: str
    cognome: str
    data_nascita: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)

class CertificatoSchema(BaseModel):
    id: int
    nome: str
    data_nascita: Optional[str] = None
    matricola: Optional[str] = None
    corso: str
    categoria: str
    data_rilascio: str
    data_scadenza: Optional[str] = None
    stato_certificato: str
    assegnazione_fallita_ragione: Optional[str] = None

class CertificatoCreazioneSchema(BaseModel):
    nome: str = Field(..., min_length=1, description="Nome e cognome del dipendente")
    data_nascita: Optional[str] = None
    corso: str = Field(..., min_length=1, description="Nome del corso")
    categoria: str = Field(..., min_length=1, description="Categoria del corso")
    data_rilascio: str
    data_scadenza: Optional[str] = None

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

# --- User Schemas ---

class UserBase(BaseModel):
    username: str
    account_name: Optional[str] = None
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    account_name: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None

class User(UserBase):
    id: int
    last_login: Optional[datetime] = None
    previous_login: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    account_name: Optional[str] = None
    is_admin: bool
    previous_login: Optional[datetime] = None

class TokenData(BaseModel):
    username: Optional[str] = None

class AuditLogSchema(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: str
    action: str
    category: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    geolocation: Optional[str] = None
    severity: Optional[str] = "LOW"

    model_config = ConfigDict(from_attributes=True)
