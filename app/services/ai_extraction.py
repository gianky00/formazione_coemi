import google.generativeai as genai
import logging
import json
from app.core.config import settings
import google.generativeai as genai

# --- Configurazione API Key ---
model = None
try:
    if not settings.GEMINI_API_KEY:
        logging.error("Errore di configurazione Gemini: GEMINI_API_KEY non trovata.")
    else:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        logging.info("Modello Gemini 'models/gemini-2.5-pro' configurato con successo.")
except Exception as e:
    logging.error(f"Errore di configurazione Gemini: {e}")

# --- Elenco categorie ---
CATEGORIE_STATICHE = [
    "ANTINCENDIO E PRIMO SOCCORSO", "ASPP", "RSPP", "ATEX", "BLSD", "CARROPONTE",
    "DIRETTIVA SEVESO", "DIRIGENTI E FORMATORI", "GRU A TORRE E PONTE", "H2S",
    "IMBRACATORE", "AGGIORNAMENTO LAVORATORI ART.37", "PREPOSTO", "GRU SU AUTOCARRO",
    "PLE", "PES PAV PEI C CANTIERE", "LAVORI IN QUOTA", "MACCHINE OPERATRICI",
    "MANITOU P.ROTATIVE", "MEDICO COMPETENTE", "MULETTO CARRELISTI",
    "SOPRAVVIVENZA E SALVATAGGIO IN MARE", "SPAZI CONFINATI DPI III E AUTORESPIRATORI",
    "HLO", "ALTRO"
]

# --- NUOVA FUNZIONE PER PDF ---
def extract_entities_with_ai(pdf_bytes: bytes) -> dict:
    """
    Estrae entità da un file PDF (in bytes) usando un modello multimodale.
    """
    if model is None:
        return {"error": "Modello Gemini non inizializzato."}

    categorie_str = ", ".join(f'"{c}"' for c in CATEGORIE_STATICHE)

    # Questo prompt ora chiede a Gemini di analizzare il PDF.
    prompt = f"""
Sei un assistente AI specializzato nell'analisi di attestati di formazione.
Analizza il certificato in formato PDF che ti fornisco.

Estrai le seguenti quattro informazioni e restituisci ESCLUSIVAMENTE un oggetto JSON valido.

1. "nome": Il nome completo del partecipante (es. "MARIO ROSSI").
2. "corso": Il titolo esatto e completo del corso frequentato.
3. "data_rilascio": La data di emissione o di rilascio dell'attestato (formato DD-MM-AAAA).
4. "categoria": Analizza il titolo del corso e classificalo in UNA SOLA delle seguenti categorie: {categorie_str}. Scegli la categoria più specifica. Se nessuna corrisponde, usa "ALTRO".

JSON:
"""

    # Costruisci l'input multimodale: prima il PDF, poi il prompt
    pdf_file = {"mime_type": "application/pdf", "data": pdf_bytes}
    model_input = [pdf_file, prompt]

    try:
        logging.info("Interrogazione Gemini Pro (Multimodale con PDF) in corso...")

        # Invia la richiesta con PDF e testo
        response = model.generate_content(model_input)

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
