from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from app.db.models import Corso

def calculate_expiration_date(issue_date: date, validity_months: int) -> date:
    """
    Calcola la data di scadenza di un certificato.
    """
    if validity_months > 0:
        return issue_date + relativedelta(months=validity_months)
    return None

def get_certificate_status(expiration_date: date) -> str:
    """
    Determina lo stato di un certificato (attivo o scaduto).
    """
    if expiration_date and expiration_date < date.today():
        return "scaduto"
    return "attivo"
