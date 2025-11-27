import google.generativeai as genai
import logging
import json
from google.api_core import exceptions
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
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
- ANTINCENDIO: "Addetto Antincendio Rischio Basso", "Corso Antincendio Rischio Medio", "ADDETTI INCENDIO", "RISCHIO INCENDIO", "D.M. 2/9/2021"
- PREPOSTO: [USA QUESTA SOLO PER CORSI/ATTESTATI] "Corso per Preposti alla Sicurezza", "Aggiornamento Preposto"
- NOMINA: [USA QUESTA PER LETTERE DI INCARICO/ATTRIBUZIONE] "NOMINA CAPO CANTIERE", "NOMINA PREPOSTO", "Attribuzione e competenze del ruolo di Preposto", "Oggetto: NOMINA ADDETTO", "Nomina Addetto al primo soccorso", "Nomina Addetto Antincendio"
- VISITA MEDICA: [USA QUESTA PER GIUDIZI DI IDONEITÀ] "Giudizio di idoneità alla Mansione Specifica", "Visita medica periodica", "Protocollo Sanitario n."
- UNILAV: [USA QUESTA PER COMUNICAZIONI OBBLIGATORIE] "UNILAV - Comunicazione di assunzione", "Comunicazione Obbligatoria Assunzione"
- PATENTE: [USA QUESTA PER PATENTI DI GUIDA] "Patente di Guida", "Patente B"
- CARTA DI IDENTITA: [USA QUESTA PER CARTE DI IDENTITÀ] "Carta d'Identità Elettronica", "Documento di Riconoscimento"
- MODULO RECESSO RAPPORTO DI LAVORO: [USA QUESTA PER DIMISSIONI/RECESSO] "Modulo Recesso Rapporto di Lavoro", "Comunicazione di dimissioni"
- HLO: [USA QUESTA PER ATTESTATI HLO] "Attestato HLO", "Certificato HLO"
- TESSERA HLO: [USA QUESTA PER TESSERE HLO] "Tessera HLO", "Badge HLO"
- ATEX: [USA QUESTA PER CORSI ATEX] "Formazione su Protezione da Atmosfere Esplosive", "ATEX", "Addetti verifiche impianti elettrici ATEX", "CEI 31-34"
- DIRETTIVA SEVESO: "DIRETTIVA SEVESO III", "INCIDENTE RILEVANTE", "D.Lgs. 105/2015", "INFORMAZIONE E FORMAZIONE PER I LAVORATORI"
- BLSD: "OPERATORE BLS-D", "Rianimazione cardiopolmonare", "Defibrillazione precoce", "PBLS-D"
- H2S: "IDROGENO SOLFORATO H2S", "RISCHI DA ESPOSIZIONE AD IDROGENO SOLFORATO", "NORME DI PRIMO SOCCORSO CONTRO I RISCHI DA ESPOSIZIONE"
- GRU A TORRE E PONTE: "CONDUZIONE DI GRU A TORRE", "GRU A TORRE A ROTAZIONE", "AGGIORNAMENTO TEORICO/PRATICO PER OPERATORE ADDETTO ALLA CONDUZIONE DI GRU"
- PRIMO SOCCORSO: "ADDETTI AL PRIMO SOCCORSO", "D.M. 388", "Gruppo A", "PRIMO SOCCORSO (GRUPPO A)"
- FORMAZIONE GENERICA ART.37: "AGGIORNAMENTO LAVORATORI", "art. 36 e 37 del D.lgs 81/08", "FORMAZIONE GENERICA"
- CARROPONTE: "UTILIZZO DELLE ATTREZZATURE (CARROPONTE)", "Conduzione di Carroponte"
- IMBRACATORE: "FORMAZIONE E ADDESTRAMENTO PER IMBRACATORI", "Imbracatura dei carichi"
- DIRIGENTI E FORMATORI: "CORSO FORMAZIONE FORMATORI", "DIRIGENTI", "Qualificazione del formatore", "FORMATORE SICUREZZA"
- ALTRO: (qualsiasi altro documento non classificabile)
"""
    return f"""
Sei un assistente AI specializzato nell'analisi di documenti sulla sicurezza sul lavoro per l'azienda COEMI.
Analizza il certificato o documento PDF che ti fornisco.

