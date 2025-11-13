import logging
import re
from transformers import pipeline
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from app.db.models import CorsiMaster

logging.basicConfig(level=logging.INFO)

# Carica il modello QA una sola volta
qa_pipeline = pipeline(
    "question-answering",
    model="antoniocappiello/bert-base-italian-uncased-squad-it",
    tokenizer="antoniocappiello/bert-base-italian-uncased-squad-it"
)

def extract_entities_with_ai(text: str, db: Session) -> dict:
    """
    Estrae entità dal testo OCR utilizzando un modello di Question Answering (QA).
    """
    entities = {
        "dipendente": None,
        "corso": None,
        "data_rilascio": None,
        "data_scadenza": None,
    }

    # Pre-processa il testo per rimuovere i titoli che confondono il modello
    processed_text = re.sub(r'il Sig\.|la Sig\.ra|Sig\.|Sig\.ra', '', text, flags=re.IGNORECASE)

    # 1. Estrazione con QA
    questions = {
        "dipendente": "Chi ha frequentato il corso?",
        "corso": "Qual è il nome del corso?",
        "data_rilascio": "Qual è la data di rilascio dell'attestato?"
    }

    for key, question in questions.items():
        result = qa_pipeline(question=question, context=processed_text)
        answer = result['answer'].strip()

        # Post-processing for corso
        if key == "corso":
            answer = re.sub(r'^\s*corso di\s*', '', answer, flags=re.IGNORECASE).strip()

        entities[key] = answer

    # 2. Conversione della data e calcolo della scadenza
    if entities["data_rilascio"]:
        try:
            # Prova a parsare formati comuni
            parsed_date = None
            date_str = entities["data_rilascio"]
            if '-' in date_str:
                parts = date_str.split('-')
                if len(parts[0]) == 4: # YYYY-MM-DD
                    parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                else: # DD-MM-YYYY
                    parsed_date = datetime.strptime(date_str, '%d-%m-%Y').date()
            elif '/' in date_str:
                parts = date_str.split('/')
                if len(parts[0]) == 4: # YYYY/MM/DD
                    parsed_date = datetime.strptime(date_str, '%Y/%m/%d').date()
                else: # DD/MM/YYYY
                    parsed_date = datetime.strptime(date_str, '%d/%m/%Y').date()

            entities["data_rilascio"] = parsed_date
        except ValueError:
            entities["data_rilascio"] = None # Non è stato possibile parsare la data

    # 3. Logica di Business (Calcolo Scadenza)
    if entities["corso"] and entities["data_rilascio"]:
        corsi = db.query(CorsiMaster).all()
        course_names = {corso.nome_corso.lower(): corso for corso in corsi}

        extracted_course_lower = entities["corso"].lower()

        for course_name, corso_obj in course_names.items():
            if course_name in extracted_course_lower:
                if corso_obj.validita_mesi > 0:
                    expiration_date = entities["data_rilascio"] + relativedelta(months=corso_obj.validita_mesi)
                    entities["data_scadenza"] = expiration_date
                break

    return entities
