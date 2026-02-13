import json
import logging
import re
import threading
from typing import Any, Optional

import google.generativeai as genai  # type: ignore
from google.api_core import exceptions
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.ai_lock import ai_global_lock
from app.core.config import settings
from app.core.constants import CATEGORIE_STATICHE

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class GeminiClient:
    _instance: Optional["GeminiClient"] = None
    _model: Any = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "GeminiClient":
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    try:
                        if not settings.GEMINI_API_KEY_ANALYSIS:
                            logging.error("GEMINI_API_KEY_ANALYSIS not found.")
                            raise ValueError("GEMINI_API_KEY_ANALYSIS not configured.")

                        # Configure with lock to prevent race with Chat
                        with ai_global_lock:
                            genai.configure(api_key=settings.GEMINI_API_KEY_ANALYSIS)
                            cls._model = genai.GenerativeModel("models/gemini-2.5-pro")

                        logging.info(
                            "Gemini model 'models/gemini-2.5-pro' initialized successfully."
                        )
                    except Exception as e:
                        logging.error(f"Failed to initialize Gemini model: {e}")
                        cls._instance = None
                        raise
        return cls._instance

    def get_model(self) -> Any:
        return self._model


def get_gemini_model() -> Any:
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


# Bug 10 Fix: Robust Retry Policy
@retry(
    stop=stop_after_attempt(6),
    wait=wait_exponential(multiplier=2, min=5, max=60),
    retry=retry_if_exception_type(
        (
            exceptions.ResourceExhausted,
            exceptions.ServiceUnavailable,
            exceptions.InternalServerError,
        )
    ),
    reraise=True,
)
def _generate_content_with_retry(model: Any, pdf_file_part: dict[str, Any], prompt: str) -> Any:
    """
    Wrapper for model.generate_content with tenacity retry logic.
    """
    logging.info("Calling AI for entity extraction...")

    with ai_global_lock:
        current_key = settings.GEMINI_API_KEY_ANALYSIS
        if current_key:
            genai.configure(api_key=current_key)
        return model.generate_content([pdf_file_part, prompt])


def _check_closing_char(stack: list[str], char: str) -> bool:
    """Helper to check if closing char matches opening char on stack."""
    if not stack:
        return False
    last = stack[-1]
    if (last == "{" and char == "}") or (last == "[" and char == "]"):
        stack.pop()
        return not stack
    return False


def _find_json_block(text: str, start_idx: int, stack: list[str]) -> int:
    for i, char in enumerate(text[start_idx:], start=start_idx):
        if char == "{" or char == "[":
            stack.append(char)
        elif (char == "}" or char == "]") and _check_closing_char(stack, char):
            return i + 1
    return -1


def _find_start_index(text: str) -> int:
    """Finds the starting index of a JSON object or list."""
    for i, char in enumerate(text):
        if char == "{" or char == "[":
            return i
    return -1


def _extract_json_block(text: str) -> str:
    """
    Robustly extracts the first valid JSON block from text, handling nested structures.
    """
    text = text.strip()

    if len(text) < 100000:
        match = re.search(r"```json\s*(.*?)```", text, re.DOTALL)
        if match:
            text = match.group(1).strip()
    else:
        if text.startswith("```json"):
            end_marker = "```"
            start = 7
            end = text.rfind(end_marker)
            if end != -1:
                text = text[start:end].strip()

    start_idx = _find_start_index(text)

    if start_idx == -1:
        return text

    stack: list[str] = []
    end_idx = _find_json_block(text, start_idx, stack)

    if end_idx != -1:
        return text[start_idx:end_idx]

    return text


def _parse_and_validate_ai_response(text_response: str) -> dict[str, Any]:
    """Parses JSON and performs initial validation on the AI response."""
    json_text = _extract_json_block(text_response)
    data = json.loads(json_text)

    if isinstance(data, list):
        if not data:
            raise ValueError("AI returned an empty list.")
        first_item: dict[str, Any] = data[0]
        if len(data) > 1:
            logging.warning(f"AI returned {len(data)} items. Processing only the first one.")
            first_item["warning"] = "multiple_certificates_found_check_file"
        data = first_item

    return dict(data)


def extract_entities_with_ai(pdf_bytes: bytes) -> dict[str, Any]:
    model = get_gemini_model()
    if model is None:
        return {"error": "Modello Gemini non inizializzato."}

    prompt = _generate_prompt()
    pdf_file_part = {"mime_type": "application/pdf", "data": pdf_bytes}

    try:
        response = _generate_content_with_retry(model, pdf_file_part, prompt)
        text_response = str(response.text).strip()
        data = _parse_and_validate_ai_response(text_response)

        if data.get("status") == "REJECT":
            reason = data.get("reason", "Generic/Syllabus")
            logging.warning(f"Document rejected by AI: {reason}")
            return {"error": f"REJECTED: {reason}", "is_rejected": True}

        data.setdefault("categoria", "ALTRO")

        logging.info(f"Successfully extracted data: {data}")
        return data

    except exceptions.ResourceExhausted as e:
        logging.error(f"Max retries reached for ResourceExhausted. Error: {e}")
        return {"error": f"AI call failed (Quota/Limit): {e}", "status_code": 429}
    except (exceptions.ServiceUnavailable, exceptions.InternalServerError) as e:
        logging.error(f"Max retries reached for Service Error. Error: {e}")
        return {"error": f"AI service unavailable: {e}"}
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON from AI response: {e}")
        return {"error": f"Invalid JSON from AI: {e}"}
    except Exception as e:
        logging.error(f"Error during AI call: {e}")
        return {"error": f"AI call failed: {e}"}
