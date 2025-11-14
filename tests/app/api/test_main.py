import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models import Dipendente, Corso, Certificato, ValidationStatus
from datetime import date

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

def test_update_certificato(test_client: TestClient, db_session: Session):
    """
    Testa l'aggiornamento di un certificato tramite l'endpoint PUT /certificati/{id}.
    """
    # Crea dati iniziali
    dipendente = Dipendente(nome="Test", cognome="User")
    corso = Corso(nome_corso="Initial Course", validita_mesi=12, categoria_corso="General")
    certificato = Certificato(
        dipendente=dipendente,
        corso=corso,
        data_rilascio=date(2025, 1, 1),
        stato_validazione=ValidationStatus.MANUAL
    )
    db_session.add_all([dipendente, corso, certificato])
    db_session.commit()

    # Dati di aggiornamento
    update_data = {
        "nome": "Test User",
        "corso": "Updated Course",
        "categoria": "General",
        "data_rilascio": "01/02/2025",
        "data_scadenza": "01/02/2026"
    }

    # Esegui la richiesta di aggiornamento
    response = test_client.put(f"/certificati/{certificato.id}", json=update_data)

    # Verifica la risposta
    assert response.status_code == 200
    data = response.json()
    assert data["corso"] == "Updated Course"

    # Verifica che i dati siano stati aggiornati nel database
    db_session.refresh(certificato)
    assert certificato.corso.nome_corso == "Updated Course"
    assert certificato.data_rilascio == date(2025, 2, 1)

def test_update_certificato_get_or_create(test_client: TestClient, db_session: Session):
    """
    Testa la logica "Get or Create" dell'endpoint di aggiornamento.
    """
    # Crea dati iniziali
    dipendente = Dipendente(nome="Old", cognome="Employee")
    corso = Corso(nome_corso="Old Course", validita_mesi=12, categoria_corso="General")
    certificato = Certificato(
        dipendente=dipendente,
        corso=corso,
        data_rilascio=date(2025, 1, 1),
    )
    db_session.add_all([dipendente, corso, certificato])
    db_session.commit()

    # Dati di aggiornamento con nuovo dipendente e nuovo corso
    update_data = {
        "nome": "New Employee",
        "corso": "New Course",
        "categoria": "General",
        "data_rilascio": "01/03/2025",
        "data_scadenza": "01/03/2026"
    }

    response = test_client.put(f"/certificati/{certificato.id}", json=update_data)
    assert response.status_code == 200

    # Verifica che il nuovo dipendente e il nuovo corso siano stati creati
    new_dipendente = db_session.query(Dipendente).filter_by(nome="New", cognome="Employee").first()
    new_corso = db_session.query(Corso).filter_by(nome_corso="New Course").first()
    assert new_dipendente is not None
    assert new_corso is not None
