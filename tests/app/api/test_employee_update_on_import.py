import io
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models import Dipendente
from datetime import date

def test_employee_update_on_csv_import(test_client: TestClient, db_session: Session):
    # 1. Create an employee
    emp = Dipendente(
        nome="OldName",
        cognome="OldSurname",
        matricola="12345",
        data_nascita=date(1980, 1, 1)
    )
    db_session.add(emp)
    db_session.commit()

    # 2. Import CSV with updated details for the same matricola
    # Note: CSV format is Cognome;Nome;Data_nascita;Badge
    csv_content = b"Cognome;Nome;Data_nascita;Badge\nNewSurname;NewName;01/01/1990;12345"
    files = {"file": ("dipendenti.csv", io.BytesIO(csv_content), "text/csv")}

    response = test_client.post("/dipendenti/import-csv", files=files)
    assert response.status_code == 200

    # 3. Verify the employee record is updated
    db_session.refresh(emp)
    assert emp.nome == "NewName"
    assert emp.cognome == "NewSurname"
    assert emp.data_nascita == date(1990, 1, 1)
