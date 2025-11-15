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

# --- NUOVA FUNZIONE PER PDF ---
def extract_entities_with_ai(pdf_bytes: bytes) -> dict:
    """
    Estrae entità da un file PDF in bytes utilizzando un modello multimodale.

    Il processo avviene in due fasi:
    1. Estrazione delle informazioni di base (nome, corso, data di rilascio).
    2. Classificazione del corso estratto in una delle categorie predefinite.

    Args:
        pdf_bytes: I bytes del file PDF da analizzare.

    Returns:
        Un dizionario contenente le entità estratte, inclusa la categoria.
        In caso di errore, restituisce un dizionario con una chiave 'error'.
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
        logging.warning("Il nome del corso non è stato estratto. Salto la classificazione e imposto 'ALTRO'.")
        categoria_data = {"categoria": "ALTRO"}
    else:
        categorie_str = ", ".join(f'"{c}"' for c in CATEGORIE_STATICHE)
        esempi_categorie = """
- ANTINCENDIO: "Addetto Antincendio Rischio Basso", "Corso Antincendio Rischio Medio", "Aggiornamento Addetto Antincendio"
- PRIMO SOCCORSO: "Addetto al Primo Soccorso Gruppo A", "Corso Primo Soccorso Gruppo B/C", "Corso BLS (Basic Life Support)"
- ASPP: "ASPP Modulo A", "ASPP Modulo B", "Aggiornamento ASPP"
- RSPP: "RSPP Modulo A", "RSPP Modulo B", "RSPP - Datore di Lavoro"
- ATEX: "Corso ATEX Atmosfere Esplosive", "Formazione Lavori in Ambienti ATEX"
- BLSD: "Corso BLSD (Basic Life Support Defibrillation)", "Uso del Defibrillatore Semiautomatico"
- CARROPONTE: "Addetto alla Conduzione di Carroponte", "Corso Gruista Carroponte"
- DIRETTIVA SEVESO: "Formazione Direttiva Seveso III", "Gestione Stabilimenti a Rischio di Incidente Rilevante"
- DIRIGENTI E FORMATORI: "Corso per Dirigenti per la Sicurezza", "Corso Formatori per la Sicurezza"
- GRU A TORRE E PONTE: "Addetto alla Conduzione di Gru a Torre", "Corso Gruista Gru a Torre"
- H2S: "Corso H2S - Idrogeno Solforato", "Formazione Rischio H2S"
- IMBRACATORE: "Corso Imbracatore di Carichi", "Addetto all'Imbracatura"
- FORMAZIONE GENERICA ART.37: "Formazione Generale Lavoratori Art. 37", "Corso Sicurezza Generale 4 ore"
- PREPOSTO: "Corso per Preposti alla Sicurezza", "Formazione Preposto Art. 37"
- GRU SU AUTOCARRO: "Addetto alla Conduzione di Gru su Autocarro", "Corso Gruista Autocarro"
- PLE: "Addetto alla Conduzione di PLE", "Corso Piattaforme di Lavoro Elevabili"
- PES PAV PEI C CANTIERE: "Corso PES PAV - Lavori Elettrici", "Formazione Rischio Elettrico CEI 11-27"
- LAVORI IN QUOTA: "Corso Lavori in Quota con DPI Anticaduta", "Utilizzo Sistemi di Protezione Anticaduta"
- MACCHINE OPERATRICI: "Addetto alla Conduzione di Macchine Operatrici", "Corso Escavatori Idraulici"
- MANITOU P.ROTATIVE: "Addetto alla Conduzione di Sollevatori Telescopici Rotativi", "Corso Manitou"
- MEDICO COMPETENTE: "Corso di Formazione per Medico Competente", "Aggiornamento Medico Competente"
- MULETTO CARRELISTI: "Addetto alla Conduzione di Carrelli Elevatori", "Patentino Muletto"
- NOMINE: "NOMINA CAPO CANTIERE", "NOMINA RAPPRESENTANTE LEGALE"
- SOPRAVVIVENZA E SALVATAGGIO IN MARE: "Corso STCW Basic Safety Training", "Sopravvivenza in Mare"
- SPAZI CONFINATI DPI III E AUTORESPIRATORI: "Corso Lavori in Spazi Confinati", "DPI III Categoria e Autorespiratori"
- HLO: "Corso HLO - Helicopter Landing Officer", "Responsabile Operazioni Eliporto"
"""

        prompt_classificazione = f"""
Sei un assistente AI esperto in sicurezza sul lavoro.
Il documento PDF è un attestato di formazione per il corso: "{corso_estratto}".

Analizza il titolo del corso e il contesto del PDF per classificarlo in UNA SOLA delle seguenti categorie predefinite:
{categorie_str}

Ecco alcuni esempi di titoli per ogni categoria per aiutarti:
{esempi_categorie}

Se nessuna categoria corrisponde, assegna "ALTRO".

Restituisci ESCLUSIVAMENTE un oggetto JSON con una singola chiave "categoria".

JSON:
"""
        try:
            logging.info(f"Seconda chiamata AI: Classificazione del corso '{corso_estratto}'...")
            response_classificazione = model.generate_content([pdf_file_part, prompt_classificazione])
            json_classificazione_text = response_classificazione.text.strip().replace("```json", "").replace("```", "")
            categoria_data = json.loads(json_classificazione_text)

            # Fallback se la categoria non è valida o non presente
            if "categoria" not in categoria_data or categoria_data["categoria"] not in CATEGORIE_STATICHE:
                logging.warning(f"Categoria non valida o assente: {categoria_data.get('categoria')}. Imposto 'ALTRO'.")
                categoria_data["categoria"] = "ALTRO"

            logging.info(f"Categoria classificata: {categoria_data}")
        except Exception as e:
            logging.error(f"Errore durante la seconda chiamata AI: {e}. Imposto 'ALTRO'.")
            categoria_data = {"categoria": "ALTRO"}

    # --- 3. Unisci i Risultati ---
    dati_finali = {
        "nome": dati_base.get("nome"),
        "corso": dati_base.get("corso"),
        "data_rilascio": dati_base.get("data_rilascio"),
        **categoria_data
    }
    logging.info(f"Dati finali combinati: {dati_finali}")

    return dati_finali
