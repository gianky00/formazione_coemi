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

    lines = text.lower().split('\n')

    # 1. Estrarre il corso
    corsi = db.query(CorsiMaster).all()
    course_names = {corso.nome_corso.lower(): corso for corso in corsi}
    for line in lines:
        for course_name in course_names.keys():
            if course_name in line:
                entities["corso"] = course_names[course_name].nome_corso
                break
        if entities["corso"]:
            break

    # 2. Estrarre le date
    date_pattern = r'\d{2,4}[-/]\d{2}[-/]\d{2,4}'
    dates = re.findall(date_pattern, text)

    # Simple logic: assume the first date is the issue date
    if dates:
        try:
            # Handle different formats like YYYY-MM-DD or DD-MM-YYYY
            parsed_date = None
            if '-' in dates[0]:
                parts = dates[0].split('-')
                if len(parts[0]) == 4: # YYYY-MM-DD
                    parsed_date = datetime.strptime(dates[0], '%Y-%m-%d').date()
                else: # DD-MM-YYYY
                    parsed_date = datetime.strptime(dates[0], '%d-%m-%Y').date()
            elif '/' in dates[0]:
                parts = dates[0].split('/')
                if len(parts[0]) == 4: # YYYY/MM/DD
                    parsed_date = datetime.strptime(dates[0], '%Y/%m/%d').date()
                else: # DD/MM/YYYY
                    parsed_date = datetime.strptime(dates[0], '%d/%m/%Y').date()

            entities["data_rilascio"] = parsed_date
        except ValueError:
            pass # Date format not recognized

    # 3. Estrarre il nome
    for line in lines:
        if "name:" in line or "nome:" in line:
            entities["nome"] = line.split(":")[-1].strip().title()
            break

    # 4. Calcolare la data di scadenza
    if entities["corso"] and entities["data_rilascio"]:
        corso_obj = course_names[entities["corso"].lower()]
        if corso_obj and corso_obj.validita_mesi > 0:
            expiration_date = entities["data_rilascio"] + relativedelta(months=corso_obj.validita_mesi)
            entities["data_scadenza"] = expiration_date

    return entities
