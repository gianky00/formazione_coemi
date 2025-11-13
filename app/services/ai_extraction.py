import logging
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)

def extract_entities_with_ai(text: str, db: Session) -> dict:
    """
    Extracts entities from OCR text using a rule-based engine.
    This function is a fallback to a rule-based system to avoid heavy dependencies.
    """
    entities = {
        "dipendente": None,
        "corso": None,
        "data_rilascio": None,
        "data_scadenza": None,
    }

    # 1. Document Classification (Implicit)
    is_certificate = "ATTESTATO" in text and "Si certifica che" in text

    if not is_certificate:
        return entities

    lines = text.split('\n')

    # 2. Riconoscimento di Entità (NER) - Rule-based
    # PERSONA (Dipendente)
    for i, line in enumerate(lines):
        if "Si certifica che" in line:
            try:
                name_line = line.split("Si certifica che")[1].strip()
                if name_line:
                    entities["dipendente"] = name_line
                elif i + 1 < len(lines):
                    entities["dipendente"] = lines[i+1].strip()
            except IndexError:
                if i + 1 < len(lines):
                    entities["dipendente"] = lines[i+1].strip()
            break

    # TITOLO_CORSO (Corso)
    for i, line in enumerate(lines):
        if "ATTESTATO" in line and i + 1 < len(lines):
            if "FORMAZIONE PREPOSTO" in lines[i+1]:
                entities["corso"] = "FORMAZIONE PREPOSTO"
                break

    # DATA_EMISSIONE (Data Rilascio)
    date_pattern = r'nei giorni (\d{2}-\d{2}-\d{4})'
    match = re.search(date_pattern, text)
    if match:
        try:
            parsed_date = datetime.strptime(match.group(1), '%d-%m-%Y').date()
            entities["data_rilascio"] = parsed_date
        except ValueError:
            pass

    # 3. Logica di Business
    if entities["data_rilascio"] and entities["corso"] and "PREPOSTO" in entities["corso"].upper():
        entities["data_scadenza"] = entities["data_rilascio"] + relativedelta(years=2)

    return entities
