import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models import Dipendente, Corso, Certificato, ValidationStatus
from datetime import date

def seed_master_courses(db: Session):
    corsi = [
        {"nome_corso": "ANTINCENDIO", "validita_mesi": 60, "categoria_corso": "ANTINCENDIO"},
        {"nome_corso": "PRIMO SOCCORSO", "validita_mesi": 36, "categoria_corso": "PRIMO SOCCORSO"},
        {"nome_corso": "General", "validita_mesi": 12, "categoria_corso": "General"},
    ]
    for corso_data in corsi:
        if not db.query(Corso).filter_by(nome_corso=corso_data["nome_corso"]).first():
            db.add(Corso(**corso_data))
    db.commit()

def test_update_certificato_not_found(test_client: TestClient, db_session: Session):
    response = test_client.put("/certificati/9999", json={"nome": "Mario Rossi"})
    assert response.status_code == 404
    assert "Certificato non trovato" in response.json()["detail"]

def test_update_certificato_invalid_name(test_client: TestClient, db_session: Session):
    seed_master_courses(db_session)
    cert = Certificato(
        dipendente=Dipendente(nome="Jane", cognome="Doe"),
        corso=db_session.query(Corso).filter_by(nome_corso="General").one(),
        data_rilascio=date(2025, 1, 1)
    )
    db_session.add(cert)
    db_session.commit()

    response = test_client.put(f"/certificati/{cert.id}", json={"nome": ""})
    assert response.status_code == 400
    assert "Il nome non può essere vuoto" in response.json()["detail"]

    response = test_client.put(f"/certificati/{cert.id}", json={"nome": "Mario"})
    assert response.status_code == 400
    assert "Formato nome non valido" in response.json()["detail"]

def test_update_certificato_invalid_category(test_client: TestClient, db_session: Session):
    seed_master_courses(db_session)
    cert = Certificato(
        dipendente=Dipendente(nome="Jane", cognome="Doe"),
        corso=db_session.query(Corso).filter_by(nome_corso="General").one(),
        data_rilascio=date(2025, 1, 1)
    )
    db_session.add(cert)
    db_session.commit()

    response = test_client.put(f"/certificati/{cert.id}", json={"categoria": "NON_EXISTENT"})
    assert response.status_code == 404
    assert "Categoria 'NON_EXISTENT' non trovata" in response.json()["detail"]

def test_valida_certificato_not_found(test_client: TestClient):
    response = test_client.put("/certificati/9999/valida")
    assert response.status_code == 404
    assert "Certificato non trovato" in response.json()["detail"]

def test_delete_certificato_not_found(test_client: TestClient):
    response = test_client.delete("/certificati/9999")
    assert response.status_code == 404
    assert "Certificato non trovato" in response.json()["detail"]

def test_import_dipendenti_csv_invalid_extension(test_client: TestClient):
    response = test_client.post("/dipendenti/import-csv", files={"file": ("test.txt", b"content", "text/plain")})
    assert response.status_code == 400
    assert "Il file deve essere in formato CSV" in response.json()["detail"]

def test_upload_pdf_ai_error(test_client: TestClient, mocker):
    mocker.patch("app.api.main.ai_extraction.extract_entities_with_ai", return_value={"error": "AI Error"})
    # Must include %PDF- header
    response = test_client.post("/upload-pdf/", files={"file": ("test.pdf", b"%PDF-1.4 content", "application/pdf")})
    assert response.status_code == 500
    assert "AI Error" in response.json()["detail"]
