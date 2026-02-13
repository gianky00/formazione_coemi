import json
import logging
import threading
from typing import Any, Optional

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

logger = logging.getLogger(__name__)

# --- AI Configuration ---
GENERATION_CONFIG: dict[str, Any] = {
    "temperature": 0.1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

CATEGORIE_STATICHE: list[str] = [
    "FORMAZIONE",
    "ADDESTRAMENTO",
    "VISITA MEDICA",
    "ABILITAZIONE",
    "ALTRO",
]


class GeminiClient:
    """Singleton for Gemini AI Client."""

    _instance: Optional["GeminiClient"] = None
    _lock = threading.Lock()
    _model: Any = None

    def __new__(cls) -> "GeminiClient":
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    if settings.GEMINI_API_KEY_ANALYSIS:
                        try:
                            genai.configure(api_key=settings.GEMINI_API_KEY_ANALYSIS)
                            cls._model = genai.GenerativeModel(
                                model_name="gemini-2.0-flash",
                                generation_config=GENERATION_CONFIG,
                            )
                        except Exception as e:
                            logger.error(f"Failed to initialize Gemini AI: {e}")
        return cls._instance

    @property
    def model(self) -> Any:
        return self._model


def _get_prompt() -> str:
    """Returns the system prompt for AI extraction."""
    return f"""
    Sei un assistente esperto in estrazione dati da documenti di formazione e sicurezza sul lavoro (certificati, attestati, visite mediche).
    Analizza il testo estratto dal PDF e restituisci un oggetto JSON con i seguenti campi:
    - nome: Nome e Cognome della persona (stringa).
    - data_nascita: Data di nascita (DD/MM/YYYY o null).
    - corso: Titolo del corso o tipo di visita (stringa).
    - categoria: Una di {CATEGORIE_STATICHE} (stringa).
    - data_rilascio: Data di emissione o della visita (DD/MM/YYYY).
    - data_scadenza: Data di scadenza (DD/MM/YYYY o null).

    REGOLE:
    1. Se non trovi la scadenza ma il corso è quinquennale, calcolala (se possibile).
    2. Restituisci SOLO il JSON, niente chiacchiere.
    3. Se il documento non è un certificato valido, restituisci {{"error": "Documento non riconosciuto"}}.
    """


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def _generate_content_with_retry(model: Any, prompt: str, text_content: str) -> str:
    """Calls Gemini API with retry logic."""
    # Ensure configuration is fresh if key rotated
    if settings.GEMINI_API_KEY_ANALYSIS:
        genai.configure(api_key=settings.GEMINI_API_KEY_ANALYSIS)

    response = model.generate_content([prompt, text_content])
    return str(response.text)


def extract_entities_with_ai(pdf_bytes: bytes) -> dict[str, Any]:
    """
    Extracts structured data from PDF content using Gemini AI.
    """
    client = GeminiClient()
    if not client.model:
        return {"error": "AI service not configured (API Key missing)"}

    try:
        # For simplicity in this example, we assume we have a helper to get text from bytes
        # or we pass the bytes directly if using Gemini Multimodal (recommended)
        # Here we'll simulate text extraction or direct byte passing
        from app.utils.file_security import get_pdf_text_preview

        text_content = get_pdf_text_preview(pdf_bytes, max_chars=10000)

        if not text_content or len(text_content.strip()) < 50:
            return {"error": "Il PDF sembra vuoto o non leggibile."}

        raw_response = _generate_content_with_retry(client.model, _get_prompt(), text_content)

        # Clean JSON markdown if present
        clean_json = raw_response.strip().replace("```json", "").replace("```", "")
        data: dict[str, Any] = json.loads(clean_json)

        # Standardize categories
        if data.get("categoria") not in CATEGORIE_STATICHE:
            data["categoria"] = "ALTRO"

        return data

    except Exception as e:
        logger.error(f"AI Extraction error: {e}", exc_info=True)
        return {"error": f"Errore durante l'elaborazione AI: {e!s}"}
