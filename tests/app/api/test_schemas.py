import pytest
from pydantic import ValidationError

from app.schemas.schemas import CertificatoCreazioneSchema as CertificatoCreateSchema


def test_certificato_create_schema_valid():
    """
    Testa la validazione di un CertificatoCreateSchema con dati validi.
    """
    data = {
        "nome": "Mario Rossi",
        "corso": "ANTINCENDIO",
        "categoria": "ANTINCENDIO",
        "data_rilascio": "14/11/2025",
        "data_scadenza": "14/11/2030",
    }
    schema = CertificatoCreateSchema(**data)
    assert schema.nome == "Mario Rossi"
    assert schema.corso == "ANTINCENDIO"


def test_certificato_create_schema_missing_fields():
    """
    Testa che CertificatoCreateSchema sollevi un errore se mancano campi obbligatori.
    """
    with pytest.raises(ValidationError):
        CertificatoCreateSchema(nome="Mario Rossi", corso="ANTINCENDIO")


def test_certificato_create_schema_invalid_date_format():
    """
    Testa che CertificatoCreateSchema sollevi un ValidationError per un formato di data non valido.
    """
    with pytest.raises(ValidationError):
        CertificatoCreateSchema(
            nome="Mario Rossi",
            corso="ANTINCENDIO",
            categoria="ANTINCENDIO",
            data_rilascio="2025-11-14",  # Formato non valido
            data_scadenza="14/11/2030",
        )