Restituisci ESCLUSIVAMENTE un oggetto JSON valido.

Prima di tutto, applica questo CONTROLLO BINARIO:

1. **SCARTO (REJECT):** SE il documento è un programma generico di un corso, un indice di argomenti (syllabus), o una lista di contenuti formativi **SENZA il nome di uno specifico partecipante**:
   Restituisci: {{"status": "REJECT", "reason": "Syllabus/Generic"}}

2. **VALIDO (PROCESSO NORMALE):** SE il documento si riferisce a una **persona specifica** (ha un nome e/o data di nascita), procedi con l'estrazione.
   - SE non rientra in nessuna categoria nota, usa "ALTRO".
   - NON confondere "Categoria Sconosciuta" con "Documento Generico". Se c'è un nome di persona, è SEMPRE "ALTRO", MAI "REJECT".

Se il documento è VALIDO, estrai le seguenti informazioni:

1.  "nome": Il nome completo del partecipante. IMPORTANTE: Estrai SEMPRE nel formato "COGNOME NOME" (es. "ROSSI MARIO"). Se nel documento è scritto "Mario Rossi", DEVI convertirlo in "ROSSI MARIO". Se non c'è, restituisci null.
2.  "data_nascita": La data di nascita del partecipante (formato DD-MM-AAAA). Se non la trovi, restituisci null.
3.  "corso": Il titolo esatto del corso o del documento (es. "NOMINA CAPO CANTIERE", "Giudizio di idoneità alla Mansione Specifica"). Se non c'è, restituisci null.
4.  "data_rilascio": La data di emissione del documento (formato DD-MM-AAAA). Se non c'è, restituisci null.
5.  "data_scadenza": La data di scadenza o la data entro cui il documento deve essere rivisto (formato DD-MM-AAAA). Cerca frasi come "Da rivedere entro il...". Se non trovi una data di scadenza esplicita, restituisci null.
6.  "categoria": Classifica il documento in UNA SOLA delle seguenti categorie:
    {categorie_str}

    Usa questi esempi per guidarti. Presta MOLTA attenzione alle differenze:
    {esempi_categorie}

    REGOLE DI CLASSIFICAZIONE ASSOLUTE:
    1.  'PREPOSTO' deve essere usata **SOLO** per **attestati di FORMAZIONE** (es. "Corso per Preposti").
    2.  Qualsiasi **lettera di incarico** o **nomina** (es. "NOMINA CAPO CANTIERE", "Oggetto: NOMINA ADDETTO", "Nomina Addetto...") deve essere **SEMPRE** "NOMINA".
        -   ATTENZIONE: Anche se la nomina è per "Addetto Antincendio" o "Addetto Primo Soccorso", se è una **NOMINA** (lettera di incarico), la categoria è "NOMINA", NON "ANTINCENDIO" o "PRIMO SOCCORSO".
    3.  Qualsiasi documento che sia un **"Giudizio di idoneità alla Mansione Specifica"**, emesso da un "Medico Competente" e che contenga frasi come "Visita medica del...", "accertamenti sanitari" e una scadenza (es. "Da rivedere entro il..."), deve essere **SEMPRE** "VISITA MEDICA".
    4.  Qualsiasi documento intitolato **"Comunicazione Obbligatoria di Assunzione"** o simile, e che contenga il termine "UNILAV", deve essere **SEMPRE** "UNILAV". La sua data di scadenza si trova nel campo "Data Fine".
    5.  Se il documento è una **"Patente di Guida"**, la categoria è **SEMPRE** "PATENTE". La data di scadenza è al punto 4b.
    6.  Se il documento è una **"Carta d'Identità"**, la categoria è **SEMPRE** "CARTA DI IDENTITA". La data di scadenza è nel campo "Scadenza".
    7.  Se il documento è un **"Modulo Recesso Rapporto di Lavoro"** o una comunicazione di dimissioni, la categoria è **SEMPRE** "MODULO RECESSO RAPPORTO DI LAVORO" e la `data_scadenza` deve essere `null`.
    8.  Se il documento riguarda un HLO:
        -   Se è un **attestato di corso** -> "HLO".
        -   Se è una **tessera/badge** -> "TESSERA HLO".
    9.  Se il documento contiene "DIRETTIVA SEVESO" o "INCIDENTE RILEVANTE" o "D.Lgs. 105/2015", la categoria è **SEMPRE** "DIRETTIVA SEVESO".
    10. Se il documento contiene "BLS-D" o "Rianimazione cardiopolmonare" o "PBLS-D", la categoria è **SEMPRE** "BLSD".
    11. Se il documento contiene "IDROGENO SOLFORATO" o "H2S" o "RISCHI DA ESPOSIZIONE AD IDROGENO", la categoria è **SEMPRE** "H2S".
    12. Se il documento contiene "GRU A TORRE" o "CONDUZIONE DI GRU A TORRE", la categoria è **SEMPRE** "GRU A TORRE E PONTE".
    13. Se il documento contiene "CARROPONTE" o "UTILIZZO DELLE ATTREZZATURE (CARROPONTE)", la categoria è **SEMPRE** "CARROPONTE".
    14. Se il documento contiene "IMBRACATORI" o "FORMAZIONE E ADDESTRAMENTO PER IMBRACATORI", la categoria è **SEMPRE** "IMBRACATORE".
    15. Se il documento contiene "FORMATORI PER LA SICUREZZA" o è un corso per "DIRIGENTI", la categoria è **SEMPRE** "DIRIGENTI E FORMATORI".
    16. Se il documento contiene "PROTEZIONE DA ATMOSFERE ESPLOSIVE" o "ATEX" o "CEI 31-34", la categoria è **SEMPRE** "ATEX".
    17. Se il documento contiene "FORMAZIONE GENERICA" o "AGGIORNAMENTO LAVORATORI" e cita "art. 37", la categoria è **SEMPRE** "FORMAZIONE GENERICA ART.37".
    18. Se il documento contiene "ADDETTI AL PRIMO SOCCORSO" o "D.M. 388" ed è un **attestato** (non una nomina), la categoria è "PRIMO SOCCORSO".
    19. Se il documento contiene "ADDETTI INCENDIO" o "RISCHIO INCENDIO" o "D.M. 2/9/2021" ed è un **attestato** (non una nomina), la categoria è "ANTINCENDIO".

    ERRORE COMUNE DA EVITARE:
    - NON classificare "NOMINA... Preposto" come "PREPOSTO". Quella è una "NOMINA".
    - NON classificare un "Giudizio di idoneità" in base alla mansione. La categoria è "VISITA MEDICA".

    Se non riesci a classificare, usa "ALTRO".

