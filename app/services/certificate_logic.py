from datetime import date
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from app.db.models import Certificato, Corso

def calculate_expiration_date(issue_date: date, validity_months: int) -> date:
    """
    Calcola la data di scadenza di un certificato.
    """
    if validity_months > 0:
        return issue_date + relativedelta(months=validity_months)
    return None

def get_certificate_status(db: Session, certificato: Certificato) -> str:
    """
    Determina lo stato di un certificato (attivo, scaduto, o rinnovato).
    """
    # Se il certificato non ha data di scadenza, è sempre attivo
    if not certificato.data_scadenza_calcolata:
        return "attivo"

    # Se la data di scadenza è futura, è attivo
    if certificato.data_scadenza_calcolata >= date.today():
        return "attivo"

    # Se è scaduto, controlla se ne esiste uno più recente per lo stesso dipendente e categoria
    newer_cert_exists = db.query(Certificato).join(Corso).filter(
        Certificato.dipendente_id == certificato.dipendente_id,
        Corso.categoria_corso == certificato.corso.categoria_corso,
        Certificato.data_rilascio > certificato.data_rilascio,
        # Considera "attivo" un certificato con data di scadenza futura o nulla
        (Certificato.data_scadenza_calcolata >= date.today()) | (Certificato.data_scadenza_calcolata == None)
    ).first()

    if newer_cert_exists:
        return "rinnovato"
    else:
        return "scaduto"
