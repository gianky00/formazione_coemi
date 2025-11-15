import google.generativeai as genai
import logging
import json
from app.core.config import settings

# --- Configurazione Logger (Buona pratica) ---
# (Usa la tua configurazione esistente)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configurazione API Key (Usa la tua) ---
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

    # --- PROMPT RINFORZATO ---
    # Ho aggiunto istruzioni negative direttamente negli esempi
    # per forzare la distinzione.
    esempi_categorie = """
- ANTINCENDIO: "Addetto Antincendio Rischio Basso", "Corso Antincendio Rischio Medio"
- PRIMO SOCCORSO: "Addetto al Primo Soccorso Gruppo A", "Corso BLS"
- ASPP: "ASPP Modulo A"
- RSPP: "RSPP Modulo A", "RSPP - Datore di Lavoro"
- PREPOSTO: [USA QUESTA SOLO PER CORSI/ATTESTATI] "Corso per Preposti alla Sicurezza", "Aggiornamento Preposto".
- NOMINE: [USA QUESTA PER LETTERE DI INCARICO/ATTRIBUZIONE] "NOMINA CAPO CANTIERE", "NOMINA PREPOSTO", "Attribuzione e competenze del ruolo di Preposto"
- ALTRO: (qualsiasi altro documento non classificabile)
"""

    # --- PROMPT RINFORZATO ---
    # Ho reso la regola ancora più esplicita e ho aggiunto
    # una sezione "ERRORE COMUNE DA EVITARE".
    prompt_completo = f"""
Sei un assistente AI specializzato nell'analisi di documenti sulla sicurezza sul lavoro per l'azienda COEMI.
Analizza il certificato o documento PDF che ti fornisco.

Estrai le seguenti informazioni e classificalo. Restituisci ESCLUSIVAMENTE un oggetto JSON valido.

1.  "nome": Il nome completo del partecipante (es. "MARIO ROSSI" o "Giliberto Salvatore"). Se non è un attestato (es. una nomina), cerca il nome del destinatario. Se non c'è, restituisci null.
2.  "corso": Il titolo esatto e completo del corso. Se non è un corso (come una "NOMINA"), estrai il titolo del documento (es. "NOMINA CAPO CANTIERE" o "Attribuzione e competenze del ruolo di Preposto"). Se non c'è, restituisci null.
3.  "data_rilascio": La data di emissione o di rilascio del documento (formato DD-MM-AAAA). Se non c'è, restituisci null.
4.  "categoria": Classifica il documento in UNA SOLA delle seguenti categorie:
    {categorie_str}

    Usa questi esempi per guidarti. Presta MOLTA attenzione alla differenza tra PREPOSTO e NOMINE:
    {esempi_categorie}

    REGOLA DI CLASSIFICAZIONE ASSOLUTA:
    1. La categoria 'PREPOSTO' deve essere usata **SOLO ED ESCLUSIVAMENTE** per **attestati di FORMAZIONE** (es. "Corso di Aggiornamento per Preposto", "Corso di Formazione per Preposti").
    2. Qualsiasi documento che sia una **lettera di incarico**, un'**attribuzione di ruolo**, o una **nomina** (come "NOMINA CAPO CANTIERE", "Attribuzione... ruolo di Preposto", "COMUNICA la Sua designazione") deve essere classificato **SEMPRE e SOLO** come "NOMINE".

    ERRORE COMUNE DA EVITARE:
    NON classificare "NOMINA... Preposto" o "Attribuzione... Preposto" come "PREPOSTO". Quella è una "NOMINE".
    Un "Corso... Preposto" è "PREPOSTO".
    Una "Nomina... Preposto" è "NOMINE".

    Se non riesci a classificare, usa "ALTRO".

JSON:
"""
    # --- Fine modifiche prompt ---

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
