from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import Certificato, Corso
from typing import Optional, List, Dict, Tuple
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
    if issue_date is None:
        return None

    if validity_months > 0:
        result = issue_date + relativedelta(months=validity_months)
        if isinstance(result, datetime):
            return result.date()
        return result
    return None

def get_certificate_status(db: Session, certificato: Certificato) -> str:
    """
    Determina lo stato di un certificato (attivo, scaduto, o archiviato).
    NOTA: Questa funzione esegue query DB ed è inefficiente per liste lunghe.
    Usare get_bulk_certificate_statuses per performance migliori.

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

def get_bulk_certificate_statuses(db: Session, certificati: List[Certificato]) -> Dict[int, str]:
    """
    Calcola lo stato per una lista di certificati in modo efficiente (bulk).
    Restituisce un dizionario {certificato_id: status}.
    """
    if not certificati:
        return {}

    today = date.today()
    status_map = {}

    # 1. Calcola stati basati sulla data (attivo/in_scadenza/scaduto_preliminare)
    #    E identifica quali certificati scaduti necessitano controllo "archiviato".
    expired_linked_certs = [] # (cert)

    threshold_std = settings.ALERT_THRESHOLD_DAYS
    threshold_med = settings.ALERT_THRESHOLD_DAYS_VISITE

    for cert in certificati:
        if cert.data_scadenza_calcolata is None:
            status_map[cert.id] = "attivo"
            continue

        # Determine threshold based on category (optimized access if possible, assumes cert.corso joined)
        threshold = threshold_std
        cat = cert.corso.categoria_corso if cert.corso else ""
        if cat == "VISITA MEDICA":
            threshold = threshold_med

        if cert.data_scadenza_calcolata >= today:
            days = (cert.data_scadenza_calcolata - today).days
            if days <= threshold:
                status_map[cert.id] = "in_scadenza"
            else:
                status_map[cert.id] = "attivo"
        else:
            # Expired. Check if needs archive check.
            if cert.dipendente_id is None:
                status_map[cert.id] = "scaduto"
            else:
                # Potentially archived. We need to check against latest dates.
                # We defer this to the bulk query result.
                expired_linked_certs.append(cert)
                # Default to scaduto, will overwrite if archiviato
                status_map[cert.id] = "scaduto"

    if not expired_linked_certs:
        return status_map

    # 2. Fetch latest release dates for RELEVANT employees/categories only.
    relevant_ids = {c.dipendente_id for c in expired_linked_certs if c.dipendente_id}

    if not relevant_ids:
        return status_map

    stmt = db.query(
        Certificato.dipendente_id,
        Corso.categoria_corso,
        func.max(Certificato.data_rilascio).label('max_rilascio')
    ).join(Corso).filter(
        Certificato.dipendente_id.in_(relevant_ids)
    ).group_by(
        Certificato.dipendente_id,
        Corso.categoria_corso
    )

    latest_results = stmt.all()
    # Map: (dipendente_id, categoria_str) -> max_date
    latest_map = {(r.dipendente_id, r.categoria_corso): r.max_rilascio for r in latest_results}

    # 3. Resolve "Archiviato" status
    for cert in expired_linked_certs:
        # Check if there is a newer date in the map
        category = cert.corso.categoria_corso if cert.corso else None
        if not category: continue

        max_date = latest_map.get((cert.dipendente_id, category))

        if max_date and max_date > cert.data_rilascio:
            status_map[cert.id] = "archiviato"

    return status_map
