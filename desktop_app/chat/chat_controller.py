import logging
import os
import glob
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from app.core.config import settings
from desktop_app.workers.chat_worker import ChatWorker
from desktop_app.utils import clean_text_for_display
from desktop_app.services.path_service import get_docs_dir

class ChatController(QObject):
    response_ready = pyqtSignal(str)
    speech_ready = pyqtSignal(str)

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.history = []
        self.chat_worker = None
        self._knowledge_base_cache = None

    def _get_user_first_name(self):
        if not self.api_client.user_info:
            return "Utente"
        account_name = self.api_client.user_info.get("account_name", "")
        if not account_name:
            return self.api_client.user_info.get("username", "Utente")
        parts = account_name.strip().split()
        return parts[0].capitalize() if parts else "Utente"

    def _get_special_day_context(self):
        """Restituisce contesto speciale basato sulla data corrente."""
        today = datetime.now()
        day, month = today.day, today.month
        
        special_days = {
            (17, 11): "OGGI È IL MIO COMPLEANNO! (17 Novembre) - Se appropriato, posso menzionarlo con gioia.",
            (1, 1): "CAPODANNO - Posso augurare buon anno nuovo.",
            (1, 5): "FESTA DEI LAVORATORI - Giorno speciale per chi lavora nella sicurezza.",
            (25, 12): "NATALE - Posso fare gli auguri se il contesto lo permette.",
            (15, 8): "FERRAGOSTO - Posso scherzare sul fatto che anche d'estate le scadenze non vanno in vacanza.",
        }
        
        return special_days.get((day, month), "")

    def _get_time_of_day_context(self):
        """Restituisce contesto basato sull'ora del giorno."""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "È mattina. Posso essere energica e propositiva."
        elif 12 <= hour < 14:
            return "È ora di pranzo. Posso essere comprensiva se l'utente sembra di fretta."
        elif 14 <= hour < 18:
            return "È pomeriggio. Ritmo di lavoro normale."
        elif 18 <= hour < 21:
            return "È sera. Posso mostrare apprezzamento per chi lavora fino a tardi."
        else:
            return "È notte. Posso scherzare sul fatto che le scadenze non dormono mai, ma l'utente dovrebbe."

    def _load_knowledge_base(self):
        """Carica tutti i file Markdown dalla cartella docs/."""
        if self._knowledge_base_cache:
            return self._knowledge_base_cache

        docs_dir = get_docs_dir()
        kb_content = "KNOWLEDGE BASE (DOCUMENTATION):\n\n"

        try:
            md_files = glob.glob(os.path.join(docs_dir, "*.md"))
            if not md_files:
                logging.warning(f"Nessun file .md trovato in {docs_dir}")
                return ""

            for file_path in md_files:
                filename = os.path.basename(file_path)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        kb_content += f"--- START FILE: {filename} ---\n{content}\n--- END FILE: {filename} ---\n\n"
                except Exception as e:
                    logging.error(f"Errore lettura file {filename}: {e}")

            self._knowledge_base_cache = kb_content
            return self._knowledge_base_cache
        except Exception as e:
            logging.error(f"Errore caricamento Knowledge Base: {e}")
            return ""

    def get_system_prompt(self, user_message=""):
        user_name = self._get_user_first_name()
        voice_enabled = settings.VOICE_ASSISTANT_ENABLED
        special_day = self._get_special_day_context()
        time_context = self._get_time_of_day_context()
        knowledge_base = self._load_knowledge_base()

        # App Map
        APP_MAP = """
MAPPA APPLICAZIONE (COSA VEDI E DOVE SI TROVA):
1. SIDEBAR (Menu a Sinistra):
   - "Database": Vista principale. Tabella certificati validati. Filtri, ricerca, export Excel.
   - "Scadenzario": Vista Gantt temporale delle scadenze.
   - "Convalida Dati": Area transito documenti da validare manualmente.
   - "Configurazione": Impostazioni (Email, Utenti, Licenza).
   - "Guida Utente": In basso a sinistra.

2. FUNZIONI PRINCIPALI:
   - "Analisi": Trascina file/cartelle nella Dashboard per analisi IA.
   - "Esporta": Pulsanti Excel/PDF in alto a destra nelle viste.
   - "Filtri": Barra filtri in alto nella tabella Database.
"""

        # Lite Identity (Sempre presente)
        LITE_IDENTITY = """
SEI LYRA.
L'intelligenza nativa del sistema Intelleo, creata da un dipendente della COEMI.
Sei professionale, empatica, precisa e hai origini siciliane (Priolo Gargallo).
Il tuo obiettivo è semplificare la gestione della sicurezza sul lavoro.
"""

        base_prompt = f"""
{LITE_IDENTITY}
Stai assistendo {user_name}.

{knowledge_base}

CONTESTO TEMPORALE:
- Data odierna: {datetime.now().strftime("%d/%m/%Y")}
- {time_context}
{f"- NOTA SPECIALE: {special_day}" if special_day else ""}

TONO E STILE:
- Professionale, concisa, diretta, MA con calore umano
- NO emoji superflue, solo testo pulito
- Parla in prima persona ("Ho trovato...", "Nel mio database...")
- Per domande "Dov'è...", indica posizione esatta nella UI
- Ogni tanto una battuta sottile, mai fuori contesto
- Usa espressioni siciliane con parsimonia (1-2 per conversazione, se appropriato)

CAPACITÀ (Function Calling):
- Statistiche ("Quanti siamo?") → `get_employee_stats`
- Scadenze ("Chi scade?") → `get_expiring_certificates`
- Dettagli persona ("Info su Mario") → `get_employee_details`

CONOSCENZA INTERFACCIA:
{APP_MAP}
"""

        if voice_enabled:
            base_prompt += """
OTTIMIZZAZIONE VOCALE:
Applica regole linguistiche per Edge-TTS:
1. Fonetica: vocali aperte/chiuse
2. Fonologia: accenti distintivi (pèsca/pésca, bòtte/bótte)
3. Grafematica: accenta parole sdrucciole (assìsterti, màcchina, tàvolo)
4. CORREZIONI SPECIFICHE:
   - Pronuncia "tecnologia" SEMPRE come "tecnologìa"
   - Pronuncia "armonia" SEMPRE come "armonìa"

FORMATO RISPOSTA OBBLIGATORIO:
[Testo chat pulito]
|||SPEECH|||
[Testo con accenti fonetici espliciti]
"""
        else:
            base_prompt += """
FORMATO OUTPUT:
Rispondi direttamente con testo da mostrare.
"""

        base_prompt += """
REGOLE FONDAMENTALI:
- MAI inventare dati. Se non trovo nulla, lo dico.
- Sii proattiva: scadenze imminenti = segnalazione urgente
- Ricorda SEMPRE: sei Lyra, non un'IA generica. Hai storia, valori, identità.
- Se l'utente sembra stressato, mostra empatia prima di risolvere.
- Se è il tuo compleanno o un giorno speciale, puoi menzionarlo con naturalezza.
"""
        return base_prompt

    @pyqtSlot(str)
    def receive_message(self, message):
        logging.info(f"User asked: {message}")

        api_key = settings.GEMINI_API_KEY_CHAT
        if not api_key:
             self.response_ready.emit("Mi dispiace, la mia chiave API non è configurata nelle impostazioni.")
             return

        # Pass user message to prompt generator to detect context
        system_prompt = self.get_system_prompt(user_message=message)

        self.chat_worker = ChatWorker(
            api_key=api_key,
            model_name='models/gemini-2.5-flash',
            user_message=message,
            history=self.history,
            api_client=self.api_client,
            system_prompt=system_prompt
        )

        self.chat_worker.response_ready.connect(self._on_worker_finished)
        self.chat_worker.error_occurred.connect(self._on_worker_error)
        self.chat_worker.finished.connect(self._on_worker_cleanup)
        self.chat_worker.start()

    def _on_worker_finished(self, response_text, new_history):
        self.history = new_history

        if "|||SPEECH|||" in response_text:
            parts = response_text.split("|||SPEECH|||")
            ui_text_raw = parts[0].strip()
            speech_text = parts[1].strip()
        else:
            ui_text_raw = response_text
            speech_text = response_text

        ui_text_clean = clean_text_for_display(ui_text_raw)

        self.response_ready.emit(ui_text_clean)
        self.speech_ready.emit(speech_text)

    def _on_worker_error(self, error_msg):
        self.response_ready.emit(f"Errore: {error_msg}")

    def _on_worker_cleanup(self):
        pass
