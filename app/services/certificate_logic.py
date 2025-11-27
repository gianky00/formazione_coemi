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

from app.schemas.schemas import CertificatoSchema

def get_certificate_status(db: Session, certificato: Certificato) -> str:
    """
    Determina lo stato di un certificato (attivo, in_scadenza, scaduto, archiviato).
    Questa funzione è robusta ai valori `None` nelle date.
    """
    if certificato.data_scadenza_calcolata is None:
        return "attivo"  # Considerato sempre attivo se non ha scadenza

    today = date.today()

    if certificato.data_scadenza_calcolata >= today:
        days_to_expire = (certificato.data_scadenza_calcolata - today).days
        
        # Gestisce il caso in cui il corso potrebbe essere None
        threshold = settings.ALERT_THRESHOLD_DAYS
        if certificato.corso and certificato.corso.categoria_corso == "VISITA MEDICA":
            threshold = settings.ALERT_THRESHOLD_DAYS_VISITE
        
        return "in_scadenza" if days_to_expire <= threshold else "attivo"

    # Se scaduto, controlla se è stato rinnovato
    if certificato.dipendente_id is None:
        return "scaduto"  # Orfano e scaduto

    # La data di rilascio è necessaria per verificare il rinnovo
    if certificato.data_rilascio is None:
        return "scaduto" # Scaduto ma non possiamo determinare se è stato rinnovato

    newer_cert_exists = db.query(Certificato).filter(
        Certificato.dipendente_id == certificato.dipendente_id,
        Certificato.corso_id == certificato.corso_id,
        Certificato.data_rilascio > certificato.data_rilascio
    ).first()

    return "archiviato" if newer_cert_exists else "scaduto"

def serialize_certificato(db: Session, certificato: Certificato) -> CertificatoSchema:
    """
    Serializza un oggetto Certificato ORM in uno schema Pydantic,
    calcolando lo stato e gestendo in modo sicuro i dipendenti orfani.
    """
    stato = get_certificate_status(db, certificato)
    
    # Gestione dipendente orfano
    if certificato.dipendente:
        nome_completo = f"{certificato.dipendente.cognome} {certificato.dipendente.nome}"
        matricola = certificato.dipendente.matricola
        data_nascita_dipendente = certificato.dipendente.data_nascita
    else:
        nome_completo = certificato.nome_dipendente_raw or "N/A"
        matricola = None
        data_nascita_dipendente = certificato.data_nascita_raw

    return CertificatoSchema(
        id=certificato.id,
        nome=nome_completo,
        corso=certificato.corso.nome_corso if certificato.corso else "N/A",
        data_rilascio=certificato.data_rilascio,
        data_scadenza_calcolata=certificato.data_scadenza_calcolata,
        stato_certificato=stato,
        validated=certificato.validated,
        categoria_corso=certificato.corso.categoria_corso if certificato.corso else "N/A",
        assegnazione_fallita_ragione=certificato.assegnazione_fallita_ragione,
        matricola=matricola,
        data_nascita=data_nascita_dipendente
    )
