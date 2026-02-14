from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Certificato, Corso


def calculate_expiration_date(issue_date: date | None, validity_months: int) -> date | None:
    """
    Calcola la data di scadenza di un certificato.
    """
    if issue_date is None:
        return None

    if validity_months > 0:
        result = issue_date + relativedelta(months=validity_months)
        if isinstance(result, datetime):
            return result.date()
        # relativedelta + date normally returns date, but Mypy can be strict
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

    newer_cert_exists = (
        db.query(Certificato)
        .join(Corso)
        .filter(
            Certificato.dipendente_id == certificato.dipendente_id,
            Corso.categoria_corso == certificato.corso.categoria_corso,
            Certificato.data_rilascio > certificato.data_rilascio,
        )
        .first()
    )

    return "archiviato" if newer_cert_exists else "scaduto"


def calculate_combined_data(certificato: Certificato) -> None:
    """
    Ricalcola la data di scadenza calcolata basandosi sulla data di rilascio
    e sulla validità del corso, se non impostata manualmente.
    """
    if certificato.data_scadenza_manuale:
        certificato.data_scadenza_calcolata = certificato.data_scadenza_manuale
    elif certificato.data_rilascio and certificato.corso and certificato.corso.validita_mesi > 0:
        certificato.data_scadenza_calcolata = calculate_expiration_date(
            certificato.data_rilascio, certificato.corso.validita_mesi
        )
    else:
        certificato.data_scadenza_calcolata = certificato.data_scadenza_manuale


def _determine_initial_status(
    cert: Certificato, today: date, threshold_std: int, threshold_med: int
) -> tuple[str, bool]:
    if cert.data_scadenza_calcolata is None:
        return "attivo", False

    threshold = (
        threshold_med
        if cert.corso and cert.corso.categoria_corso == "VISITA MEDICA"
        else threshold_std
    )

    if cert.data_scadenza_calcolata >= today:
        days = (cert.data_scadenza_calcolata - today).days
        return "in_scadenza" if days <= threshold else "attivo", False

    # Expired
    needs_archive_check = cert.dipendente_id is not None
    return "scaduto", needs_archive_check


def _fetch_latest_dates(
    db: Session, expired_linked_certs: list[Certificato]
) -> dict[tuple[int, str], date]:
    relevant_ids = {c.dipendente_id for c in expired_linked_certs if c.dipendente_id}
    if not relevant_ids:
        return {}

    stmt = (
        db.query(
            Certificato.dipendente_id,
            Corso.categoria_corso,
            func.max(Certificato.data_rilascio).label("max_rilascio"),
        )
        .join(Corso)
        .filter(Certificato.dipendente_id.in_(relevant_ids))
        .group_by(Certificato.dipendente_id, Corso.categoria_corso)
    )

    latest_results = stmt.all()
    # Ensure correct typing for the map
    return {(int(r.dipendente_id), str(r.categoria_corso)): r.max_rilascio for r in latest_results}


def get_bulk_certificate_statuses(db: Session, certificati: list[Certificato]) -> dict[int, str]:
    if not certificati:
        return {}

    today = date.today()
    status_map: dict[int, str] = {}
    expired_linked_certs: list[Certificato] = []

    threshold_std = settings.ALERT_THRESHOLD_DAYS
    threshold_med = settings.ALERT_THRESHOLD_DAYS_VISITE

    for cert in certificati:
        status, needs_check = _determine_initial_status(cert, today, threshold_std, threshold_med)
        status_map[int(cert.id)] = status
        if needs_check:
            expired_linked_certs.append(cert)

    if not expired_linked_certs:
        return status_map

    latest_map = _fetch_latest_dates(db, expired_linked_certs)

    for cert in expired_linked_certs:
        category = cert.corso.categoria_corso if cert.corso else None
        if not category or cert.dipendente_id is None:
            continue

        max_date = latest_map.get((int(cert.dipendente_id), str(category)))
        if max_date and max_date > cert.data_rilascio:
            status_map[int(cert.id)] = "archiviato"

    return status_map
