from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.db.models import Corso
from app.db.session import get_db

router = APIRouter(prefix="/corsi", tags=["courses"])


@router.get("", response_model=list[dict[str, Any]])
def get_corsi(
    db: Annotated[Session, Depends(get_db)],
    license: Annotated[bool, Depends(deps.verify_license)],
) -> Any:
    """Ritorna l'elenco di tutti i corsi registrati."""
    return db.query(Corso).all()
