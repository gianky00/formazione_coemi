from datetime import date

from app.db.models import Dipendente


def test_csv_import_flexible_dates(test_client, db_session):
    # CSV with mixed date formats
    # YYYY-MM-DD for birth, DD/MM/YYYY for hiring
    content = "Cognome;Nome;Data_nascita;Badge;Data_assunzione\nRossi;Mario;1980-01-01;123;01/02/2020\nVerdi;Luigi;01-01-1990;456;2021/03/01"

    response = test_client.post(
        "/dipendenti/import-csv", files={"file": ("dates.csv", content, "text/csv")}
    )
    assert response.status_code == 200

    # Verify Rossi
    rossi = db_session.query(Dipendente).filter(Dipendente.matricola == "123").first()
    assert rossi.data_nascita == date(1980, 1, 1)
    assert rossi.data_assunzione == date(2020, 2, 1)

    # Verify Verdi
    verdi = db_session.query(Dipendente).filter(Dipendente.matricola == "456").first()
    assert verdi.data_nascita == date(1990, 1, 1)
    # 2021/03/01 -> March 1st 2021
    assert verdi.data_assunzione == date(2021, 3, 1)
