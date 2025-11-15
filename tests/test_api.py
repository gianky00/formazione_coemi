import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models import Dipendente, Corso, Certificato, ValidationStatus
from datetime import date

def test_create_certificato(test_client: TestClient, db_session: Session, mock_ai_service):
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

    # Verifica che lo stato del certificato sia stato aggiornato nel database
    db_session.refresh(certificato)
    assert certificato.stato_validazione == ValidationStatus.MANUAL

def test_update_certificato(test_client: TestClient, db_session: Session):
    """
    Testa l'aggiornamento di un certificato, verificando che i dati vengano
    correttamente modificati nel database.
    """
    # Arrange: Crea i dati iniziali nel database
    initial_dipendente = Dipendente(nome="Test", cognome="User")
    initial_corso = Corso(nome_corso="Initial Course", validita_mesi=12, categoria_corso="General")
    certificato = Certificato(
        dipendente=initial_dipendente,
        corso=initial_corso,
        data_rilascio=date(2025, 1, 1),
        stato_validazione=ValidationStatus.MANUAL
    )
    db_session.add_all([initial_dipendente, initial_corso, certificato])
    db_session.commit()

    update_payload = {
        "nome": "Test User",
        "corso": "Updated Course",
        "categoria": "General",
        "data_rilascio": "01/02/2025",
        "data_scadenza": "01/02/2026"
    }

    # Act: Esegui la richiesta di aggiornamento
    response = test_client.put(f"/certificati/{certificato.id}", json=update_payload)

    # Assert: Verifica la risposta dell'API e lo stato del database
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["corso"] == "Updated Course"
    assert response_data["data_rilascio"] == "01/02/2025"

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

@pytest.mark.parametrize("payload_override, expected_status_code, error_detail_part", [
    ({"data_rilascio": ""}, 422, "La data non può essere vuota"),
    ({"data_rilascio": "14-11-2025"}, 422, "Formato data non valido"),
    ({"data_rilascio": "2025/11/14"}, 422, "Formato data non valido"),
    ({"nome": ""}, 422, "at least 1 character"),
    ({"corso": ""}, 422, "at least 1 character"),
    ({"categoria": ""}, 422, "at least 1 character"),
    ({"nome": "Mario"}, 400, "Formato nome non valido"),
])
def test_create_certificato_invalid_payload_fails(test_client: TestClient, db_session: Session, payload_override, expected_status_code, error_detail_part):
    """
    Testa che la creazione di un certificato fallisca con dati di input non validi,
    coprendo vari scenari tramite parametrizzazione.
    """
    # Setup del corso master nel DB per evitare errori 404
    corso_antincendio = Corso(nome_corso="ANTINCENDIO", validita_mesi=60, categoria_corso="ANTINCENDIO")
    db_session.add(corso_antincendio)
    db_session.commit()

    # Payload di base valido
    valid_payload = {
        "nome": "Mario Rossi",
        "corso": "Corso Antincendio Base",
        "categoria": "ANTINCENDIO",
        "data_rilascio": "14/11/2025",
        "data_scadenza": "14/11/2030"
    }

    # Applica l'override per il caso di test corrente
    invalid_payload = valid_payload.copy()
    invalid_payload.update(payload_override)

    # Esegui la richiesta
    response = test_client.post("/certificati/", json=invalid_payload)

    # Verifica lo status code e il messaggio di errore
    assert response.status_code == expected_status_code
    response_data = response.json()
    if isinstance(response_data.get('detail'), list):
        assert any(error_detail_part in error['msg'] for error in response_data['detail'])
    else:
        assert error_detail_part in response_data.get('detail', '')

@pytest.mark.parametrize("input_scadenza, expected_db_value, expected_response_value", [
    ("15/12/2030", date(2030, 12, 15), "15/12/2030"),
    (None, None, None),
    ("", None, None),
    ("None", None, None),
    ("none", None, None),
])
def test_update_certificato_data_scadenza_variations(test_client: TestClient, db_session: Session, input_scadenza, expected_db_value, expected_response_value):
    """
    Testa l'aggiornamento della data di scadenza con vari input (validi, null, stringhe vuote).
    """
    # Arrange
    certificato = Certificato(
        dipendente=Dipendente(nome="Jane", cognome="Doe"),
        corso=Corso(nome_corso="Test Course", validita_mesi=60, categoria_corso="General"),
        data_rilascio=date(2025, 1, 1),
        data_scadenza_calcolata=date(2025, 1, 1) # Valore iniziale
    )
    db_session.add(certificato)
    db_session.commit()

    update_payload = {
        "nome": "Jane Doe",
        "corso": "Test Course",
        "categoria": "General",
        "data_rilascio": "01/01/2025",
        "data_scadenza": input_scadenza
    }

    # Act
    response = test_client.put(f"/certificati/{certificato.id}", json=update_payload)

    # Assert
    assert response.status_code == 200
    db_session.refresh(certificato)
    assert certificato.data_scadenza_calcolata == expected_db_value
    assert response.json()["data_scadenza"] == expected_response_value

def test_upload_pdf(test_client: TestClient, db_session: Session, mocker):
    """
    Testa l'endpoint di upload PDF, mockando la chiamata al servizio AI
    per rendere il test veloce e deterministico.
    """
    # Arrange: Popola il DB con il corso necessario
    corso_antincendio = Corso(nome_corso="ANTINCENDIO", validita_mesi=60, categoria_corso="ANTINCENDIO")
    db_session.add(corso_antincendio)
    db_session.commit()

    # Arrange: Mock della funzione di estrazione AI
    mocked_extracted_data = {
        "nome": "Mario Rossi",
        "corso": "Corso Sicurezza Base",
        "categoria": "ANTINCENDIO",
        "data_rilascio": "10-10-2025"
    }
    mocker.patch(
        "app.api.main.ai_extraction.extract_entities_with_ai",
        return_value=mocked_extracted_data
    )

    # Crea un file PDF fittizio in memoria
    fake_pdf_bytes = b"%PDF-1.5 fake content"
    files = {"file": ("test.pdf", fake_pdf_bytes, "application/pdf")}

    # Act: Esegui la richiesta di upload
    response = test_client.post("/upload-pdf/", files=files)

    # Assert: Verifica la risposta
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["filename"] == "test.pdf"
    assert response_data["entities"]["nome"] == "Mario Rossi"
    assert response_data["entities"]["data_rilascio"] == "10/10/2025"
    assert "data_scadenza" in response_data["entities"] # Verifica che la logica di calcolo sia stata chiamata

def test_delete_certificato(test_client: TestClient, db_session: Session):
    # Create some test data
    dipendente = Dipendente(nome="Peter", cognome="Jones")
    corso = Corso(nome_corso="Corso di Sicurezza", validita_mesi=36, categoria_corso="TEST")
    db_session.add(dipendente)
    db_session.add(corso)
    db_session.commit()

    certificato = Certificato(
        dipendente_id=dipendente.id,
        corso_id=corso.id,
        data_rilascio=date(2023, 1, 1),
        data_scadenza_calcolata=date(2026, 1, 1),
        stato_validazione=ValidationStatus.MANUAL,
    )
    db_session.add(certificato)
    db_session.commit()

    response = test_client.delete(f"/certificati/{certificato.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Certificato cancellato con successo"
