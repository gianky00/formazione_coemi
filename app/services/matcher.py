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

    found_employees = {}

    # Try all possible splits
    for i in range(1, len(nome_parts)):
        part1 = " ".join(nome_parts[:i])
        part2 = " ".join(nome_parts[i:])

        query = db.query(Dipendente).filter(
            or_(
                (Dipendente.nome.ilike(part1)) & (Dipendente.cognome.ilike(part2)),
                (Dipendente.nome.ilike(part2)) & (Dipendente.cognome.ilike(part1))
            )
        )

        matches = query.all()
        for emp in matches:
            found_employees[emp.id] = emp

    if len(found_employees) == 1:
        return list(found_employees.values())[0]

    return None
