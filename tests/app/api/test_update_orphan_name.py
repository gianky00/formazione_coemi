from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models import Corso

def test_update_orphan_certificate_name(test_client: TestClient, db_session: Session):
    """
    Tests that the name of an orphaned certificate can be successfully updated.
    """
    # 1. Setup: Ensure the 'HLO' course category exists
    if not db_session.query(Corso).filter_by(categoria_corso="HLO").first():
        db_session.add(Corso(nome_corso="HLO", categoria_corso="HLO", validita_mesi=24))
        db_session.commit()

    # 2. Create an orphan certificate
    create_payload = {
        "nome": "Original Orphan Name",
        "corso": "HLO",
        "categoria": "HLO",
        "data_rilascio": "01/01/2024",
    }
    response_create = test_client.post("/api/v1/certificati/", json=create_payload)
    assert response_create.status_code == 200
    cert_id = response_create.json()["id"]
    assert response_create.json()["nome"] == "Original Orphan Name"

    # 3. Update the name of the orphan certificate
    update_payload = {"nome": "Updated Orphan Name"}
    response_update = test_client.put(f"/api/v1/certificati/{cert_id}", json=update_payload)
    assert response_update.status_code == 200
    assert response_update.json()["nome"] == "Updated Orphan Name"

    # 4. Verify that the name change has persisted
    response_get = test_client.get(f"/api/v1/certificati/{cert_id}")
    assert response_get.status_code == 200
    assert response_get.json()["nome"] == "Updated Orphan Name"
