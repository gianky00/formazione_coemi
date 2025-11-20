from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from app.db.models import Certificato, Corso
from typing import Optional
from app.core.config import settings

def calculate_expiration_date(issue_date: date, validity_months: int) -> Optional[date]:
    """
    Calcola la data di scadenza di un certificato.

    Args:
        issue_date: La data di rilascio del certificato.
        validity_months: Il numero di mesi di validità del corso.

    Returns:
        La data di scadenza calcolata, o None se la validità è zero.
    """
    if validity_months > 0:
        result = issue_date + relativedelta(months=validity_months)
        if isinstance(result, datetime):
            return result.date()
        return result
    return None

def get_certificate_status(db: Session, certificato: Certificato) -> str:
    """
    Determina lo stato di un certificato (attivo, scaduto, o archiviato).

    Args:
        db: La sessione del database.
        certificato: L'oggetto Certificato da valutare.

    Returns:
        Lo stato del certificato come stringa ('attivo', 'scaduto', 'archiviato').
    """
    if certificato.data_scadenza_calcolata is None:
        return "attivo"

    today = date.today()

    if certificato.data_scadenza_calcolata >= today:
        days_to_expire = (certificato.data_scadenza_calcolata - today).days
        threshold = settings.ALERT_THRESHOLD_DAYS

        if certificato.corso and certificato.corso.categoria_corso == "VISITA MEDICA":
            threshold = settings.ALERT_THRESHOLD_DAYS_VISITE

        if days_to_expire <= threshold:
            return "in_scadenza"
        return "attivo"

    # If the certificate is not linked to an employee, it cannot be considered "renewed"
    # by another certificate (even another orphan).
    if certificato.dipendente_id is None:
        return "scaduto"

    newer_cert_exists = db.query(Certificato).join(Corso).filter(
        Certificato.dipendente_id == certificato.dipendente_id,
        Corso.categoria_corso == certificato.corso.categoria_corso,
        Certificato.data_rilascio > certificato.data_rilascio
    ).first()

    return "archiviato" if newer_cert_exists else "scaduto"
