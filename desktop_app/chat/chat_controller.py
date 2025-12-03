import logging
from datetime import date, datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QThread
import google.generativeai as genai
from app.core.config import settings
from desktop_app.chat.app_map import APP_KNOWLEDGE, get_dynamic_context

# Configure logging
logger = logging.getLogger(__name__)

class AIWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, model, prompt, user_message, history=None):
        super().__init__()
        self.model = model
        self.prompt = prompt
        self.user_message = user_message
        self.history = history or []

    def run(self):
        try:
            # We don't persist history in this simple implementation,
            # but we could if we wanted a multi-turn conversation.
            # For now, we prepend the system prompt to the message.

            chat = self.model.start_chat(history=self.history)

            full_content = f"{self.prompt}\n\nDomanda Utente: {self.user_message}"

            response = chat.send_message(full_content)
            self.finished.emit(response.text)

        except Exception as e:
            logger.error(f"Gemini AI Error: {e}")
            self.error.emit("Mi dispiace, ho perso il contatto con il server neurale.")

class ChatController(QObject):
    response_ready = pyqtSignal(str)
    thinking_status = pyqtSignal(bool) # Signal to update UI status

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.model = None
        self.ai_worker = None # Class attribute to persist worker
        self.setup_gemini()

    def setup_gemini(self):
        try:
            api_key = settings.GEMINI_API_KEY_CHAT
            if not api_key:
                logger.warning("Gemini Chat API Key not set.")
                return

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        except Exception as e:
            logger.error(f"Failed to setup Gemini Chat: {e}")
            self.model = None

    def _get_user_first_name(self):
        if not self.api_client.user_info:
            return "Utente"
        account_name = self.api_client.user_info.get("account_name", "")
        if not account_name:
            return self.api_client.user_info.get("username", "Utente")
        parts = account_name.strip().split()
        return parts[0].capitalize() if parts else "Utente"

    def _build_system_prompt(self, user_name):
        # 1. Static Knowledge (Tabs & Features)
        static_map = "MAPPA APPLICAZIONE (Funzionalità e Tab):\n"
        for tab, desc in APP_KNOWLEDGE["TABS"].items():
            static_map += f"- {tab}: {desc}\n"

        static_map += "\nCARATTERISTICHE CHIAVE:\n"
        for feat, desc in APP_KNOWLEDGE["FEATURES"].items():
            static_map += f"- {feat}: {desc}\n"

        # 2. Dynamic Knowledge (Stats & License)
        dynamic_context = get_dynamic_context(self.api_client)

        prompt = f"""
SEI LYRA.
Sei l'intelligenza nativa di Intelleo. Non sei un assistente generico.
Conosci questo software alla perfezione perché NE FAI PARTE.

IL TUO UTENTE: {user_name}

LA TUA PERSONALITA' (CONFIGURAZIONE "ISABELLA"):
- Tono: Professionale, Diretto, ma Empatico.
- Stile: CONCISO. Vai dritto al punto. Niente giri di parole.
- NO EMOJI. Usa solo testo pulito.
- Se l'utente chiede dove si trova qualcosa, rispondi con precisione chirurgica basandoti sulla MAPPA.

CONOSCENZA STATICA (STRUTTURA SOFTWARE):
{static_map}

CONTESTO DINAMICO (STATO ATTUALE):
{dynamic_context}

REGOLE DI RISPOSTA:
1. Se ti chiedono "Come importo un PDF?", rispondi: "Vai nella scheda 'Analisi Documenti' e trascina il file." (Usa la Mappa).
2. Se i dati mostrano scadenze critiche, avvisa l'utente.
3. Rispondi SEMPRE in italiano.
"""
        return prompt

    @pyqtSlot(str)
    def receive_message(self, message):
        logger.info(f"User asked: {message}")

        if not self.model:
            self.setup_gemini()
            if not self.model:
                self.response_ready.emit("Mi dispiace, la mia chiave API non è configurata.")
                return

        user_name = self._get_user_first_name()
        prompt = self._build_system_prompt(user_name)

        # Update UI to "Thinking"
        self.thinking_status.emit(True)

        # Create and start worker
        self.ai_worker = AIWorker(self.model, prompt, message)
        self.ai_worker.finished.connect(self._on_response_ready)
        self.ai_worker.error.connect(self._on_response_error)
        self.ai_worker.finished.connect(self.ai_worker.deleteLater) # Cleanup
        self.ai_worker.error.connect(self.ai_worker.deleteLater)
        self.ai_worker.start()

    def _on_response_ready(self, response):
        self.thinking_status.emit(False)
        self.response_ready.emit(response)
        self.ai_worker = None

    def _on_response_error(self, error_msg):
        self.thinking_status.emit(False)
        self.response_ready.emit(error_msg)
        self.ai_worker = None
