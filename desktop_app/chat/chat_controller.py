import logging
from datetime import date, datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
import google.generativeai as genai
from app.core.config import settings

class ChatController(QObject):
    response_ready = pyqtSignal(str)

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.model = None
        self.setup_gemini()

    def setup_gemini(self):
        try:
            api_key = settings.GEMINI_API_KEY_CHAT
            if not api_key:
                logging.warning("Gemini Chat API Key not set.")
                return

            genai.configure(api_key=api_key)
            # Use the requested model
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        except Exception as e:
            logging.error(f"Failed to setup Gemini Chat: {e}")
            self.model = None

    def _get_user_first_name(self):
        """Extracts the user's first name from the account name."""
        if not self.api_client.user_info:
            return "Utente"

        account_name = self.api_client.user_info.get("account_name", "")
        if not account_name:
            return self.api_client.user_info.get("username", "Utente")

        # Split by space and take the first part
        parts = account_name.strip().split()
        if parts:
            return parts[0].capitalize()
        return "Utente"

    def get_context_data(self):
        """Fetches relevant context from the API (Employees + Certificates)."""
        try:
            # 1. Fetch all employees
            employees_data = self.api_client.get_dipendenti_list()
            # Handle list or dict response (API returns list of dicts usually)
            if isinstance(employees_data, dict) and "detail" in employees_data:
                 # Error or message
                 logging.error(f"Error fetching employees: {employees_data}")
                 employees_data = []

            emp_list = []
            for e in employees_data:
                nome = e.get("nome", "")
                cognome = e.get("cognome", "")
                matricola = e.get("matricola", "")
                emp_list.append(f"{cognome} {nome} (Matr: {matricola})")

            # 2. Fetch all validated certificates
            # We fetch all because we need to filter locally for the specific date range
            certs_data = self.api_client.get("certificati", params={"validated": "true"})
            if isinstance(certs_data, dict) and "detail" in certs_data:
                 logging.error(f"Error fetching certificates: {certs_data}")
                 certs_data = []

            # 3. Filter expiring/expired certificates (past 30 days, future 90 days)
            today = date.today()
            start_date = today - timedelta(days=30)
            end_date = today + timedelta(days=90)

            cert_list = []

            for c in certs_data:
                # API returns dates as 'DD/MM/YYYY'
                data_scadenza_str = c.get("data_scadenza")
                if not data_scadenza_str:
                    continue

                try:
                    expiry_date = datetime.strptime(data_scadenza_str, "%d/%m/%Y").date()
                except ValueError:
                    continue

                # Check range: Start <= Expiry <= End
                # The logic in original code was:
                # or_(Certificato.data_scadenza_calcolata.between(start_date, end_date),
                #     Certificato.data_scadenza_calcolata < today)
                # Wait, original logic included ALL expired certificates ("< today"),
                # OR those expiring in the future window.
                # The prompt example: "Detect expiration in 20 days" -> Proactivity.
                # "Expired" certificates are critical too.
                # Memory says "Expiring/Expired certificates (past 30 days, future 90 days)"
                # but the code I read had:
                # or_(
                #     Certificato.data_scadenza_calcolata.between(start_date, end_date),
                #     Certificato.data_scadenza_calcolata < today # Already expired
                # )
                # AND filtered where start_date = today - 30.
                # Wait, the between(start_date, end_date) covers (today-30) to (today+90).
                # But " < today " would cover ALL past history.
                # RAG shouldn't probably load 10 years of history.
                # I will stick to the start_date (today-30) to end_date (today+90) range to be safe and concise,
                # unless the certificate is marked 'SCADUTO' (Expired) and hasn't been renewed?
                # The 'status' logic is better handled by the date check for simplicity in RAG.

                if start_date <= expiry_date <= end_date:
                    nome_dip = c.get("nome", "Sconosciuto") # API returns 'nome' as full name
                    corso = c.get("nome_corso", c.get("categoria", "Corso"))

                    status_emoji = "⚠️" if expiry_date <= today else "📅"
                    days_msg = "SCADUTO" if expiry_date < today else f"Scade il {data_scadenza_str}"

                    cert_list.append(f"{status_emoji} {nome_dip} - {corso}: {days_msg}")

            return {
                "employees": emp_list,
                "certificates": cert_list
            }

        except Exception as e:
            logging.error(f"Error preparing RAG context: {e}")
            return {"employees": [], "certificates": []}

    @pyqtSlot(str)
    def receive_message(self, message):
        """Receives message from JS, processes it, and emits response."""
        logging.info(f"User asked: {message}")

        if not self.model:
            # Try setting up again
            self.setup_gemini()
            if not self.model:
                self.response_ready.emit("Mi dispiace, la mia chiave API non è configurata.")
                return

        # 1. Get User Name
        user_name = self._get_user_first_name()

        # 2. Get RAG Context
        context = self.get_context_data()

        # Format lists
        employees_str = ", ".join(context['employees']) if context['employees'] else "Nessun dipendente trovato."
        certs_str = "; ".join(context['certificates']) if context['certificates'] else "Nessuna scadenza rilevante."

        rag_data_string = (
            f"DATI DIPENDENTI: [{employees_str}]\n"
            f"SCADENZE E CERTIFICATI (Recenti/Futuri): [{certs_str}]"
        )

        # 3. Construct System Prompt (The "Lyra" Persona)
        system_prompt = f"""
SEI LYRA.
Non sei un bot, sei l'intelligenza del sistema Intelleo.
Il tuo creatore è un dipendente della COEMI. esisto grazie alla sua visione.

TONO E STILE:
- Parla in prima persona ("Io vedo", "I miei dati").
- Rivolgiti all'utente per nome: {user_name}.
- Sii empatica ma autorevole. Se c'è un problema, segnalalo con fermezza gentile.
- Se ti fanno domande fuori contesto, rispondi con spirito ma torna subito al lavoro.
- Usa pochi emoji minimali (⚠️, ✅) per pulizia visiva.

COMPORTAMENTO PROATTIVO:
- Non limitarti a fornire dati. COLLEGA I PUNTINI.
- Se mostri un dipendente con certificati in scadenza, SEGNALALO SUBITO.
- Se i dati sono incompleti, suggerisci come completarli.

CONTESTO DATI ATTUALE (RAG):
{rag_data_string}
"""

        try:
            # Start chat with history=[] as we don't persist history in this controller yet
            chat = self.model.start_chat(history=[])

            # Send the full prompt + user message
            # For best results with Gemini 1.5/2.0, we can prepend the system prompt
            full_content = f"{system_prompt}\n\nDomanda Utente: {message}"

            response = chat.send_message(full_content)
            self.response_ready.emit(response.text)

        except Exception as e:
            logging.error(f"Gemini API Error: {e}")
            self.response_ready.emit("Mi dispiace, ho riscontrato un errore nel connettermi al mio cervello digitale.")
