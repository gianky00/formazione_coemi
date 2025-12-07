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

    if certificato.dipendente_id is None:
        return "scaduto"

    newer_cert_exists = db.query(Certificato).join(Corso).filter(
        Certificato.dipendente_id == certificato.dipendente_id,
        Corso.categoria_corso == certificato.corso.categoria_corso,
        Certificato.data_rilascio > certificato.data_rilascio
    ).first()

    return "archiviato" if newer_cert_exists else "scaduto"

def _determine_initial_status(cert, today, threshold_std, threshold_med):
    if cert.data_scadenza_calcolata is None:
        return "attivo", False

    threshold = threshold_med if cert.corso and cert.corso.categoria_corso == "VISITA MEDICA" else threshold_std

    if cert.data_scadenza_calcolata >= today:
        days = (cert.data_scadenza_calcolata - today).days
        return "in_scadenza" if days <= threshold else "attivo", False

    # Expired
    needs_archive_check = cert.dipendente_id is not None
    return "scaduto", needs_archive_check

def _fetch_latest_dates(db, expired_linked_certs):
    relevant_ids = {c.dipendente_id for c in expired_linked_certs if c.dipendente_id}
    if not relevant_ids:
        return {}

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
    return {(r.dipendente_id, r.categoria_corso): r.max_rilascio for r in latest_results}

def get_bulk_certificate_statuses(db: Session, certificati: List[Certificato]) -> Dict[int, str]:
    # S3776: Refactored to reduce complexity
    if not certificati:
        return {}

    today = date.today()
    status_map = {}
    expired_linked_certs = []

    threshold_std = settings.ALERT_THRESHOLD_DAYS
    threshold_med = settings.ALERT_THRESHOLD_DAYS_VISITE

    for cert in certificati:
        status, needs_check = _determine_initial_status(cert, today, threshold_std, threshold_med)
        status_map[cert.id] = status
        if needs_check:
            expired_linked_certs.append(cert)

    if not expired_linked_certs:
        return status_map

    latest_map = _fetch_latest_dates(db, expired_linked_certs)

    for cert in expired_linked_certs:
        category = cert.corso.categoria_corso if cert.corso else None
        if not category: continue

        max_date = latest_map.get((cert.dipendente_id, category))
        if max_date and max_date > cert.data_rilascio:
            status_map[cert.id] = "archiviato"

    return status_map
