import logging
from transformers import pipeline
from sqlalchemy.orm import Session
from app.db.models import CorsiMaster

logging.basicConfig(level=logging.INFO)

# Use a pipeline as a high-level helper
logging.info("Loading question-answering model...")
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
logging.info("Model loaded successfully.")

def extract_entities_with_ai(text: str, db: Session) -> dict:
    """
    Extracts entities from OCR text using an AI model.
    """
    results = {}

    # 1. Extract Name
    question = "Qual è il nome del partecipante?"
    results["nome"] = qa_pipeline(question=question, context=text)

    # 2. Extract Course
    question = "Qual è il nome del corso?"
    results["corso"] = qa_pipeline(question=question, context=text)

    # 3. Extract Issue Date
    question = "Qual è la data di rilascio?"
    results["data_rilascio"] = qa_pipeline(question=question, context=text)

    # 4. Extract Expiration Date
    question = "Qual è la data di scadenza?"
    results["data_scadenza"] = qa_pipeline(question=question, context=text)

    return results
