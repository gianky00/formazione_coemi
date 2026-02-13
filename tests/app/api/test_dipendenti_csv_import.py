from sqlalchemy.orm import Session

from app.db.models import Dipendente


def test_csv_import_with_hiring_date(test_client, db_session: Session):
    client = test_client

    # CSV Content: id_risorsa;Cognome;Nome;Data_nascita;Badge;Data_assunzione
    csv_content = """id_risorsa;Cognome;Nome;Data_nascita;Badge;Data_assunzione
101;Bianchi;Luigi;15/05/1985;B001;01/02/2023
102;Verdi;Mario;20/10/1990;B002;
"""
    files = {"file": ("test.csv", csv_content, "text/csv")}
    # Note: test_client base_url includes /api/v1 from conftest
    # Endpoint is /dipendenti/import-csv
    response = client.post("/dipendenti/import-csv", files=files)
    assert response.status_code == 200, response.text

    # Verify Bianchi
    bianchi = db_session.query(Dipendente).filter(Dipendente.matricola == "B001").first()
    assert bianchi is not None
    assert bianchi.nome == "Luigi"
    assert bianchi.data_assunzione is not None
    assert bianchi.data_assunzione.strftime("%Y-%m-%d") == "2023-02-01"

    # Verify Verdi (Empty Data_assunzione)
    verdi = db_session.query(Dipendente).filter(Dipendente.matricola == "B002").first()
    assert verdi is not None
    assert verdi.data_assunzione is None
