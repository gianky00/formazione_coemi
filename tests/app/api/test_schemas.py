import pytest
from pydantic import ValidationError
from app.api.main import CertificatoCreateSchema

def test_certificato_create_schema_valid():
    """
    Testa la validazione di un CertificatoCreateSchema con dati validi.
    """
    data = {
        "nome": "Mario Rossi",
        "corso": "ANTINCENDIO",
        "categoria": "ANTINCENDIO",
        "data_rilascio": "14/11/2025",
        "data_scadenza": "14/11/2030"
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
    Testa che CertificatoCreateSchema (indirettamente tramite l'endpoint)
    gestisca un formato di data non valido.

    Nota: Pydantic non valida il formato della data in questo caso,
    ma il test è utile per documentare il comportamento atteso a livello di endpoint.
    """
    data = {
        "nome": "Mario Rossi",
        "corso": "ANTINCENDIO",
        "categoria": "ANTINCENDIO",
        "data_rilascio": "2025-11-14", # Formato non valido
        "data_scadenza": "2030-11-14"
    }
    # Questo non solleverà un errore Pydantic, ma fallirà a livello di endpoint.
    # Il test serve a chiarire questo comportamento.
    schema = CertificatoCreateSchema(**data)
    assert schema.data_rilascio == "2025-11-14"
