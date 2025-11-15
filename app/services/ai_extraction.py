import google.generativeai as genai
import logging
import json
from app.core.config import settings

# --- Configurazione Logger (Buona pratica) ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configurazione API Key ---
model = None
try:
    if not settings.GEMINI_API_KEY:
        logging.error("Errore di configurazione Gemini: GEMINI_API_KEY non trovata.")
        logging.info("Assicurati di averla impostata nelle variabili d'ambiente o in app.core.config.settings")
    else:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        logging.info("Modello Gemini 'models/gemini-2.5-pro' configurato con successo.")
except Exception as e:
    logging.error(f"Errore di configurazione Gemini: {e}")

# --- Elenco categorie ---
CATEGORIE_STATICHE = [
    "ANTINCENDIO", "PRIMO SOCCORSO", "ASPP", "RSPP", "ATEX", "BLSD", "CARROPONTE",
    "DIRETTIVA SEVESO", "DIRIGENTI E FORMATORI", "GRU A TORRE E PONTE", "H2S",
    "IMBRACATORE", "FORMAZIONE GENERICA ART.37", "PREPOSTO", "GRU SU AUTOCARRO",
    "PLE", "PES PAV PEI C CANTIERE", "LAVORI IN QUOTA", "MACCHINE OPERATRICI",
    "MANITOU P.ROTATIVE", "MEDICO COMPETENTE", "MULETTO CARRELISTI", "NOMINE",
    "SOPRAVVIVENZA E SALVATAGGIO IN MARE", "SPAZI CONFINATI DPI III E AUTORESPIRATORI",
    "HLO", "ALTRO"
]

def extract_entities_with_ai(pdf_bytes: bytes) -> dict:
    """
    Estrae entità da un file PDF in bytes utilizzando un modello multimodale
    in UNA SOLA CHIAMATA, con logica avanzata per distinguere corsi e nomine.
    """
    if model is None:
        logging.error("Il modello Gemini non è inizializzato. Impossibile procedere.")
        return {"error": "Modello Gemini non inizializzato."}

    categorie_str = ", ".join(f'"{c}"' for c in CATEGORIE_STATICHE)

    esempi_categorie = """
- ANTINCENDIO: "Addetto Antincendio Rischio Basso", "Corso Antincendio Rischio Medio"
- PRIMO SOCCORSO: "Addetto al Primo Soccorso Gruppo A", "Corso BLS"
- ASPP: "ASPP Modulo A"
- RSPP: "RSPP Modulo A", "RSPP - Datore di Lavoro"
- PREPOSTO: "Corso per Preposti alla Sicurezza", "Aggiornamento Preposto"
- NOMINE: "NOMINA CAPO CANTIERE", "NOMINA PREPOSTO", "NOMINA RAPPRESENTANTE LEGALE", "Attribuzione e competenze del ruolo di Preposto"
- ALTRO: (qualsiasi altro documento non classificabile)
"""

    # --- Chiamata Unica: Estrazione e Classificazione ---

    prompt_completo = f"""
Sei un assistente AI specializzato nell'analisi di documenti sulla sicurezza sul lavoro per l'azienda COEMI.
Analizza il certificato o documento PDF che ti fornisco.

Estrai le seguenti informazioni e classificalo. Restituisci ESCLUSIVAMENTE un oggetto JSON valido.

1.  "nome": Il nome completo del partecipante (es. "MARIO ROSSI" o "Giliberto Salvatore"). Se non è un attestato (es. una nomina), cerca il nome del destinatario. Se non c'è, restituisci null.
2.  "corso": Il titolo esatto e completo del corso. Se non è un corso (come una "NOMINA"), estrai il titolo del documento (es. "NOMINA CAPO CANTIERE" o "Attribuzione e competenze del ruolo di Preposto"). Se non c'è, restituisci null.
3.  "data_rilascio": La data di emissione o di rilascio del documento (formato DD-MM-AAAA). Se non c'è, restituisci null.
4.  "categoria": Classifica il documento in UNA SOLA delle seguenti categorie, usando il contesto totale del PDF:
    {categorie_str}

    Usa questi esempi per guidarti:
    {esempi_categorie}

    REGOLA FONDAMENTALE PER LA CLASSIFICAZIONE:
    - Se il documento è un **corso** o un **attestato di formazione** (es. "Corso di Aggiornamento per Preposto"), la categoria è quella del corso (es. "PREPOSTO").
    - Se il documento è una **nomina**, una **lettera di incarico** o un'**attribuzione di ruolo** (es. "NOMINA CAPO CANTIERE", "Attribuzione... ruolo di Preposto", "COMUNICA la Sua designazione... quale PREPOSTO"), la categoria deve essere **SEMPRE** "NOMINE", anche se il ruolo menzionato è "Preposto".

    Se non riesci a classificare, usa "ALTRO".

JSON:
"""
    pdf_file_part = {"mime_type": "application/pdf", "data": pdf_bytes}

    try:
        logging.info("Chiamata AI Unica: Estrazione e Classificazione...")
        response = model.generate_content([pdf_file_part, prompt_completo])

        # Pulizia robusta del JSON in risposta
        json_text = response.text.strip()
        if json_text.startswith("```json"):
            json_text = json_text[7:]
        if json_text.endswith("```"):
            json_text = json_text[:-3]

        json_text = json_text.strip()

        dati_finali = json.loads(json_text)

        # Assicurati che le chiavi principali esistano con 'null' se assenti
        dati_finali.setdefault("nome", None)
        dati_finali.setdefault("corso", None)
        dati_finali.setdefault("data_rilascio", None)

        # Fallback se la categoria non è valida o assente
        if "categoria" not in dati_finali or dati_finali["categoria"] not in CATEGORIE_STATICHE:
            logging.warning(f"Categoria non valida o assente: {dati_finali.get('categoria')}. Imposto 'ALTRO'.")
            dati_finali["categoria"] = "ALTRO"

        logging.info(f"Dati finali estratti: {dati_finali}")
        return dati_finali

    except json.JSONDecodeError as e:
        logging.error(f"Errore durante il parsing del JSON: {e}. Risposta AI: {response.text}")
        return {"error": f"JSON non valido dalla AI: {e}", "categoria": "ALTRO", "nome": None, "corso": None, "data_rilascio": None}
    except Exception as e:
        logging.error(f"Errore durante la chiamata AI unica: {e}")
        return {"error": f"Chiamata AI fallita: {e}", "categoria": "ALTRO", "nome": None, "corso": None, "data_rilascio": None}
