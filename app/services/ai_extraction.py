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
    "IMBRACATORE", "FORMAZIONE GENERICA ART.37", "PREPOSTO", "GRU SU AUTOCARRO",
    "PLE", "PES PAV PEI C CANTIERE", "LAVORI IN QUOTA", "MACCHINE OPERATRICI",
    "MANITOU P.ROTATIVE", "MEDICO COMPETENTE", "MULETTO CARRELISTI",
    "SOPRAVVIVENZA E SALVATAGGIO IN MARE", "SPAZI CONFINATI DPI III E AUTORESPIRATORI",
    "HLO"
]

# --- NUOVA FUNZIONE PER PDF ---
def extract_entities_with_ai(pdf_bytes: bytes) -> dict:
    """
    Estrae entità da un file PDF (in bytes) usando un modello multimodale in due passaggi.
    """
    if model is None:
        return {"error": "Modello Gemini non inizializzato."}

    # --- 1. Prima Chiamata: Estrazione Dati Base ---
    prompt_estrazione = """
Sei un assistente AI specializzato nell'analisi di attestati di formazione.
Analizza il certificato in formato PDF che ti fornisco.

Estrai le seguenti tre informazioni e restituisci ESCLUSIVAMENTE un oggetto JSON valido.

1. "nome": Il nome completo del partecipante (es. "MARIO ROSSI").
2. "corso": Il titolo esatto e completo del corso frequentato.
3. "data_rilascio": La data di emissione o di rilascio dell'attestato (formato DD-MM-AAAA).

JSON:
"""
    pdf_file_part = {"mime_type": "application/pdf", "data": pdf_bytes}

    try:
        logging.info("Prima chiamata AI: Estrazione dati...")
        response_estrazione = model.generate_content([pdf_file_part, prompt_estrazione])
        json_estrazione_text = response_estrazione.text.strip().replace("```json", "").replace("```", "")
        dati_base = json.loads(json_estrazione_text)
        logging.info(f"Dati base estratti: {dati_base}")
    except Exception as e:
        logging.error(f"Errore durante la prima chiamata AI: {e}")
        return {"error": f"Prima chiamata AI fallita: {e}"}

    # --- 2. Seconda Chiamata: Classificazione Categoria ---
    corso_estratto = dati_base.get("corso")
    if not corso_estratto:
        return {"error": "Il nome del corso non è stato estratto, impossibile classificare."}

    categorie_str = ", ".join(f'"{c}"' for c in CATEGORIE_STATICHE)
    prompt_classificazione = f"""
Sei un assistente AI esperto in sicurezza sul lavoro.
Il documento PDF è un attestato di formazione per il corso: "{corso_estratto}".

Analizza il titolo del corso e il contesto del PDF per classificarlo in UNA SOLA delle seguenti categorie predefinite:
{categorie_str}

Restituisci ESCLUSIVAMENTE un oggetto JSON con una singola chiave "categoria".

JSON:
"""
    try:
        logging.info(f"Seconda chiamata AI: Classificazione del corso '{corso_estratto}'...")
        response_classificazione = model.generate_content([pdf_file_part, prompt_classificazione])
        json_classificazione_text = response_classificazione.text.strip().replace("```json", "").replace("```", "")
        categoria_data = json.loads(json_classificazione_text)
        logging.info(f"Categoria classificata: {categoria_data}")
    except Exception as e:
        logging.error(f"Errore durante la seconda chiamata AI: {e}")
        return {"error": f"Seconda chiamata AI fallita: {e}"}

    # --- 3. Unisci i Risultati ---
    dati_finali = {**dati_base, **categoria_data}
    logging.info(f"Dati finali combinati: {dati_finali}")

    return dati_finali
