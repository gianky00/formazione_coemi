from datetime import date
from app.db.models import Dipendente, Certificato, Corso

def test_update_certificato_homonym_linking(test_client, db_session):
    """
    Tests that when a certificate's name is updated, the system correctly uses
    the date of birth to link it to the correct employee among homonyms.
    """
    # 1. Setup Employees with the same name but different DOBs
    emp1 = Dipendente(nome="Mario", cognome="Rossi", matricola="M01", data_nascita=date(1980, 1, 1))
    emp2 = Dipendente(nome="Mario", cognome="Rossi", matricola="M02", data_nascita=date(1990, 1, 1))
    course = Corso(nome_corso="Homonym Test", categoria_corso="General", validita_mesi=12)
    db_session.add_all([emp1, emp2, course])
    db_session.commit()

    # 2. Create an orphaned certificate with a slightly misspelled name but the correct DOB for emp1
    cert = Certificato(
        nome_dipendente_raw="Mario Ross",
        data_nascita_raw=date(1980, 1, 1), # DOB for emp1
        corso_id=course.id,
        data_rilascio=date(2023, 1, 1),
        validated=False
    )
    db_session.add(cert)
    db_session.commit()
    assert cert.dipendente_id is None

    # 3. Update the name to the correct "Mario Rossi"
    payload = {"nome": "Mario Rossi"}
    response = test_client.put(f"/api/v1/certificati/{cert.id}", json=payload)
    
    # 4. Assert that the certificate is now linked specifically to emp1
    assert response.status_code == 200
    data = response.json()
    assert data["matricola"] == "M01" # Should link to the employee with the matching DOB

    db_session.refresh(cert)
    assert cert.dipendente_id == emp1.id

def test_update_certificato_data_nascita(test_client, db_session):
    """
    Tests that a certificate's date of birth can be updated, which can
    change its employee linkage.
    """
    # 1. Setup employees and an orphan certificate linked to emp1's DOB
    emp1 = Dipendente(nome="Jane", cognome="Doe", matricola="J01", data_nascita=date(1985, 5, 5))
    emp2 = Dipendente(nome="Jane", cognome="Doe", matricola="J02", data_nascita=date(1995, 10, 10))
    course = Corso(nome_corso="DOB Update", categoria_corso="General", validita_mesi=12)
    db_session.add_all([emp1, emp2, course])
    db_session.commit()

    cert = Certificato(
        nome_dipendente_raw="Jane Doe",
        data_nascita_raw=date(1985, 5, 5), # Initially matches emp1
        corso_id=course.id,
        data_rilascio=date(2023, 1, 1),
    )
    db_session.add(cert)
    db_session.commit()

    # Link it to emp1 first by updating the name
    test_client.put(f"/api/v1/certificati/{cert.id}", json={"nome": "Jane Doe"})
    db_session.refresh(cert)
    assert cert.dipendente_id == emp1.id

    # 2. Now, update only the date of birth to match emp2
    payload = {"data_nascita": "10/10/1995"}
    response = test_client.put(f"/api/v1/certificati/{cert.id}", json=payload)
    assert response.status_code == 200
    data = response.json()

    # 3. Assert that the certificate is now linked to emp2
    assert data["matricola"] == "J02"
    db_session.refresh(cert)
    assert cert.dipendente_id == emp2.id
