import pytest
from app.schemas.schemas import DipendenteCreateSchema
from pydantic import ValidationError

def test_name_validation():
    # Valid
    DipendenteCreateSchema(nome="Mario", cognome="O'Neal")
    DipendenteCreateSchema(nome="Mario Luigi", cognome="Rossi")

    # Invalid
    with pytest.raises(ValidationError):
        DipendenteCreateSchema(nome="Mario123", cognome="Rossi")
    with pytest.raises(ValidationError):
        DipendenteCreateSchema(nome="Mario!", cognome="Rossi")
    with pytest.raises(ValidationError):
        DipendenteCreateSchema(nome="Mario/Rossi", cognome="Rossi")
