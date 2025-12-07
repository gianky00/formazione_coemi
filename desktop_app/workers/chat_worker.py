import logging
import time
from datetime import date, datetime, timedelta
from PyQt6.QtCore import QThread, pyqtSignal
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

class ChatWorker(QThread):
    """
    Worker thread to handle Gemini API interactions asynchronously.
    Supports Function Calling for 'Omniscience'.
    """
    # Emits response text AND updated history
    response_ready = pyqtSignal(str, list)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_key, model_name, user_message, history, api_client, system_prompt):
        super().__init__()
        self.api_key = api_key
        self.model_name = model_name
        self.user_message = user_message
        self.history = history
        self.api_client = api_client
        self.system_prompt = system_prompt
        self.model = None

    def run(self):
        try:
            if not self.api_key:
                raise ValueError("API Key mancante. Configurala nelle impostazioni.")

            genai.configure(api_key=self.api_key)

            # Define Tools List
            tools_list = [
                self.get_employee_stats,
                self.get_expiring_certificates,
                self.get_employee_details
            ]

            # Configure Model
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                tools=tools_list,
                system_instruction=self.system_prompt
            )

            # Start Chat with History
            chat = self.model.start_chat(history=self.history, enable_automatic_function_calling=True)

            # Send Message
            response = chat.send_message(self.user_message)

            # Emit response text and the updated history (including tool calls)
            self.response_ready.emit(response.text, chat.history)

        except Exception as e:
            logging.error(f"Gemini Worker Error: {e}")
            msg = str(e)
            if "429" in msg:
                msg = "Ho pensato troppo forte. Riprova tra poco (Quota API esaurita)."
            elif "API key" in msg:
                msg = "Chiave API non valida."
            self.error_occurred.emit(msg)

    # --- TOOLS ---

    def get_employee_stats(self):
        """
        Restituisce il numero totale di dipendenti e certificati nel sistema.
        """
        try:
            emps = self.api_client.get_dipendenti_list()
            certs = self.api_client.get("certificati")
            return {
                "total_employees": len(emps) if isinstance(emps, list) else 0,
                "total_certificates": len(certs) if isinstance(certs, list) else 0
            }
        except Exception as e:
            return {"error": str(e)}

    def get_expiring_certificates(self, days_limit: int = 30):
        """
        Restituisce la lista dei certificati in scadenza nei prossimi 'days_limit' giorni.
        Include anche i scaduti.
        """
        try:
            all_certs = self.api_client.get("certificati", params={"validated": "true"})
            if not isinstance(all_certs, list):
                return []

            today = date.today()
            limit_date = today + timedelta(days=int(days_limit))

            results = []
            for c in all_certs:
                expiry_str = c.get("data_scadenza")
                if not expiry_str: continue
                try:
                    expiry = datetime.strptime(expiry_str, "%d/%m/%Y").date()
                    if expiry <= limit_date:
                        status_emoji = "⚠️" if expiry <= today else "📅"
                        results.append(f"{status_emoji} {c.get('nome')} - {c.get('nome_corso')}: Scade il {expiry_str}")
                except Exception: # S5754: Handle exception
                    continue
            return results[:30]
        except Exception as e:
            return {"error": str(e)}

    def get_employee_details(self, name_query: str):
        """
        Cerca un dipendente per nome e restituisce i suoi dettagli e certificati.
        """
        try:
            all_emps = self.api_client.get_dipendenti_list()
            if not isinstance(all_emps, list):
                return "Errore nel recupero dipendenti."

            matches = [e for e in all_emps if name_query.lower() in f"{e.get('nome', '')} {e.get('cognome', '')}".lower()]

            if not matches:
                return f"Nessun dipendente trovato con nome simile a '{name_query}'"

            target = matches[0]
            details = self.api_client.get_dipendente_detail(target['id'])

            summary = {
                "nome": details.get("nome"),
                "cognome": details.get("cognome"),
                "matricola": details.get("matricola"),
                "certificati": []
            }

            for c in details.get("certificati", []):
                 summary["certificati"].append(f"{c.get('nome_corso')}: {c.get('stato_certificato')} ({c.get('data_scadenza')})")

            return summary
        except Exception as e:
            return {"error": str(e)}
