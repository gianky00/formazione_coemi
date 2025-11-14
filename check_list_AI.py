import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carica il file .env per prendere la chiave
load_dotenv() 
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("Chiave API non trovata nel file .env")
else:
    genai.configure(api_key=API_KEY)
    
    print("--- Modelli disponibili che supportano 'generateContent' ---")
    try:
        for m in genai.list_models():
             if 'generateContent' in m.supported_generation_methods:
                 print(m.name)
    except Exception as e:
        print(f"Errore durante il recupero dei modelli: {e}")