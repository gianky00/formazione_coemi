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
                if not settings.GEMINI_API_KEY_ANALYSIS:
                    logging.error("GEMINI_API_KEY_ANALYSIS not found.")
                    raise ValueError("GEMINI_API_KEY_ANALYSIS not configured.")
                genai.configure(api_key=settings.GEMINI_API_KEY_ANALYSIS)
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
- ANTINCENDIO: "ADDETTI INCENDIO", "LIVELLO 3", "RISCHIO INCENDIO", "D.M. 2/9/2021", "Corso Antincendio Rischio Medio"
- PREPOSTO: [SOLO ATTESTATI] "Corso per Preposti alla Sicurezza", "Aggiornamento Preposto"
- NOMINA: [SOLO LETTERE DI INCARICO] "Oggetto: NOMINA ADDETTO", "Nomina Addetto al primo soccorso e gestione delle emergenze e incendio", "NOMINA CAPO CANTIERE", "NOMINA PREPOSTO", "Attribuzione e competenze del ruolo di Preposto", "Lettera di incarico"
- VISITA MEDICA: "Giudizio di idoneità alla Mansione Specifica", "Visita medica periodica", "Protocollo Sanitario n."
- UNILAV: "UNILAV - Comunicazione di assunzione", "Comunicazione Obbligatoria Assunzione"
- PATENTE: "Patente di Guida", "Patente B"
- CARTA DI IDENTITA: "Carta d'Identità Elettronica", "Documento di Riconoscimento"
- MODULO RECESSO RAPPORTO DI LAVORO: "Modulo Recesso Rapporto di Lavoro", "Comunicazione di dimissioni"
- HLO: [CORSO] "Attestato HLO", "Certificato HLO"
- TESSERA HLO: [BADGE] "Tessera HLO", "Badge HLO"
- ATEX: "FORMAZIONE SU PROTEZIONE DA ATMOSFERE ESPLOSIVE (ATEX)", "ATEX", "Titolo XI", "CEI 31-34", "Addetti verifiche impianti elettrici ATEX"
- DIRETTIVA SEVESO: "DIRETTIVA SEVESO III", "INCIDENTE RILEVANTE", "D.Lgs. 105/2015", "INFORMAZIONE E FORMAZIONE PER I LAVORATORI"
- BLSD: "OPERATORE BLS-D", "Rianimazione cardiopolmonare di base", "Adulto - Bambino e Lattante", "PBLS-D", "Defibrillazione precoce"
- H2S: "IDROGENO SOLFORATO H2S", "RISCHI DA ESPOSIZIONE AD IDROGENO SOLFORATO", "NORME DI PRIMO SOCCORSO CONTRO I RISCHI DA ESPOSIZIONE"
- GRU A TORRE E PONTE: "GRU A TORRE A ROTAZIONE IN BASSO E A ROTAZIONE IN ALTO", "AGGIORNAMENTO TEORICO/PRATICO PER OPERATORE ADDETTO ALLA CONDUZIONE DI GRU", "CONDUZIONE DI GRU A TORRE"
- PRIMO SOCCORSO: "ADDETTI AL PRIMO SOCCORSO (GRUPPO A)", "D.M. 388", "Gruppo A"
- FORMAZIONE GENERICA ART.37: "AGGIORNAMENTO LAVORATORI", "art. 36 e 37 del D.lgs 81/08", "FORMAZIONE GENERICA", "Corso per la sicurezza e salute sui luoghi"
- CARROPONTE: "FORMAZIONE E ADDESTRAMENTO PER L'UTILIZZO DELLE ATTREZZATURE (CARROPONTE)", "Conduzione di Carroponte", "UTILIZZO DELLE ATTREZZATURE (CARROPONTE)"
- IMBRACATORE: "FORMAZIONE E ADDESTRAMENTO PER IMBRACATORI", "Imbracatura dei carichi", "art. 71 c.7 lettera a"
- DIRIGENTI E FORMATORI: "CORSO FORMAZIONE FORMATORI PER LA SICUREZZA SUL LAVORO", "DIRIGENTI", "Decreto interministeriale del 6 marzo 2013", "Qualificazione del formatore", "FORMATORE SICUREZZA"
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

    REGOLE DI CLASSIFICAZIONE ASSOLUTE (GERARCHIA RIGIDA):
    1.  **DIRETTIVA SEVESO**: Se contiene "DIRETTIVA SEVESO" o "INCIDENTE RILEVANTE" o "D.Lgs. 105/2015", è SEMPRE "DIRETTIVA SEVESO".
    2.  **ATEX**: Se contiene "PROTEZIONE DA ATMOSFERE ESPLOSIVE" o "ATEX" o "Titolo XI", è SEMPRE "ATEX". (Eccezione: se è un corso per "FORMATORI", vedi regola Dirigenti).
    3.  **H2S**: Se contiene "IDROGENO SOLFORATO" o "H2S" o "RISCHI DA ESPOSIZIONE AD IDROGENO", è SEMPRE "H2S".
    4.  **GRU A TORRE E PONTE**: Se contiene "GRU A TORRE" o "ROTAZIONE IN BASSO", è SEMPRE "GRU A TORRE E PONTE".
    5.  **CARROPONTE**: Se contiene "CARROPONTE" o "UTILIZZO DELLE ATTREZZATURE (CARROPONTE)", è SEMPRE "CARROPONTE".
    6.  **IMBRACATORE**: Se contiene "IMBRACATORI" o "IMBRACATURA", è SEMPRE "IMBRACATORE".
    7.  **BLSD**: Se contiene "BLS-D" o "Rianimazione cardiopolmonare" o "PBLS-D", è SEMPRE "BLSD".
    8.  **DIRIGENTI E FORMATORI**: Se contiene "FORMATORI PER LA SICUREZZA", "CORSO FORMAZIONE FORMATORI" o "DIRIGENTI", è SEMPRE "DIRIGENTI E FORMATORI".
    9.  **FORMAZIONE GENERICA ART.37**: Se contiene "FORMAZIONE GENERICA" o ("AGGIORNAMENTO LAVORATORI" e cita "art. 37"), è SEMPRE "FORMAZIONE GENERICA ART.37".

    10. **NOMINA (Lettere di Incarico)**:
        -   Se il documento è una **Lettera di Incarico** o una **Nomina** (es. inizia con "Oggetto: NOMINA ADDETTO", "Nomina Addetto...", "Con la presente Vi notifichiamo di averla nominata..."), la categoria è **SEMPRE** "NOMINA".
        -   **ATTENZIONE:** Questo vale ANCHE SE la nomina è per "Addetto Antincendio" o "Primo Soccorso". Se è una **NOMINA** (lettera), va classificata come "NOMINA".
        -   NON classificare una Lettera di Nomina come "ANTINCENDIO" o "PRIMO SOCCORSO" o "PREPOSTO".

    11. **ANTINCENDIO**: Se il documento è un **ATTESTATO** (non una nomina) e riguarda "ADDETTI INCENDIO", "RISCHIO INCENDIO" o "D.M. 2/9/2021", è "ANTINCENDIO".
    12. **PRIMO SOCCORSO**: Se il documento è un **ATTESTATO** (non una nomina) e riguarda "ADDETTI AL PRIMO SOCCORSO", "D.M. 388" o "Gruppo A", è "PRIMO SOCCORSO".

    ALTRE REGOLE SPECIFICHE:
    -   'PREPOSTO' deve essere usata **SOLO** per **attestati di FORMAZIONE** (es. "Corso per Preposti"). Una "NOMINA PREPOSTO" è una "NOMINA".
    -   "VISITA MEDICA": Solo per "Giudizio di idoneità".
    -   "UNILAV": Solo per "Comunicazione Obbligatoria di Assunzione".
    -   "PATENTE": Solo per Patenti di Guida.
    -   "HLO" vs "TESSERA HLO": Attestato -> "HLO". Badge -> "TESSERA HLO".

    Se non riesci a classificare in nessuna delle categorie sopra, usa "ALTRO".

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
