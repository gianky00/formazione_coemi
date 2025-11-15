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
    in UNA SOLA CHIAMATA.
    """
    if model is None:
        return {"error": "Modello Gemini non inizializzato."}

    categorie_str = ", ".join(f'"{c}"' for c in CATEGORIE_STATICHE)
    esempi_categorie = """
- ANTINCENDIO: "Addetto Antincendio Rischio Basso", "Corso Antincendio Rischio Medio"
- PRIMO SOCCORSO: "Addetto al Primo Soccorso Gruppo A", "Corso BLS"
- ASPP: "ASPP Modulo A"
- RSPP: "RSPP Modulo A", "RSPP - Datore di Lavoro"
- PREPOSTO: "Corso per Preposti alla Sicurezza"
- NOMINE: "NOMINA CAPO CANTIERE", "NOMINA PREPOSTO", "NOMINA RAPPRESENTANTE LEGALE"
- ALTRO: (qualsiasi altro documento non classificabile)
"""

    # --- Chiamata Unica: Estrazione e Classificazione ---
    prompt_completo = f"""
Sei un assistente AI specializzato nell'analisi di documenti sulla sicurezza sul lavoro.
Analizza il certificato o documento PDF che ti fornisco.

Estrai le seguenti informazioni e classificalo. Restituisci ESCLUSIVAMENTE un oggetto JSON valido.

1.  "nome": Il nome completo del partecipante (es. "MARIO ROSSI"  o "Giliberto Salvatore" [cite: 5, 46]). Se non è un attestato (es. una nomina), cerca il nome del destinatario.
2.  "corso": Il titolo esatto e completo del corso. Se non è un corso (come una "NOMINA"), estrai il titolo del documento (es. "NOMINA CAPO CANTIERE"  o "Attribuzione... ruolo di Preposto" ).
3.  "data_rilascio": La data di emissione o di rilascio del documento (formato DD-MM-AAAA [cite: 34, 62]).
4.  "categoria": Classifica il documento in UNA SOLA delle seguenti categorie, usando il contesto totale del PDF:
    {categorie_str}

    Usa questi esempi per guidarti:
    {esempi_categorie}

    Se il documento è una nomina  o un'attribuzione di ruolo, classificalo come "NOMINE".
    Se non riesci a classificare, usa "ALTRO".

JSON:
"""
    pdf_file_part = {"mime_type": "application/pdf", "data": pdf_bytes}

    try:
        logging.info("Chiamata AI Unica: Estrazione e Classificazione...")
        response = model.generate_content([pdf_file_part, prompt_completo])
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        dati_finali = json.loads(json_text)

        # Fallback se la categoria non è valida
        if "categoria" not in dati_finali or dati_finali["categoria"] not in CATEGORIE_STATICHE:
            logging.warning(f"Categoria non valida: {dati_finali.get('categoria')}. Imposto 'ALTRO'.")
            dati_finali["categoria"] = "ALTRO"

        logging.info(f"Dati finali estratti: {dati_finali}")
        return dati_finali

    except Exception as e:
        logging.error(f"Errore durante la chiamata AI unica: {e}")
        return {"error": f"Chiamata AI fallita: {e}", "categoria": "ALTRO"}
