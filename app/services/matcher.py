from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.models import Dipendente
from typing import Optional
from datetime import date

def find_employee_by_name(db: Session, raw_name: str, data_nascita: Optional[date] = None) -> Optional[Dipendente]:
    """
    Tenta di trovare un dipendente nel database basandosi su una stringa di nome grezzo.
    Cerca combinazioni Nome Cognome e Cognome Nome.
    Optimized: Uses a single query with OR conditions.

    Args:
        db: Sessione DB
        raw_name: Nome grezzo (es. "Mario Rossi")
        data_nascita: Opzionale. Usato per disambiguare omonimi.
    """
    if not raw_name or not raw_name.strip():
        return None

    nome_parts = raw_name.strip().split()
    if len(nome_parts) < 2:
        return None

    # Optimization: One query with multiple OR conditions
    conditions = []

    # Try all possible splits
    for i in range(1, len(nome_parts)):
        part1 = " ".join(nome_parts[:i])
        part2 = " ".join(nome_parts[i:])

        # Matches Nome=part1 AND Cognome=part2
        conditions.append(
            (Dipendente.nome.ilike(part1)) & (Dipendente.cognome.ilike(part2))
        )
        # Matches Nome=part2 AND Cognome=part1
        conditions.append(
            (Dipendente.nome.ilike(part2)) & (Dipendente.cognome.ilike(part1))
        )

    if not conditions:
        return None

    query = db.query(Dipendente).filter(or_(*conditions))
    matches = query.all()

    if not matches:
        return None

    found_employees = {emp.id: emp for emp in matches}

    # Se abbiamo una data di nascita, filtriamo
    if data_nascita:
        filtered_by_dob = [e for e in found_employees.values() if e.data_nascita == data_nascita]
        if len(filtered_by_dob) == 1:
            return filtered_by_dob[0]

        # Se filtrando per data non troviamo nessuno (o ancora troppi?), e avevamo > 1 candidati prima,
        # allora c'è ambiguità o mismatch.
        # Se filtrando per data ne troviamo 0, ma avevamo candidati per nome,
        # significa che il nome corrisponde ma la data no -> Probabilmente non è lui.
        if len(filtered_by_dob) == 0:
            # Nessuna corrispondenza esatta con nome E data
            return None

    # Se non abbiamo data di nascita, o se dopo il filtro ne rimangono > 1 (improbabile con data esatta),
    # controlliamo se ne avevamo trovato solo uno all'inizio.
    if len(found_employees) == 1:
        return list(found_employees.values())[0]

    # Troppi candidati e nessuna data per risolvere, oppure data non corrispondente
    return None
