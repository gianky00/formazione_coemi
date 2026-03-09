from datetime import datetime
from pydantic import BaseModel, Field, field_validator

DATE_FORMAT_DMY: str = "%d/%m/%Y"
DATE_ERROR_MSG: str = "Formato data non valido. Usare DD/MM/YYYY."

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

class CertificatoCreazioneSchema(BaseModel):
    nome: str = Field(..., min_length=1)
    data_nascita: str | None = None
    corso: str = Field(..., min_length=1)
    categoria: str = Field(..., min_length=1)
    data_rilascio: str
    data_scadenza: str | None = None
    dipendente_id: int | None = None

    @field_validator("nome")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        if v and len(v.strip().split()) < 2: raise ValueError("Formato nome non valido")
        return v

    @field_validator("data_rilascio")
    @classmethod
    def validate_data_rilascio(cls, v: str) -> str:
        try: datetime.strptime(v, DATE_FORMAT_DMY)
        except ValueError: raise ValueError(DATE_ERROR_MSG)
        return v

    @field_validator("data_scadenza")
    @classmethod
    def validate_data_scadenza(cls, v: str | None) -> str | None:
        if v is None or not v.strip() or v.strip().lower() == "none": return None
        try: datetime.strptime(v, DATE_FORMAT_DMY)
        except ValueError: raise ValueError(DATE_ERROR_MSG)
        return v

class CertificatoAggiornamentoSchema(BaseModel):
    nome: str | None = None
    data_nascita: str | None = None
    corso: str | None = None
    categoria: str | None = None
    data_rilascio: str | None = None
    data_scadenza: str | None = None

    @field_validator("nome")
    @classmethod
    def validate_full_name(cls, v: str | None) -> str | None:
        if v is not None and len(v.strip().split()) < 2: raise ValueError("Formato nome non valido")
        return v

    @field_validator("data_rilascio", "data_scadenza")
    @classmethod
    def validate_dates(cls, v: str | None) -> str | None:
        if v is None or not v.strip() or v.strip().lower() == "none": return None
        try: datetime.strptime(v, DATE_FORMAT_DMY)
        except ValueError: raise ValueError(DATE_ERROR_MSG)
        return v
