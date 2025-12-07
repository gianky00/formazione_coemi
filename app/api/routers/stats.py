from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.db.session import get_db
from app.db.models import Certificato, Dipendente, Corso, ValidationStatus
from app.api import deps
from datetime import date, timedelta
from app.core.config import settings

router = APIRouter()

@router.get("/summary")
def get_stats_summary(db: Session = Depends(get_db), current_user = Depends(deps.get_current_user)):
    today = date.today()
    threshold = today + timedelta(days=settings.ALERT_THRESHOLD_DAYS)

    total_dipendenti = db.query(Dipendente).count()

    # Only consider Validated Certificates for stats
    base_query = db.query(Certificato).filter(Certificato.stato_validazione == ValidationStatus.MANUAL)
    total_certificati = base_query.count()

    scaduti = base_query.filter(Certificato.data_scadenza_calcolata < today).count()

    in_scadenza = base_query.filter(
        Certificato.data_scadenza_calcolata >= today,
        Certificato.data_scadenza_calcolata <= threshold
    ).count()

    validi_safe = base_query.filter(Certificato.data_scadenza_calcolata > threshold).count()

    compliance = 0
    if total_certificati > 0:
        # S125: Removed commented out code
        compliance = int(((total_certificati - scaduti) / total_certificati) * 100)

    return {
        "total_dipendenti": total_dipendenti,
        "total_certificati": total_certificati,
        "scaduti": scaduti,
        "in_scadenza": in_scadenza,
        "validi": validi_safe,
        "compliance_percent": compliance
    }

@router.get("/compliance")
def get_compliance_by_category(db: Session = Depends(get_db), current_user = Depends(deps.get_current_user)):
    today = date.today()

    results = db.query(
        Corso.categoria_corso,
        func.count(Certificato.id).label("total"),
        func.sum(case((Certificato.data_scadenza_calcolata < today, 1), else_=0)).label("scaduti")
    ).join(Certificato, Corso.id == Certificato.corso_id)\
     .filter(Certificato.stato_validazione == ValidationStatus.MANUAL)\
     .group_by(Corso.categoria_corso).all()

    data = []
    for row in results:
        cat = row[0]
        total = row[1]
        scaduti = row[2] or 0
        valid_cnt = total - scaduti
        percent = int((valid_cnt / total) * 100) if total > 0 else 0
        data.append({
            "category": cat,
            "total": total,
            "scaduti": scaduti,
            "compliance": percent
        })

    data.sort(key=lambda x: x['compliance'])
    return data
