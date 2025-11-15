from datetime import date
from dateutil.relativedelta import relativedelta
from app.services.certificate_logic import calculate_expiration_date, get_certificate_status

def test_calculate_expiration_date():
    """
    Testa la funzione di calcolo della data di scadenza.
    """
    issue_date = date(2025, 1, 1)

    # Test con validità in mesi
    assert calculate_expiration_date(issue_date, 12) == date(2026, 1, 1)
    assert calculate_expiration_date(issue_date, 36) == date(2028, 1, 1)

    # Test con validità zero (nessuna scadenza)
    assert calculate_expiration_date(issue_date, 0) is None

def test_get_certificate_status():
    """
    Testa la funzione che determina lo stato del certificato.
    """
    today = date.today()

    # Test con certificato attivo (scadenza futura)
    future_date = today + relativedelta(months=1)
    assert get_certificate_status(future_date) == "attivo"

    # Test con certificato scaduto (scadenza passata)
    past_date = today - relativedelta(months=1)
    assert get_certificate_status(past_date) == "scaduto"

    # Test con certificato senza data di scadenza
    assert get_certificate_status(None) == "attivo"
