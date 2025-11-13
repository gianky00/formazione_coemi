import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from app.db.models import CorsiMaster

def extract_entities(text: str, db: Session) -> dict:
    """
    Extracts entities from OCR text using a rule-based engine.
    """
    entities = {
        "nome": None,
        "corso": None,
        "data_rilascio": None,
        "data_scadenza": None,
    }

    lines = text.split('\n')

    # 1. Estrarre il nome del dipendente
    for i, line in enumerate(lines):
        if "Si certifica che" in line:
            # Il nome potrebbe essere sulla stessa riga o su quella successiva
            try:
                name_line = line.split("Si certifica che")[1].strip()
                if name_line:
                    entities["nome"] = name_line
                elif i + 1 < len(lines):
                    entities["nome"] = lines[i+1].strip()
            except IndexError:
                if i + 1 < len(lines):
                    entities["nome"] = lines[i+1].strip()
            break

    # 2. Estrarre il nome del corso
    for i, line in enumerate(lines):
        if "ATTESTATO" in line and i + 1 < len(lines):
            # Il nome del corso e' sulla riga successiva
            if "FORMAZIONE PREPOSTO" in lines[i+1]:
                entities["corso"] = "FORMAZIONE PREPOSTO"
                break

    # 3. Estrarre la data di emissione
    date_pattern = r'nei giorni (\d{2}-\d{2}-\d{4})'
    match = re.search(date_pattern, text)
    if match:
        try:
            parsed_date = datetime.strptime(match.group(1), '%d-%m-%Y').date()
            entities["data_rilascio"] = parsed_date
        except ValueError:
            pass  # Formato data non riconosciuto

    # 4. Calcolare la data di scadenza
    if entities["data_rilascio"]:
        # Per i preposti, la scadenza e' di 2 anni
        expiration_date = entities["data_rilascio"] + relativedelta(years=2)
        entities["data_scadenza"] = expiration_date

    return entities
