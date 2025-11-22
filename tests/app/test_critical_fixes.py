import pytest
from datetime import date
from io import BytesIO
from app.db.models import Dipendente, Corso, Certificato, ValidationStatus

def test_duplicate_certificate_conflict(test_client, db_session):
    """
    Test that creating a duplicate certificate returns 409 Conflict.
    """
    # 1. Create a certificate via API
    payload = {
        "nome": "Mario Rossi",
        "data_nascita": "01/01/1980",
        "corso": "Corso A",
        "categoria": "CAT A",
        "data_rilascio": "01/01/2023",
        "data_scadenza": "01/01/2024"
    }
    response = test_client.post("/certificati/", json=payload)
    assert response.status_code == 200

    # 2. Try to create the exact same certificate again
    response2 = test_client.post("/certificati/", json=payload)
    assert response2.status_code == 409
    assert "esiste già" in response2.json()["detail"]

def test_homonym_resolution(test_client, db_session):
    """
    Test that homonyms are resolved using date of birth.
    """
    # 1. Create two employees with same name but different DOB
    emp1 = Dipendente(nome="Mario", cognome="Rossi", matricola="M001", data_nascita=date(1980, 1, 1))
    emp2 = Dipendente(nome="Mario", cognome="Rossi", matricola="M002", data_nascita=date(1990, 5, 5))
    db_session.add(emp1)
    db_session.add(emp2)
    db_session.commit()

    # 2. Create certificate for Mario Rossi (1980)
    payload1 = {
        "nome": "Mario Rossi",
        "data_nascita": "01/01/1980",
        "corso": "Corso 1",
        "categoria": "CAT 1",
        "data_rilascio": "01/01/2023",
        "data_scadenza": "01/01/2024"
    }
    resp1 = test_client.post("/certificati/", json=payload1)
    assert resp1.status_code == 200
    assert resp1.json()["matricola"] == "M001"

    # 3. Create certificate for Mario Rossi (1990)
    payload2 = {
        "nome": "Mario Rossi",
        "data_nascita": "05/05/1990",
        "corso": "Corso 2",
        "categoria": "CAT 2", # Different category to avoid duplicate check if course name matches
        "data_rilascio": "01/01/2023",
        "data_scadenza": "01/01/2024"
    }
    resp2 = test_client.post("/certificati/", json=payload2)
    assert resp2.status_code == 200
    assert resp2.json()["matricola"] == "M002"

    # 4. Create certificate for Mario Rossi (Unknown DOB) -> Should be Orphan/Ambiguous
    payload3 = {
        "nome": "Mario Rossi",
        "data_nascita": None,
        "corso": "Corso 3",
        "categoria": "CAT 3",
        "data_rilascio": "01/01/2023",
        "data_scadenza": "01/01/2024"
    }
    resp3 = test_client.post("/certificati/", json=payload3)
    assert resp3.status_code == 200
    assert resp3.json()["matricola"] is None
    assert "Assegnare" in resp3.json()["nome"] or resp3.json()["matricola"] is None

def test_csv_import_latin1(test_client, db_session):
    """
    Test importing a CSV with Latin-1 encoding (common for Excel).
    """
    # Create content with special char (e.g. à) in Latin-1
    content = "Cognome;Nome;Data_nascita;Badge\nRossì;Mario;01/01/1980;M100"
    content_latin1 = content.encode("latin-1")

    files = {"file": ("test.csv", content_latin1, "text/csv")}
    resp = test_client.post("/dipendenti/import-csv", files=files)
    assert resp.status_code == 200

    # Verify it was imported correctly (decoded properly)
    emp = db_session.query(Dipendente).filter_by(matricola="M100").first()
    assert emp is not None
    assert emp.cognome == "Rossì"  # Should be decoded correctly

def test_csv_size_limit(test_client):
    """
    Test that CSV larger than 5MB is rejected.
    """
    # Create 6MB content
    large_content = b"a" * (6 * 1024 * 1024)
    files = {"file": ("large.csv", large_content, "text/csv")}
    resp = test_client.post("/dipendenti/import-csv", files=files)
    assert resp.status_code == 413
    assert "5MB" in resp.json()["detail"]

def test_pdf_size_limit(test_client):
    """
    Test that PDF larger than 20MB is rejected.
    """
    large_content = b"a" * (21 * 1024 * 1024)
    files = {"file": ("large.pdf", large_content, "application/pdf")}
    resp = test_client.post("/upload-pdf/", files=files)
    assert resp.status_code == 413
    assert "20MB" in resp.json()["detail"]

def test_pdf_date_correction(test_client, mock_ai_service):
    """
    Test that upload-pdf corrects date formats.
    """
    # Mock AI response with weird date format
    mock_ai_service.return_value = {
        "nome": "Test User",
        "categoria": "TEST",
        "corso": "Test Course",
        "data_rilascio": "2023-01-31", # YYYY-MM-DD
        "data_scadenza": "31-01-2024", # DD-MM-YYYY
        "data_nascita": "31.01.1980"   # DD.MM.YYYY
    }

    files = {"file": ("test.pdf", b"%PDF-1.4 dummy content", "application/pdf")}
    resp = test_client.post("/upload-pdf/", files=files)
    assert resp.status_code == 200

    entities = resp.json()["entities"]
    # All should be normalized to DD/MM/YYYY
    assert entities["data_rilascio"] == "31/01/2023"
    assert entities["data_scadenza"] == "31/01/2024"
    assert entities["data_nascita"] == "31/01/1980"
