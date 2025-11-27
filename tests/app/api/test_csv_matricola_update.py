from datetime import date
from app.db.models import Dipendente, Certificato, Corso
import io

def test_csv_rehiring_update_matricola(test_client, db_session):
    # Setup: Existing employee with OLD matricola
    emp = Dipendente(nome="Mario", cognome="Rossi", matricola="OLD001", data_nascita=date(1980, 1, 1))
    db_session.add(emp)
    emp_historical = Dipendente(nome="Luigi", cognome="Verdi", matricola="HIST01", data_nascita=date(1950, 1, 1))
    db_session.add(emp_historical)
    db_session.commit()
    emp_id = emp.id

    # CSV Content: Mario Rossi with NEW matricola
    csv_content = (
        "Cognome;Nome;Badge;Data_nascita\n"
        "Rossi;Mario;NEW001;01/01/1980\n"
    ).encode('utf-8')
    files = {"file": ("import.csv", io.BytesIO(csv_content), "text/csv")}

    response = test_client.post("/api/v1/dipendenti/import-csv", files=files)
    assert response.status_code == 200

    db_session.expire_all()
    updated_emp = db_session.get(Dipendente, emp_id)

    assert updated_emp.id == emp_id
    assert updated_emp.matricola == "NEW001"
    historical = db_session.query(Dipendente).filter_by(matricola="HIST01").first()
    assert historical is not None

def test_csv_duplicate_error(test_client, db_session):
    # Setup: Two employees with SAME details
    d1 = Dipendente(nome="Giovanni", cognome="Bianchi", matricola="DUP01", data_nascita=date(1990, 1, 1))
    d2 = Dipendente(nome="Giovanni", cognome="Bianchi", matricola="DUP02", data_nascita=date(1990, 1, 1))
    db_session.add_all([d1, d2])
    db_session.commit()

    csv_content = (
        "Cognome;Nome;Badge;Data_nascita\n"
        "Bianchi;Giovanni;NEW999;01/01/1990\n"
    ).encode('utf-8')
    files = {"file": ("import.csv", io.BytesIO(csv_content), "text/csv")}

    response = test_client.post("/api/v1/dipendenti/import-csv", files=files)
    assert response.status_code == 200
    data = response.json()

    assert "warnings" in data and len(data["warnings"]) > 0
    assert "Bianchi Giovanni" in str(data["warnings"])
    db_session.refresh(d1)
    db_session.refresh(d2)
    assert d1.matricola == "DUP01"
    assert d2.matricola == "DUP02"

def test_csv_broad_effect_linking(test_client, db_session):
    emp = Dipendente(nome="Anna", cognome="Neri", matricola="OLD_A", data_nascita=date(1985, 5, 5))
    course = Corso(nome_corso="Test Course", categoria_corso="General", validita_mesi=12)
    db_session.add_all([emp, course])
    db_session.commit()

    cert_auto = Certificato(
        nome_dipendente_raw="Anna Neri", data_nascita_raw=date(1985, 5, 5),
        corso_id=course.id, data_rilascio=date(2023, 1, 1), validated=False
    )
    cert_manual = Certificato(
        nome_dipendente_raw="Anna Neri", data_nascita_raw=date(1985, 5, 5),
        corso_id=course.id, data_rilascio=date(2023, 2, 1), validated=True
    )
    db_session.add_all([cert_auto, cert_manual])
    db_session.commit()

    csv_content = (
        "Cognome;Nome;Badge;Data_nascita\n"
        "Neri;Anna;NEW_A;05/05/1985\n"
    ).encode('utf-8')
    files = {"file": ("import.csv", io.BytesIO(csv_content), "text/csv")}

    response = test_client.post("/api/v1/dipendenti/import-csv", files=files)
    assert response.status_code == 200

    db_session.expire_all()
    db_session.refresh(emp)
    db_session.refresh(cert_auto)
    db_session.refresh(cert_manual)

    assert emp.matricola == "NEW_A"
    assert cert_auto.dipendente_id == emp.id
    assert cert_manual.dipendente_id == emp.id
