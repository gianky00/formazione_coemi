import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models import Dipendente, Corso, Certificato
from datetime import date
from app.services.ai_extraction import AIInvalidJSONError, AIExtractionError

def test_update_certificato_not_found(test_client: TestClient):
    response = test_client.put("/api/v1/certificati/99999", json={"nome": "Any Name"})
    assert response.status_code == 404

def test_update_certificato_invalid_name(test_client: TestClient, db_session: Session):
    cert = Certificato(
        corso=db_session.query(Corso).filter_by(categoria_corso="General").one(),
        data_rilascio=date(2025, 1, 1)
    )
    db_session.add(cert)
    db_session.commit()

    response_empty = test_client.put(f"/api/v1/certificati/{cert.id}", json={"nome": " "})
    assert response_empty.status_code == 400
    
    response_short = test_client.put(f"/api/v1/certificati/{cert.id}", json={"nome": "Mario"})
    assert response_short.status_code == 400

def test_update_certificato_invalid_category(test_client: TestClient, db_session: Session):
    cert = Certificato(
        corso=db_session.query(Corso).filter_by(categoria_corso="General").one(),
        data_rilascio=date(2025, 1, 1)
    )
    db_session.add(cert)
    db_session.commit()

    response = test_client.put(f"/api/v1/certificati/{cert.id}", json={"categoria": "NON_EXISTENT"})
    assert response.status_code == 404

def test_valida_certificato_not_found(test_client: TestClient):
    response = test_client.put("/api/v1/certificati/99999/valida")
    assert response.status_code == 404

def test_delete_certificato_not_found(test_client: TestClient):
    response = test_client.delete("/api/v1/certificati/99999")
    assert response.status_code == 404

def test_import_dipendenti_csv_invalid_extension(test_client: TestClient):
    response = test_client.post("/api/v1/dipendenti/import-csv", files={"file": ("test.txt", b"c", "text/plain")})
    assert response.status_code == 400

def test_upload_pdf_ai_error(test_client: TestClient, mocker):
    mocker.patch("app.api.main.ai_extraction.extract_entities_with_ai", side_effect=AIExtractionError("AI service down"))
    
    response = test_client.post("/api/v1/upload-pdf/", files={"file": ("test.pdf", b"%PDF-", "application/pdf")})
    assert response.status_code == 503
    assert "AI service down" in response.json()["detail"]
