from datetime import date, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.db.models import Certificato, Corso, Dipendente, User, ValidationStatus
from app.db.session import get_db

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/summary", response_model=dict[str, Any])
def get_stats_summary(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Any:
    """Ritorna un riepilogo generale delle statistiche."""
    today = date.today()
    threshold = today + timedelta(days=settings.ALERT_THRESHOLD_DAYS)

    total_dipendenti = db.query(Dipendente).count()

    # Only consider Validated Certificates for stats
    base_query = db.query(Certificato).filter(
        Certificato.stato_validazione == ValidationStatus.MANUAL
    )
    total_certificati = base_query.count()

    scaduti = base_query.filter(Certificato.data_scadenza_calcolata < today).count()

    in_scadenza = base_query.filter(
        Certificato.data_scadenza_calcolata >= today,
        Certificato.data_scadenza_calcolata <= threshold,
    ).count()

    validi_safe = base_query.filter(Certificato.data_scadenza_calcolata > threshold).count()

    compliance = 0
    if total_certificati > 0:
        compliance = int(((total_certificati - scaduti) / total_certificati) * 100)

    return {
        "total_dipendenti": total_dipendenti,
        "total_certificati": total_certificati,
        "scaduti": scaduti,
        "in_scadenza": in_scadenza,
        "validi": validi_safe,
        "compliance_percent": compliance,
    }


@router.get("/compliance", response_model=list[dict[str, Any]])
def get_compliance_by_category(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Any:
    """Ritorna la compliance percentuale divisa per categoria di corso."""
    today = date.today()
    threshold = today + timedelta(days=settings.ALERT_THRESHOLD_DAYS)

    results = (
        db.query(
            Corso.categoria_corso,
            func.count(Certificato.id).label("total"),
            func.sum(case((Certificato.data_scadenza_calcolata < today, 1), else_=0)).label(
                "scaduti"
            ),
            func.sum(
                case(
                    (
                        (Certificato.data_scadenza_calcolata >= today)
                        & (Certificato.data_scadenza_calcolata <= threshold),
                        1,
                    ),
                    else_=0,
                )
            ).label("in_scadenza"),
            func.sum(case((Certificato.data_scadenza_calcolata > threshold, 1), else_=0)).label(
                "attivi"
            ),
        )
        .join(Certificato, Corso.id == Certificato.corso_id)
        .filter(Certificato.stato_validazione == ValidationStatus.MANUAL)
        .group_by(Corso.categoria_corso)
        .all()
    )

    data = []
    for row in results:
        cat = str(row[0])
        total = int(row[1] or 0)
        expired = int(row[2] or 0)
        expiring = int(row[3] or 0)
        active = int(row[4] or 0)

        compliance = int((active / total) * 100) if total > 0 else 0
        data.append(
            {
                "category": cat,
                "total": total,
                "active": active,
                "expiring": expiring,
                "expired": expired,
                "compliance": compliance,
            }
        )

    import operator

    data.sort(key=operator.itemgetter("compliance"))
    return data
