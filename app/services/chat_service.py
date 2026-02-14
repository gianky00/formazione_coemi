import logging
from datetime import date
from typing import Any

import google.generativeai as genai
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Certificato, Dipendente, User

logger = logging.getLogger(__name__)


class ChatService:
    """
    Service for AI Chat functionalities using RAG (Retrieval-Augmented Generation).
    """

    def get_rag_context(self, db: Session, user: User, query: str = "") -> str:
        """
        Retrieves relevant database context based on the user's query.
        """
        from app.services import certificate_logic

        context_parts = []

        # 1. Global Stats
        emp_count = db.query(Dipendente).count()
        cert_count = db.query(Certificato).count()
        context_parts.append("Statistiche Globali:")
        context_parts.append(f"- Totale Dipendenti: {emp_count}")
        context_parts.append(f"- Totale Documenti: {cert_count}")

        # 2. Identify if the user is asking about a specific employee
        # Basic smart search: extract words from query and check for matches
        import re

        clean_query = re.sub(r"[^\w\s]", "", query)
        words = [w for w in clean_query.split() if len(w) > 3]
        if words:
            # Search for employees matching those words
            emp_filters = []
            for word in words:
                emp_filters.append(Dipendente.nome.ilike(f"%{word}%"))
                emp_filters.append(Dipendente.cognome.ilike(f"%{word}%"))

            employees = db.query(Dipendente).filter(or_(*emp_filters)).limit(3).all()

            if employees:
                context_parts.append("\nDati dipendenti trovati nel DB:")
                for emp in employees:
                    # Privacy masking for non-admins if needed, here we use initials for the test
                    masked_name = f"{emp.cognome} {emp.nome[0]}." if emp.nome else emp.cognome
                    emp_info = f"- {masked_name} (Matricola: {emp.matricola or 'N/D'})"
                    context_parts.append(emp_info)

                    # Get their certificates
                    certs = (
                        db.query(Certificato)
                        .filter(Certificato.dipendente_id == emp.id)
                        .order_by(Certificato.data_scadenza_calcolata.asc())
                        .limit(5)
                        .all()
                    )
                    for cert in certs:
                        categoria = cert.corso.categoria_corso if cert.corso else "ALTRO"
                        stato = certificate_logic.get_certificate_status(db, cert)
                        context_parts.append(
                            f"  * Certificato: {cert.corso.nome_corso if cert.corso else 'N/D'} ({categoria}) - "
                            f"Scadenza: {cert.data_scadenza_calcolata} - Stato: {stato}"
                        )

        # 3. Summary of expired (always useful)
        expired_count = (
            db.query(Certificato).filter(Certificato.data_scadenza_calcolata < date.today()).count()
        )
        context_parts.append(f"\nDOCUMENTI SCADUTI (Top {min(expired_count, 5)}):")
        # Add a few examples if needed...

        # 4. General System Context
        context_parts.append(f"\nUtente attuale: {user.username} (Admin: {user.is_admin})")

        return "\n".join(context_parts)

    def chat_with_intelleo(self, message: str, history: list[dict[str, Any]], context: str) -> str:
        """
        Sends message to Gemini AI with context and returns the response.
        """
        api_key = settings.GEMINI_API_KEY_CHAT or settings.GEMINI_API_KEY_ANALYSIS
        if not api_key:
            return "Errore: Chiave API Chat non configurata nelle impostazioni."

        try:
            genai.configure(api_key=api_key)

            system_prompt = f"""
            Sei 'Intelleo', l'assistente AI avanzato di COEMI per la gestione della formazione.
            Il tuo compito è aiutare l'utente a navigare tra i dati dei certificati e dei dipendenti.

            REGOLE:
            1. Usa i dati forniti nel CONTESTO qui sotto per rispondere in modo preciso.
            2. Se non conosci la risposta basandoti sul contesto, dillo chiaramente.
            3. Sii professionale, conciso e cordiale.
            4. Se rilevi criticità (es. certificati scaduti), evidenziale.

            CONTESTO DATABASE:
            {context}
            """

            # Combine system prompt with the message or use it as instructions
            # For simplicity with start_chat, we can prepend it to the history or first message
            # Better: use the system_instruction parameter if supported by the model/SDK version
            # here we'll use a standard chat session

            # Gemini history format requires 'role' and 'parts'
            gemini_history = [
                {"role": "user" if h["role"] == "user" else "model", "parts": [h["content"]]}
                for h in history
            ]

            # Prepend system context as a 'user' message or use GenerativeModel(system_instruction=...)
            # Since we are using an instance, we recreate it with instruction for better results
            model_with_instr = genai.GenerativeModel(
                "models/gemini-2.0-flash", system_instruction=system_prompt
            )

            chat_session = model_with_instr.start_chat(history=gemini_history)
            response = chat_session.send_message(message)

            return str(response.text)

        except Exception as e:
            logger.error(f"AI Chat error: {e}", exc_info=True)
            return f"Spiacente, si è verificato un errore durante la chat: {e!s}"


chat_service: ChatService = ChatService()
