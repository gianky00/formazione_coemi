from sqlalchemy.orm import Session
from app.db.models import Dipendente
from datetime import date

def test_dipendenti_crud(test_client, db_session: Session):
    client = test_client
    # 1. Create
    payload = {
        "nome": "Mario",
        "cognome": "Rossi",
        "matricola": "MR001",
        "email": "mario.rossi@test.com",
        "categoria_reparto": "IT",
        "data_assunzione": "2023-01-01",
        "data_nascita": "1990-01-01"
    }
    # Note: test_client base_url includes /api/v1, so we should just use /dipendenti/
    # But let's check conftest base_url. "http://testserver/api/v1".
    # So we should use "/dipendenti/"
    response = client.post("/dipendenti/", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    emp_id = data["id"]
    assert data["email"] == "mario.rossi@test.com"
    assert data["data_assunzione"] == "2023-01-01"

    # 2. Get Detail
    response = client.get(f"/dipendenti/{emp_id}")
    assert response.status_code == 200
    detail = response.json()
    assert detail["matricola"] == "MR001"
    assert detail["certificati"] == []

    # 3. Update
    update_payload = {"categoria_reparto": "HR"}
    response = client.put(f"/dipendenti/{emp_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["categoria_reparto"] == "HR"

    # 4. List
    response = client.get("/dipendenti")
    assert response.status_code == 200
    lst = response.json()
    assert len(lst) >= 1
    found = False
    for item in lst:
        if item["id"] == emp_id:
            assert item["email"] == "mario.rossi@test.com"
            # Note: List schema might not include all fields if I didn't update it,
            # but I updated DipendenteSchema which is used for list too.
            # Let's verify.
            found = True
    assert found

    # 5. Delete
    response = client.delete(f"/dipendenti/{emp_id}")
    assert response.status_code == 200

    # Verify deletion
    response = client.get(f"/dipendenti/{emp_id}")
    assert response.status_code == 404
