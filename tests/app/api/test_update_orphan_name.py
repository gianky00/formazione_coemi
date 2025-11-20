def test_update_orphan_certificate_name(test_client):
    # 1. Create an orphan certificate
    payload = {
        "nome": "Ghost Rider",
        "corso": "HLO",
        "categoria": "HLO",
        "data_rilascio": "01/01/2023",
        "data_scadenza": "01/01/2028"
    }
    response = test_client.post("/certificati/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Ghost Rider"
    cert_id = data["id"]

    # 2. Update the name to another orphan name
    update_payload = {
        "nome": "Spirit of Vengeance"
    }
    response = test_client.put(f"/certificati/{cert_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()

    # This is where I expect the bug
    assert data["nome"] == "Spirit of Vengeance"

    # 3. Verify persistence
    response = test_client.get(f"/certificati/{cert_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Spirit of Vengeance"
