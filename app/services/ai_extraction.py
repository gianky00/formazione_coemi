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
    "PLE", "PES PAV PEI C CANTIERE", "LAVORI IN QUOTA", "MACCHINE OPERATrici",
    "MANITOU P.ROTATIVE", "MEDICO COMPETENTE", "MULETTO CARRELISTI", "NOMINE", "VISITA MEDICA",
    "SOPRAVVIVENZA E SALVATAGGIO IN MARE", "SPAZI CONFINATI DPI III E AUTORESPIRATORI",
    "HLO", "ALTRO"
]

def extract_entities_with_ai(pdf_bytes: bytes) -> dict:
    """
    Estrae entità da un file PDF in bytes utilizzando un modello multimodale
    in UNA SOLA CHIAMATA, con logica avanzata per distinguere corsi, nomine e visite mediche.
    """
    if model is None:
        logging.error("Il modello Gemini non è inizializzato. Impossibile procedere.")
        return {"error": "Modello Gemini non inizializzato."}

    categorie_str = ", ".join(f'"{c}"' for c in CATEGORIE_STATICHE)

    esempi_categorie = """
- ANTINCENDIO: "Addetto Antincendio Rischio Basso", "Corso Antincendio Rischio Medio"
- PREPOSTO: [USA QUESTA SOLO PER CORSI/ATTESTATI] "Corso per Preposti alla Sicurezza", "Aggiornamento Preposto".
- NOMINE: [USA QUESTA PER LETTERE DI INCARICO/ATTRIBUZIONE] "NOMINA CAPO CANTIERE", "NOMINA PREPOSTO", "Attribuzione e competenze del ruolo di Preposto"
- VISITA MEDICA: [USA QUESTA PER GIUDIZI DI IDONEITÀ] "Giudizio di idoneità alla Mansione Specifica", "Visita medica periodica"
- ALTRO: (qualsiasi altro documento non classificabile)
"""

    prompt_completo = f"""
Sei un assistente AI specializzato nell'analisi di documenti sulla sicurezza sul lavoro per l'azienda COEMI.
Analizza il certificato o documento PDF che ti fornisco.

Estrai le seguenti informazioni e classificalo. Restituisci ESCLUSIVAMENTE un oggetto JSON valido.

1.  "nome": Il nome completo del partecipante (es. "MARIO ROSSI"). Se non c'è, restituisci null.
2.  "corso": Il titolo esatto del corso o del documento (es. "NOMINA CAPO CANTIERE", "Giudizio di idoneità alla Mansione Specifica"). Se non c'è, restituisci null.
3.  "data_rilascio": La data di emissione del documento (formato DD-MM-AAAA). Se non c'è, restituisci null.
4.  "data_scadenza": La data di scadenza o la data entro cui il documento deve essere rivisto (formato DD-MM-AAAA). Cerca frasi come "Da rivedere entro il...". Se non trovi una data di scadenza esplicita, restituisci null.
5.  "categoria": Classifica il documento in UNA SOLA delle seguenti categorie:
    {categorie_str}

    Usa questi esempi per guidarti. Presta MOLTA attenzione alle differenze:
    {esempi_categorie}

    REGOLE DI CLASSIFICAZIONE ASSOLUTE:
    1.  'PREPOSTO' deve essere usata **SOLO** per **attestati di FORMAZIONE**.
    2.  Qualsiasi **lettera di incarico** o **nomina** (es. "NOMINA CAPO CANTIERE", "Attribuzione... ruolo di Preposto") deve essere **SEMPRE** "NOMINE".
    3.  Qualsiasi documento che sia un **"Giudizio di idoneità alla Mansione Specifica"**, emesso da un "Medico Competente" e che contenga frasi come "Visita medica del...", "accertamenti sanitari" e una scadenza (es. "Da rivedere entro il..."), deve essere **SEMPRE** "VISITA MEDICA".

    ERRORE COMUNE DA EVITARE:
    - NON classificare "NOMINA... Preposto" come "PREPOSTO". Quella è una "NOMINE".
    - NON classificare un "Giudizio di idoneità" in base alla mansione. La categoria è "VISITA MEDICA".

    Se non riesci a classificare, usa "ALTRO".

JSON:
"""
    pdf_file_part = {"mime_type": "application/pdf", "data": pdf_bytes}

    try:
        logging.info("Chiamata AI Unica: Estrazione e Classificazione...")
        response = model.generate_content([pdf_file_part, prompt_completo])

        json_text = response.text.strip().replace("```json", "").replace("```", "")

        dati_finali = json.loads(json_text)

        dati_finali.setdefault("nome", None)
        dati_finali.setdefault("corso", None)
        dati_finali.setdefault("data_rilascio", None)
        dati_finali.setdefault("data_scadenza", None)

        if "categoria" not in dati_finali or dati_finali["categoria"] not in CATEGORIE_STATICHE:
            logging.warning(f"Categoria non valida o assente: {dati_finali.get('categoria')}. Imposto 'ALTRO'.")
            dati_finali["categoria"] = "ALTRO"

        logging.info(f"Dati finali estratti: {dati_finali}")
        return dati_finali

    except json.JSONDecodeError as e:
        logging.error(f"Errore durante il parsing del JSON: {e}. Risposta AI: {response.text}")
        return {"error": f"JSON non valido dalla AI: {e}", "categoria": "ALTRO", "nome": None, "corso": None, "data_rilascio": None, "data_scadenza": None}
    except Exception as e:
        logging.error(f"Errore durante la chiamata AI unica: {e}")
        return {"error": f"Chiamata AI fallita: {e}", "categoria": "ALTRO", "nome": None, "corso": None, "data_rilascio": None, "data_scadenza": None}
