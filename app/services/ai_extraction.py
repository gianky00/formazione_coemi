import os
import json
import logging
import re
import google.generativeai as genai
from dotenv import load_dotenv
from app.db.session import SessionLocal
from app.db.models import CorsiMaster

# Carica le variabili d'ambiente dal file .env
load_dotenv()

logging.basicConfig(level=logging.INFO)

# Configura l'API di Gemini
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY non trovata nel file .env")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-pro')
    logging.info("Modello Gemini Pro configurato con successo.")
except Exception as e:
    logging.error(f"Errore di configurazione Gemini: {e}")
    model = None

_master_courses_cache = None

def get_master_courses_list():
    """
    Recupera la lista dei corsi master dal database e la mette in cache.
    """
    global _master_courses_cache
    if _master_courses_cache is None:
        db = SessionLocal()
        try:
            corsi = db.query(CorsiMaster.nome_corso).all()
            _master_courses_cache = [corso[0] for corso in corsi]
        finally:
            db.close()
    return _master_courses_cache

def build_prompt(text: str) -> str:
    """
    Costruisce il prompt per l'API di Gemini.
    """
    master_courses = get_master_courses_list()

    return f"""
Sei un assistente AI specializzato nell'analisi e nell'estrazione di dati da attestati di formazione sulla sicurezza sul lavoro.

Il tuo compito è estrarre le informazioni richieste e CLASSIFICARE il corso frequentato in una delle seguenti categorie master.

Lista dei Corsi Master:
---
{", ".join(master_courses)}
---

Analizza il seguente testo estratto da un certificato:
---
{text}
---

Estrai le seguenti informazioni e restituisci ESCLUSIVAMENTE un oggetto JSON valido.

- "nome": Il nome completo del partecipante.
- "corso": Il titolo esatto del corso frequentato, come appare nel testo.
- "data_rilascio": La data di emissione o di rilascio dell'attestato (formato DD-MM-YYYY).
- "corso_master": La categoria dalla "Lista dei Corsi Master" che meglio corrisponde al corso frequentato.

Se un campo non è presente, il suo valore deve essere null.

JSON:
"""

def extract_entities_with_ai(text: str) -> dict:
    """
    Estrae entità dal testo OCR utilizzando l'API di Gemini Pro.
    """
    if not model:
        return {"error": "Modello Gemini non configurato."}

    prompt = build_prompt(text)

    try:
        logging.info("Interrogazione Gemini Pro in corso...")
        response = model.generate_content(prompt)

        # Pulisci ed estrai il JSON dalla risposta
        # Gemini potrebbe aggiungere ```json ... ``` alla risposta, puliamolo.
        json_response_text = response.text.strip()

        # Usa un'espressione regolare per trovare il JSON nel testo
        match = re.search(r'\{.*\}', json_response_text, re.DOTALL)
        if not match:
            logging.error(f"Nessun JSON valido trovato nella risposta di Gemini: {response.text}")
            return {"error": "Risposta non valida da Gemini."}

        json_response_text = match.group(0)

        # Converti la stringa JSON in un dizionario Python
        dati_estratti = json.loads(json_response_text)

        logging.info(f"Dati estratti dall'AI: {dati_estratti}")
        return dati_estratti

    except json.JSONDecodeError:
        logging.error(f"Errore: Gemini non ha restituito un JSON valido.")
        logging.error(f"Risposta ricevuta: {response.text}")
        return {"error": "JSON non valido da Gemini."}
    except Exception as e:
        logging.error(f"Errore durante la chiamata a Gemini: {e}")
        return {"error": f"Errore API Gemini: {e}"}
