import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models import Dipendente, Corso, Certificato, ValidationStatus

def test_create_certificato(test_client: TestClient, db_session: Session):
    """
    Testa la creazione di un certificato tramite l'endpoint POST /certificati/.
    """
    # Aggiungi un corso di esempio al database di test
    corso_antincendio = Corso(
        nome_corso="ANTINCENDIO",
        validita_mesi=60,
        categoria_corso="ANTINCENDIO"
    )
    db_session.add(corso_antincendio)
    db_session.commit()

    # Dati di esempio
    certificato_data = {
        "nome": "Mario Rossi",
        "corso": "ANTINCENDIO",
        "categoria": "ANTINCENDIO",
        "data_rilascio": "14/11/2025",
        "data_scadenza": "14/11/2030"
    }

    # Esegui la richiesta
    response = test_client.post("/certificati/", json=certificato_data)

    # Verifica la risposta
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Mario Rossi"
    assert data["corso"] == "ANTINCENDIO"
    assert data["stato_certificato"] == "attivo"

    # Verifica che il certificato sia stato creato nel database
    certificato_db = db_session.query(Certificato).filter(Certificato.id == data["id"]).first()
    assert certificato_db is not None
    assert certificato_db.stato_validazione == ValidationStatus.AUTOMATIC
    assert certificato_db.dipendente.cognome == "Rossi"
    assert certificato_db.corso.nome_corso == "ANTINCENDIO"

def test_validate_certificato(test_client: TestClient, db_session: Session):
    """
    Testa la validazione di un certificato tramite l'endpoint PUT /certificati/{id}/valida.
    """
    # Crea un certificato di esempio
    from datetime import date
    certificato = Certificato(
        dipendente=Dipendente(nome="Jane", cognome="Doe"),
        corso=Corso(nome_corso="PRIMO SOCCORSO", validita_mesi=36, categoria_corso="PRIMO SOCCORSO"),
        data_rilascio=date(2025, 11, 14),
        stato_validazione=ValidationStatus.AUTOMATIC
    )
    db_session.add(certificato)
    db_session.commit()

    # Esegui la richiesta di validazione
    response = test_client.put(f"/certificati/{certificato.id}/valida")

    # Verifica la risposta
    assert response.status_code == 200
    assert response.json()["message"] == "Certificato validato con successo"

    # Verifica che lo stato del certificato sia stato aggiornato nel database
    db_session.refresh(certificato)
    assert certificato.stato_validazione == ValidationStatus.MANUAL
