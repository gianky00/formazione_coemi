import logging
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models import Dipendente, Certificato, Corso
from sqlalchemy import select, or_
from datetime import date, timedelta
import google.generativeai as genai

class ChatController(QObject):
    response_ready = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
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

    def get_context_data(self):
        """Fetches relevant context from the database."""
        db = SessionLocal()
        try:
            # Fetch all employees
            stmt_emp = select(Dipendente.nome, Dipendente.cognome, Dipendente.matricola)
            employees = db.execute(stmt_emp).all()
            emp_list = [f"{e.cognome} {e.nome} (Matr: {e.matricola})" for e in employees]

            # Fetch expiring/expired certificates (past 30 days, future 90 days)
            today = date.today()
            start_date = today - timedelta(days=30)
            end_date = today + timedelta(days=90)

            # Using data_scadenza_calcolata
            stmt_cert = select(
                Corso.nome_corso,
                Dipendente.cognome,
                Dipendente.nome,
                Certificato.data_scadenza_calcolata
            ).join(Dipendente, Certificato.dipendente_id == Dipendente.id)\
             .join(Corso, Certificato.corso_id == Corso.id)\
             .where(
                 or_(
                     Certificato.data_scadenza_calcolata.between(start_date, end_date),
                     Certificato.data_scadenza_calcolata < today # Already expired
                 )
             ).order_by(Certificato.data_scadenza_calcolata)

            certs = db.execute(stmt_cert).all()
            cert_list = [f"{c.cognome} {c.nome} - {c.nome_corso}: Scade {c.data_scadenza_calcolata}" for c in certs]

            return {
                "employees": emp_list,
                "certificates": cert_list
            }
        except Exception as e:
            logging.error(f"Error fetching RAG context: {e}")
            return {"employees": [], "certificates": []}
        finally:
            db.close()

    @pyqtSlot(str)
    def receive_message(self, message):
        """Receives message from JS, processes it, and emits response."""
        logging.info(f"User asked: {message}")

        if not self.model:
            # Try setting up again in case key was added later
            self.setup_gemini()
            if not self.model:
                self.response_ready.emit("Mi dispiace, la mia chiave API non è configurata.")
                return

        # Context Injection
        context = self.get_context_data()
        context_str = (
            f"Dati Dipendenti: {', '.join(context['employees'])}\n"
            f"Scadenze/Certificati (Recenti/Futuri): {'; '.join(context['certificates'])}"
        )

        system_prompt = (
            "Il tuo nome è Lyra. Sei l'assistente IA di Intelleo. "
            "Rispondi in modo professionale, conciso e sicuro. "
            f"Usa i seguenti dati contestuali aggiornati per rispondere (se pertinenti): [{context_str}] "
            "Se l'utente chiede qualcosa fuori da questi dati, rispondi basandoti sulla tua conoscenza generale "
            "ma specifica che non è nel database."
        )

        try:
            # We don't maintain history in this simple implementation,
            # but we pass the system prompt as the first part.
            chat = self.model.start_chat(history=[])

            # Gemini Python SDK handles system instructions differently in 1.5/2.0
            # but putting it in the message or history usually works.
            # Best practice for flash/pro is often a system instruction arg if supported,
            # or just prepending it.

            full_prompt = f"{system_prompt}\n\nUtente: {message}"

            response = chat.send_message(full_prompt)
            self.response_ready.emit(response.text)
        except Exception as e:
            logging.error(f"Gemini API Error: {e}")
            self.response_ready.emit("Mi dispiace, ho riscontrato un errore nel processare la tua richiesta.")
