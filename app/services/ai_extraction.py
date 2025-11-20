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
    # Assicuriamo che ATEX sia incluso nelle categorie inviate al prompt
    categorie_list = list(CATEGORIE_STATICHE)
    if "ATEX" not in categorie_list:
        categorie_list.append("ATEX")
    
    categorie_str = ", ".join(f'"{c}"' for c in categorie_list)
    
    esempi_categorie = """
- ANTINCENDIO: "Addetto Antincendio Rischio Basso", "Corso Antincendio Rischio Medio"
- PREPOSTO: [USA QUESTA SOLO PER CORSI/ATTESTATI] "Corso per Preposti alla Sicurezza", "Aggiornamento Preposto".
- NOMINE: [USA QUESTA PER LETTERE DI INCARICO/ATTRIBUZIONE] "NOMINA CAPO CANTIERE", "NOMINA PREPOSTO", "Attribuzione e competenze del ruolo di Preposto"
- VISITA MEDICA: [USA QUESTA PER GIUDIZI DI IDONEITÀ] "Giudizio di idoneità alla Mansione Specifica", "Visita medica periodica"
- UNILAV: [USA QUESTA PER COMUNICAZIONI OBBLIGATORIE] "UNILAV - Comunicazione di assunzione", "Comunicazione Obbligatoria Assunzione"
- PATENTE: [USA QUESTA PER PATENTI DI GUIDA] "Patente di Guida", "Patente B"
- CARTA DI IDENTITA: [USA QUESTA PER CARTE DI IDENTITÀ] "Carta d'Identità Elettronica", "Documento di Riconoscimento"
- MODULO RECESSO RAPPORTO DI LAVORO: [USA QUESTA PER DIMISSIONI/RECESSO] "Modulo Recesso Rapporto di Lavoro", "Comunicazione di dimissioni"
- HLO: [USA QUESTA PER ATTESTATI HLO] "Attestato HLO", "Certificato HLO"
- TESSERA HLO: [USA QUESTA PER TESSERE HLO] "Tessera HLO", "Badge HLO"
- ATEX: [USA QUESTA PER CORSI ATEX] "Formazione su Protezione da Atmosfere Esplosive", "ATEX", "Addetti verifiche impianti elettrici ATEX"
- ALTRO: (qualsiasi altro documento non classificabile)
"""
    return f"""
Sei un assistente AI specializzato nell'analisi di documenti sulla sicurezza sul lavoro per l'azienda COEMI.
Analizza il certificato o documento PDF che ti fornisco.

Estrai le seguenti informazioni e classificalo. Restituisci ESCLUSIVAMENTE un oggetto JSON valido.

1.  "nome": Il nome completo del partecipante (es. "MARIO ROSSI"). Se non c'è, restituisci null.
2.  "data_nascita": La data di nascita del partecipante (formato DD-MM-AAAA). Se non la trovi, restituisci null.
3.  "corso": Il titolo esatto del corso o del documento (es. "NOMINA CAPO CANTIERE", "Giudizio di idoneità alla Mansione Specifica"). Se non c'è, restituisci null.
4.  "data_rilascio": La data di emissione del documento (formato DD-MM-AAAA). Se non c'è, restituisci null.
5.  "data_scadenza": La data di scadenza o la data entro cui il documento deve essere rivisto (formato DD-MM-AAAA). Cerca frasi come "Da rivedere entro il...". Se non trovi una data di scadenza esplicita, restituisci null.
6.  "categoria": Classifica il documento in UNA SOLA delle seguenti categorie:
    {categorie_str}

    Usa questi esempi per guidarti. Presta MOLTA attenzione alle differenze:
    {esempi_categorie}

    REGOLE DI CLASSIFICAZIONE ASSOLUTE:
    1.  'PREPOSTO' deve essere usata **SOLO** per **attestati di FORMAZIONE**.
    2.  Qualsiasi **lettera di incarico** o **nomina** (es. "NOMINA CAPO CANTIERE", "Attribuzione... ruolo di Preposto") deve essere **SEMPRE** "NOMINE".
    3.  Qualsiasi documento che sia un **"Giudizio di idoneità alla Mansione Specifica"**, emesso da un "Medico Competente" e che contenga frasi come "Visita medica del...", "accertamenti sanitari" e una scadenza (es. "Da rivedere entro il..."), deve essere **SEMPRE** "VISITA MEDICA".
    4.  Qualsiasi documento intitolato **"Comunicazione Obbligatoria di Assunzione"** o simile, e che contenga il termine "UNILAV", deve essere **SEMPRE** "UNILAV". La sua data di scadenza si trova nel campo "Data Fine".
    5.  Se il documento è una **"Patente di Guida"**, la categoria è **SEMPRE** "PATENTE". La data di scadenza è al punto 4b.
    6.  Se il documento è una **"Carta d'Identità"**, la categoria è **SEMPRE** "CARTA DI IDENTITA". La data di scadenza è nel campo "Scadenza".
    7.  Se il documento è un **"Modulo Recesso Rapporto di Lavoro"** o una comunicazione di dimissioni, la categoria è **SEMPRE** "MODULO RECESSO RAPPORTO DI LAVORO" e la `data_scadenza` deve essere `null`.
    8.  Se il documento è relativo a un HLO (Helicopter Landing Officer), controlla se è un **attestato di corso** (in quel caso la categoria è "HLO") o una **tessera/badge personale** (in quel caso la categoria è "TESSERA HLO").
    9.  Se il documento riguarda la formazione su **"Atmosfere Esplosive"** o contiene il termine **"ATEX"**, la categoria deve essere **SEMPRE** "ATEX".

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

        if isinstance(data, list):
            if not data:
                raise ValueError("AI returned an empty list.")
            data = data[0]

        data.setdefault("categoria", "ALTRO")

        # Aggiungiamo ATEX alle categorie valide consentite
        valid_categories = list(CATEGORIE_STATICHE)
        if "ATEX" not in valid_categories:
            valid_categories.append("ATEX")

        if data["categoria"] not in valid_categories:
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