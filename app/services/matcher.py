from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.models import Dipendente
from typing import Optional

def find_employee_by_name(db: Session, raw_name: str) -> Optional[Dipendente]:
    """
    Tenta di trovare un dipendente nel database basandosi su una stringa di nome grezzo.
    Cerca combinazioni Nome Cognome e Cognome Nome.
    """
    if not raw_name or not raw_name.strip():
        return None

    nome_parts = raw_name.strip().split()
    if len(nome_parts) < 2:
        return None

    # Assumiamo splitting sul primo spazio per Nome / Cognome o viceversa
    part1, part2 = nome_parts[0], " ".join(nome_parts[1:])

    query = db.query(Dipendente).filter(
        or_(
            (Dipendente.nome.ilike(part1)) & (Dipendente.cognome.ilike(part2)),
            (Dipendente.nome.ilike(part2)) & (Dipendente.cognome.ilike(part1))
        )
    )

    dipendenti = query.all()
    if len(dipendenti) == 1:
        return dipendenti[0]

    return None
