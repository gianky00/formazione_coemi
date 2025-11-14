import google.generativeai as genai
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Configura il percorso per trovare il file .env
PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / '.env'

# Carica il file .env
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    logging.info(f"File .env caricato da: {ENV_PATH}")
else:
    print(f"ATTENZIONE: File .env non trovato. {ENV_PATH}")

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("ERRORE: GEMINI_API_KEY non trovata nel file .env")
else:
    try:
        genai.configure(api_key=API_KEY)
        
        print("--- Modelli disponibili per 'generateContent' ---")
        for m in genai.list_models():
             if 'generateContent' in m.supported_generation_methods:
                 print(m.name)
                 
    except Exception as e:
        print(f"Errore durante la connessione a Google: {e}")