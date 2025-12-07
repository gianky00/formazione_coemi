import logging
import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import date, timedelta
from typing import List, Dict, Any
from app.core.config import settings
from app.core.ai_lock import ai_global_lock
from app.db.models import Certificato, Dipendente, User
from app.services.certificate_logic import get_bulk_certificate_statuses

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        # S1186: Empty method implementation
        # Service initialization logic if needed
        pass

    def _format_cert_info(self, cert, status):
        """Helper to format certificate info with privacy masking."""
        emp_name = cert.dipendente.nome if cert.dipendente else (cert.nome_dipendente_raw or "Sconosciuto")
        parts = emp_name.split()
        masked_name = f"{parts[0]} {parts[1][0]}." if len(parts) > 1 else emp_name
        date_str = cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else "N/A"
        return f"- {masked_name}: {cert.corso.nome_corso} ({status.upper()}, Scade: {date_str})"

    def _get_relevant_certs(self, db, threshold_date):
        return db.query(Certificato).join(Dipendente, isouter=True).filter(
            or_(
                Certificato.data_scadenza_calcolata <= threshold_date,
                Certificato.data_scadenza_calcolata == None
            )
        ).limit(50).all()

    def get_rag_context(self, db: Session, user: User) -> str:
        """
        Retrieves context from the database to ground the AI.
        Optimized for performance and privacy.
        """
        # S3776: Refactored to reduce complexity
        today = date.today()
        threshold_date = today + timedelta(days=settings.ALERT_THRESHOLD_DAYS)

        total_certs = db.query(func.count(Certificato.id)).scalar()
        total_employees = db.query(func.count(Dipendente.id)).scalar()
        
        relevant_certs = self._get_relevant_certs(db, threshold_date)
        statuses = get_bulk_certificate_statuses(db, relevant_certs)

        expiring_list = []
        expired_list = []
        
        for cert in relevant_certs:
            status = statuses.get(cert.id, "attivo")
            info = self._format_cert_info(cert, status)
            
            if status == "scaduto":
                expired_list.append(info)
            elif status == "in_scadenza":
                expiring_list.append(info)

        orphans = db.query(Certificato).filter(Certificato.dipendente_id == None).limit(20).all()
        orphans_list = []
        for c in orphans:
            raw = c.nome_dipendente_raw or "Sconosciuto"
            parts = raw.split()
            masked_raw = f"{parts[0]} {parts[1][0]}." if len(parts) > 1 else raw
            orphans_list.append(f"- {c.corso.nome_corso} (Rilevato: {masked_raw})")

        return f"""
DATI DI CONTESTO ATTUALI (Aggiornati al {today.strftime('%d/%m/%Y')}):

UTENTE ATTUALE: {user.username}

STATISTICHE SISTEMA:
- Totale Dipendenti: {total_employees}
- Totale Documenti: {total_certs}

DOCUMENTI SCADUTI (Top {len(expired_list)}):
{chr(10).join(expired_list[:20])}
{'... (altri omessi)' if len(expired_list) > 20 else ''}

DOCUMENTI IN SCADENZA (Top {len(expiring_list)}):
{chr(10).join(expiring_list[:20])}
{'... (altri omessi)' if len(expiring_list) > 20 else ''}

DOCUMENTI DA VALIDARE/ORFANI (Top {len(orphans_list)}):
{chr(10).join(orphans_list)}
{'... (altri omessi)' if len(orphans) > 20 else ''}
"""

    def chat_with_intelleo(self, message: str, history: List[Dict[str, str]], context: str) -> str:
        api_key = settings.GEMINI_API_KEY_CHAT

        # S1066: Merged if
        if not api_key or "obf:" in api_key:
             return "Errore: Chiave API Chat non configurata."

        # Bug 2 Fix: Lock the configuration
        with ai_global_lock:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('models/gemini-2.5-flash')

                system_prompt = f"""
Sei Intelleo, l'assistente AI avanzato per la sicurezza sul lavoro di COEMI.
Il tuo compito è assistere l'utente nella gestione delle scadenze e dei documenti.

LINEE GUIDA:
1. Rispondi SOLO basandoti sui DATI DI CONTESTO forniti. Se non sai una cosa, dillo.
2. Sii professionale, conciso e proattivo.
3. Se ci sono documenti scaduti, suggerisci di rinnovarli urgentemente.
4. Se ci sono documenti orfani, suggerisci di andare nella sezione 'Convalida Dati'.
5. Parla in italiano perfetto.

{context}
"""

                gemini_history = []
                for msg in history:
                    role = 'user' if msg.get('role') == 'user' else 'model'
                    gemini_history.append({'role': role, 'parts': [msg.get('content', '')]})

                chat_session = model.start_chat(history=gemini_history)
                final_prompt = f"{system_prompt}\n\nUTENTE: {message}"
                response = chat_session.send_message(final_prompt)
                return response.text

            except Exception as e:
                logger.error(f"Chat Error: {e}")
                return f"Errore durante la generazione della risposta: {e}"

chat_service = ChatService()
