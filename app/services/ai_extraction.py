import google.generativeai as genai
import logging
import json
from app.core.config import settings
from app.core.constants import CATEGORIE_STATICHE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GeminiClient:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeminiClient, cls).__new__(cls)
            try:
                if not settings.GEMINI_API_KEY:
                    logging.error("GEMINI_API_KEY not found.")
                    raise ValueError("GEMINI_API_KEY not configured.")
                genai.configure(api_key=settings.GEMINI_API_KEY)
                cls._model = genai.GenerativeModel('models/gemini-2.5-pro')
                logging.info("Gemini model 'models/gemini-2.5-pro' initialized successfully.")
            except Exception as e:
                logging.error(f"Failed to initialize Gemini model: {e}")
                cls._instance = None
                raise
        return cls._instance

    def get_model(self):
        return self._model

def get_gemini_model():
    try:
        return GeminiClient().get_model()
    except ValueError as e:
        logging.error(f"Error getting Gemini model: {e}")
        return None

def _generate_prompt() -> str:
    categorie_str = ", ".join(f'"{c}"' for c in CATEGORIE_STATICHE)
    esempi_categorie = """
- ANTINCENDIO: "Addetto Antincendio Rischio Basso", "Corso Antincendio Rischio Medio"
- PREPOSTO: [USA QUESTA SOLO PER CORSI/ATTESTATI] "Corso per Preposti alla Sicurezza", "Aggiornamento Preposto".
- NOMINE: [USA QUESTA PER LETTERE DI INCARICO/ATTRIBUZIONE] "NOMINA CAPO CANTIERE", "NOMINA PREPOSTO", "Attribuzione e competenze del ruolo di Preposto"
- VISITA MEDICA: [USA QUESTA PER GIUDIZI DI IDONEITÀ] "Giudizio di idoneità alla Mansione Specifica", "Visita medica periodica"
- ALTRO: (qualsiasi altro documento non classificabile)
"""
    return f"""
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

def extract_entities_with_ai(pdf_bytes: bytes) -> dict:
    model = get_gemini_model()
    if model is None:
        return {"error": "Modello Gemini non inizializzato."}

    prompt = _generate_prompt()
    pdf_file_part = {"mime_type": "application/pdf", "data": pdf_bytes}

    try:
        logging.info("Calling AI for entity extraction and classification...")
        response = model.generate_content([pdf_file_part, prompt])

        json_text = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(json_text)

        data.setdefault("categoria", "ALTRO")
        if data["categoria"] not in CATEGORIE_STATICHE:
            logging.warning(f"Invalid category '{data['categoria']}'. Defaulting to 'ALTRO'.")
            data["categoria"] = "ALTRO"

        logging.info(f"Successfully extracted data: {data}")
        return data

    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON from AI response: {e}. AI response: {response.text}")
        return {"error": f"Invalid JSON from AI: {e}"}
    except Exception as e:
        logging.error(f"Error during AI call: {e}")
        return {"error": f"AI call failed: {e}"}
