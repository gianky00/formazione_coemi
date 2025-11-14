import google.generativeai as genai
import os
import logging
import json
from dotenv import load_dotenv

# Carica le variabili d'ambiente (per la API_KEY)
load_dotenv()

# Lista statica delle categorie
CATEGORIE_STATICHE = [
    "ANTINCENDIO E PRIMO SOCCORSO", "ASPP", "RSPP", "ATEX", "BLSD",
    "CARROPONTE", "DIRETTIVA SEVESO", "DIRIGENTI E FORMATORI",
    "GRU A TORRE E PONTE", "H2S", "IMBRACATORE",
    "AGGIORNAMENTO LAVORATORI ART.37", "PREPOSTO", "GRU SU AUTOCARRO",
    "PLE", "PES PAV PEI C CANTIERE", "LAVORI IN QUOTA",
    "MACCHINE OPERATRICI", "MANITOU P.ROTATIVE", "MEDICO COMPETENTE",
    "MULETTO CARRELISTI", "SOPRAVVIVENZA E SALVATAGGIO IN MARE",
    "SPAZI CONFINATI DPI III E AUTORESPIRATORI", "HLO", "ALTRO"
]

model = None
try:
    API_KEY = os.environ.get("GEMINI_API_KEY")
    if not API_KEY:
        logging.error("Errore di configurazione Gemini: GEMINI_API_KEY non trovata nel file .env")
    else:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('models/gemini-2.5-pro') # O il modello che preferisci
        logging.info("Modello Gemini Pro configurato con successo.")
except Exception as e:
    logging.error(f"Errore di configurazione Gemini: {e}")

def extract_entities_with_ai(text: str) -> dict:
    if model is None:
        return {"error": "Modello Gemini non inizializzato."}

    # Converti la lista di categorie in una stringa per il prompt
    categorie_str = ", ".join(f'"{c}"' for c in CATEGORIE_STATICHE)

    prompt = f"""
    Sei un assistente AI specializzato nell'analisi e nell'estrazione di dati da attestati di formazione sulla sicurezza sul lavoro.

    Analizza il seguente testo estratto da un certificato:
    ---
    {text}
    ---

    Estrai le seguenti quattro informazioni e restituisci ESCLUSIVAMENTE un oggetto JSON valido.

    1. "nome": Il nome completo del partecipante (es. "MARIO ROSSI").
    2. "corso": Il titolo esatto e completo del corso frequentato (es. "FORMAZIONE PER ADDETTI Al LAVORI IN QUOTA...").
    3. "data_rilascio": La data di emissione o di rilascio dell'attestato (formato DD-MM-AAAA).
    4. "categoria": Analizza il titolo del corso e classificalo in UNA SOLA delle seguenti categorie: {categorie_str}. Scegli la categoria più specifica e pertinente. Se nessuna corrisponde, usa "ALTRO".

    JSON:
    """

    try:
        logging.info("Interrogazione Gemini Pro in corso...")
        response = model.generate_content(prompt)

        # Pulisci ed estrai il JSON dalla risposta
        json_response_text = response.text.strip().replace("```json", "").replace("```", "")

        dati_estratti = json.loads(json_response_text)
        logging.info(f"Dati estratti dall'AI: {dati_estratti}")
        return dati_estratti

    except json.JSONDecodeError:
        logging.error(f"Errore: Gemini non ha restituito un JSON valido. Risposta: {response.text}")
        return {"error": "Risposta AI non valida (JSON)"}
    except Exception as e:
        logging.error(f"Errore durante la chiamata a Gemini: {e}")
        return {"error": str(e)}
