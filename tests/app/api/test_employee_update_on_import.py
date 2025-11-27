import io
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models import Dipendente
from datetime import date

def test_employee_update_on_csv_import(test_client: TestClient, db_session: Session):
    """
    Tests that importing a CSV file correctly updates the details of an
    existing employee identified by the same 'matricola' (badge number).
    """
    # 1. Pre-populate the database with an existing employee
    initial_employee = Dipendente(
        nome="Original Name",
        cognome="Original Surname",
        matricola="E001",
        data_nascita=date(1985, 10, 10)
    )
    db_session.add(initial_employee)
    db_session.commit()
    employee_id = initial_employee.id

    # 2. Create a CSV with updated information for the same employee
    csv_content = (
        "Cognome;Nome;Data_nascita;Badge\n"
        "Updated Surname;Updated Name;25/12/1995;E001"
    ).encode('utf-8')
    files = {"file": ("update.csv", io.BytesIO(csv_content), "text/csv")}

    # 3. Call the import endpoint
    response = test_client.post("/api/v1/dipendenti/import-csv", files=files)
    assert response.status_code == 200

    # 4. Verify the employee's record was updated in the database
    db_session.expire_all() # Ensure we get the latest data from the DB
    updated_employee = db_session.get(Dipendente, employee_id)
    
    assert updated_employee is not None
    assert updated_employee.nome == "Updated Name"
    assert updated_employee.cognome == "Updated Surname"
    assert updated_employee.data_nascita == date(1995, 12, 25)
