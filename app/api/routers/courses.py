from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.db.models import Corso
from app.db.session import get_db

router = APIRouter(prefix="/corsi", tags=["courses"])


@router.get("", response_model=list)
def get_corsi(db: Session = Depends(get_db), license: bool = Depends(deps.verify_license)):
    """Ritorna l'elenco di tutti i corsi registrati."""
    return db.query(Corso).all()
