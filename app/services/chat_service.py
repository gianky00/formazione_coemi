import logging
import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import date, timedelta
from typing import List, Dict, Any
from app.core.config import settings
from app.db.models import Certificato, Dipendente, User
from app.services.certificate_logic import get_bulk_certificate_statuses

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        # We delay configuration to runtime to handle dynamic key updates and multi-key conflicts
        pass

    def get_rag_context(self, db: Session, user: User) -> str:
        """
        Retrieves context from the database to ground the AI.
        """
        today = date.today()
        threshold_date = today + timedelta(days=settings.ALERT_THRESHOLD_DAYS)

        # 1. Statistics
        total_certs = db.query(Certificato).count()
        total_employees = db.query(Dipendente).count()
        
        # 2. Expiring / Expired
        # Fetching certificates that are expired or expiring soon
        relevant_certs = db.query(Certificato).join(Dipendente, isouter=True).filter(
            or_(
                Certificato.data_scadenza_calcolata <= threshold_date,
                Certificato.data_scadenza_calcolata == None
            )
        ).all()

        expiring_list = []
        expired_list = []
        
        statuses = get_bulk_certificate_statuses(db, relevant_certs)
        
        for cert in relevant_certs:
            status = statuses.get(cert.id, "attivo")
            emp_name = cert.dipendente.nome if cert.dipendente else (cert.nome_dipendente_raw or "Sconosciuto")
            
            # Safe access to calculated date
            date_str = cert.data_scadenza_calcolata or "N/A"
            info = f"- {emp_name}: {cert.corso.nome_corso} ({status.upper()}, Scade: {date_str})"
            
            if status == "scaduto":
                expired_list.append(info)
            elif status == "in_scadenza":
                expiring_list.append(info)

        # 3. Orphans (Issues)
        orphans = db.query(Certificato).filter(Certificato.dipendente_id == None).all()
        orphans_list = [f"- {c.corso.nome_corso} (Rilevato: {c.nome_dipendente_raw})" for c in orphans]

        # Construct Context String
        context = f"""
DATI DI CONTESTO ATTUALI (Aggiornati al {today.strftime('%d/%m/%Y')}):

UTENTE ATTUALE: {user.username} ({user.account_name or 'Nessun Nome Account'})

STATISTICHE SISTEMA:
- Totale Dipendenti: {total_employees}
- Totale Documenti: {total_certs}

DOCUMENTI SCADUTI ({len(expired_list)}):
{chr(10).join(expired_list[:20])} 
{'... (altri omessi)' if len(expired_list) > 20 else ''}

DOCUMENTI IN SCADENZA ({len(expiring_list)}):
{chr(10).join(expiring_list[:20])}
{'... (altri omessi)' if len(expiring_list) > 20 else ''}

DOCUMENTI DA VALIDARE/ORFANI ({len(orphans_list)}):
{chr(10).join(orphans_list[:20])}
{'... (altri omessi)' if len(orphans_list) > 20 else ''}
"""
        return context

    def chat_with_intelleo(self, message: str, history: List[Dict[str, str]], context: str) -> str:
        api_key = settings.GEMINI_API_KEY_CHAT

        if not api_key or "obf:" in api_key: # Simple check if reveal failed or empty
             # If reveal failed, it might still return the string, but settings property handles reveal.
             # If the string is empty or invalid format, we can't proceed.
             if not api_key:
                 return "Errore: Chiave API Chat non configurata."

        try:
            # Re-configure global genai with Chat Key
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('models/gemini-2.5-flash')
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Flash: {e}")
            return f"Errore inizializzazione AI: {e}"

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

        try:
            chat_session = model.start_chat(history=gemini_history)
            final_prompt = f"{system_prompt}\n\nUTENTE: {message}"
            response = chat_session.send_message(final_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Chat Error: {e}")
            # More descriptive error for debugging
            return f"Errore durante la generazione della risposta: {e}"

chat_service = ChatService()
