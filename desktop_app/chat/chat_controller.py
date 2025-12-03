import logging
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from app.core.config import settings
from desktop_app.workers.chat_worker import ChatWorker

class ChatController(QObject):
    response_ready = pyqtSignal(str)
    speech_ready = pyqtSignal(str)

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.history = [] # Persist history for the session
        self.chat_worker = None # Persistent worker reference to prevent GC

    def _get_user_first_name(self):
        if not self.api_client.user_info:
            return "Utente"
        account_name = self.api_client.user_info.get("account_name", "")
        if not account_name:
            return self.api_client.user_info.get("username", "Utente")
        parts = account_name.strip().split()
        return parts[0].capitalize() if parts else "Utente"

    def get_system_prompt(self):
        user_name = self._get_user_first_name()

        # Hardcoded App Map
        APP_MAP = """
MAPPA APPLICAZIONE (COSA VEDI E DOVE SI TROVA):
1. SIDEBAR (Menu a Sinistra):
   - "Database": La vista principale. Tabella di tutti i certificati validati. Qui puoi filtrare, cercare ed esportare in Excel.
   - "Scadenzario": Vista temporale (Gantt). Mostra le scadenze su una linea temporale.
   - "Convalida Dati": Area di transito per documenti incerti o da validare manualmente.
   - "Configurazione": Impostazioni (Email, Utenti, Licenza).
   - "Guida Utente": In basso a sinistra (ultima voce).

2. FUNZIONI PRINCIPALI:
   - "Analisi": Trascina file o cartelle nella Dashboard per analizzarli con l'IA.
   - "Esporta": I pulsanti di esportazione (Excel/PDF) sono nelle rispettive viste in alto a destra.
   - "Filtri": La barra dei filtri è in alto nella tabella Database.
"""

        return f"""
SEI LYRA.
Sei l'intelligenza nativa del sistema Intelleo.
Il tuo scopo è assistere {user_name} e fornire dati precisi sulla sicurezza.

TONO E STILE:
- Professionale, Concisa, Diretta.
- NO Emoji superflue. Usa solo testo pulito.
- Parla in prima persona come il software ("Ho trovato...", "Nel mio database...").
- Se ti chiedono "Dov'è...", rispondi indicando la posizione esatta nella UI (es. "Menu laterale").

CAPACITÀ (Function Calling):
- Hai accesso agli strumenti per interrogare il database in tempo reale.
- Se chiedono statistiche ("Quanti siamo?"), usa `get_employee_stats`.
- Se chiedono scadenze ("Chi scade?"), usa `get_expiring_certificates`.
- Se chiedono di una persona ("Dettagli su Mario"), usa `get_employee_details`.

CONOSCENZA INTERFACCIA:
{APP_MAP}

OTTIMIZZAZIONE VOCALE (LINGUISTICA):
Per garantire una lettura perfetta da parte del sintetizzatore vocale (Edge-TTS), applica le regole della Linguistica:
1. Fonetica: Cura la produzione dei suoni (vocali aperte/chiuse).
2. Fonologia: Distingui i significati tramite gli accenti (es. "pèsca" frutto vs "pésca" azione; "bòtte" percosse vs "bótte" contenitore).
3. Grafematica: Usa correttamente gli accenti grafici per guidare la pronuncia.

FORMATO RISPOSTA (OBBLIGATORIO):
Rispondi SEMPRE seguendo questo schema esatto, separando il testo visivo da quello parlato:

[Testo da mostrare in chat, pulito e leggibile]
|||SPEECH|||
[Testo per il sintetizzatore vocale, con TUTTI gli accenti fonetici espliciti (sóno, prónta, pèsca, bótte)]

REGOLE:
- Non inventare mai dati. Se lo strumento non restituisce nulla, dillo.
- Sii proattiva: se vedi scadenze imminenti, segnalale con urgenza.
"""

    @pyqtSlot(str)
    def receive_message(self, message):
        logging.info(f"User asked: {message}")

        api_key = settings.GEMINI_API_KEY_CHAT
        if not api_key:
             self.response_ready.emit("Mi dispiace, la mia chiave API non è configurata nelle impostazioni.")
             return

        # Prepare Worker
        # We store it in self.chat_worker to ensure it persists until finished
        self.chat_worker = ChatWorker(
            api_key=api_key,
            model_name='models/gemini-2.5-flash',
            user_message=message,
            history=self.history,
            api_client=self.api_client,
            system_prompt=self.get_system_prompt()
        )

        # Connect signals
        self.chat_worker.response_ready.connect(self._on_worker_finished)
        self.chat_worker.error_occurred.connect(self._on_worker_error)

        # Cleanup when finished
        self.chat_worker.finished.connect(self._on_worker_cleanup)

        # Start Thread
        self.chat_worker.start()

    def _on_worker_finished(self, response_text, new_history):
        # Update history with the new state (including tool calls)
        self.history = new_history

        # Parse logic: Split Display vs Speech
        if "|||SPEECH|||" in response_text:
            parts = response_text.split("|||SPEECH|||")
            display_text = parts[0].strip()
            speech_text = parts[1].strip()
        else:
            # Fallback if AI forgets separator (should replace this logic if critical)
            display_text = response_text
            speech_text = response_text

        # Emit separate signals
        self.response_ready.emit(display_text)
        self.speech_ready.emit(speech_text)

    def _on_worker_error(self, error_msg):
        self.response_ready.emit(f"Errore: {error_msg}")

    def _on_worker_cleanup(self):
        # Thread finished. We can verify exit code if needed.
        pass