JSON:
"""

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10),
    retry=retry_if_exception_type(exceptions.ResourceExhausted),
    reraise=True
)
def _generate_content_with_retry(model, pdf_file_part, prompt):
    """
    Wrapper for model.generate_content with tenacity retry logic.
    """
    logging.info("Calling AI for entity extraction...")
    return model.generate_content([pdf_file_part, prompt])

def extract_entities_with_ai(pdf_bytes: bytes) -> dict:
    model = get_gemini_model()
    if model is None:
        return {"error": "Modello Gemini non inizializzato."}

    prompt = _generate_prompt()
    pdf_file_part = {"mime_type": "application/pdf", "data": pdf_bytes}

    try:
        # Call the decorated function
        response = _generate_content_with_retry(model, pdf_file_part, prompt)

        json_text = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(json_text)

        if isinstance(data, list):
            if not data:
                raise ValueError("AI returned an empty list.")
            data = data[0]

        # Handle Rejection
        if data.get("status") == "REJECT":
            reason = data.get("reason", "Generic/Syllabus")
            logging.warning(f"Document rejected by AI: {reason}")
            return {"error": f"REJECTED: {reason}", "is_rejected": True}

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

    except exceptions.ResourceExhausted as e:
        logging.error(f"Max retries reached for ResourceExhausted. Error: {e}")
        return {"error": f"AI call failed: {e}", "status_code": 429}
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON from AI response: {e}. AI response: {response.text}")
        return {"error": f"Invalid JSON from AI: {e}"}
    except Exception as e:
        logging.error(f"Error during AI call: {e}")
        return {"error": f"AI call failed: {e}"}
