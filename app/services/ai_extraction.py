import google.generativeai as genai
import os
import logging
import json
from dotenv import load_dotenv

# Carica le variabili d'ambiente (per la API_KEY)
load_dotenv()

model = None
try:
    API_KEY = os.environ.get("GEMINI_API_KEY")
    if not API_KEY:
        logging.error("Errore di configurazione Gemini: GEMINI_API_KEY non trovata nel file .env")
    else:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        logging.info("Modello Gemini Pro configurato con successo.")
except Exception as e:
    logging.error(f"Errore di configurazione Gemini: {e}")

def extract_entities_with_ai(text: str) -> dict:
    if model is None:
        return {"error": "Modello Gemini non inizializzato."}

    prompt = f"""
    Sei un assistente AI specializzato nell'estrazione di dati da attestati di formazione.

    **ISTRUZIONI CRITICHE:**
    1.  **Restituisci solo un oggetto JSON valido.** Non includere testo, spiegazioni o commenti aggiuntivi.
    2.  **Il campo "nome" è FONDAMENTALE.** Deve obbligatoriamente contenere sia il nome che il cognome. Se trovi un solo nome, cerca attentamente nel testo per trovare la parte mancante. Il valore di "nome" DEVE contenere almeno due parole.
    3.  Estrai le informazioni richieste con la massima precisione.

    **ESEMPIO:**
    Testo di input:
    ---
    Si certifica che AGATI GAETANO nato a Siracusa ha superato con successo il corso di FORMAZIONE PREPOSTO tenutosi in data 20-09-2022.
    ---
    JSON di output atteso:
    ```json
    {{"nome": "AGATI GAETANO", "corso": "FORMAZIONE PREPOSTO", "data_rilascio": "20-09-2022"}}
    ```

    **IL TUO COMPITO:**
    Analizza il seguente testo e genera l'oggetto JSON corrispondente.

    Testo di input:
    ---
    {text}
    ---

    JSON di output:
    """

    try:
        logging.info("Interrogazione Gemini Pro in corso con prompt migliorato...")
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
