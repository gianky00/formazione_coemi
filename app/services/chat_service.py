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

    def _search_employee_by_name(self, db: Session, search_name: str) -> str:
        """Search for employees by name (case-insensitive, partial match)."""
        if not search_name or len(search_name) < 2:
            return ""
        
        search_terms = search_name.upper().split()
        
        # Build query with OR conditions for flexible matching
        conditions = []
        for term in search_terms:
            conditions.append(Dipendente.cognome.ilike(f"%{term}%"))
            conditions.append(Dipendente.nome.ilike(f"%{term}%"))
        
        employees = db.query(Dipendente).filter(or_(*conditions)).limit(10).all()
        
        if not employees:
            return ""
        
        result = []
        for emp in employees:
            # Get this employee's certificates
            certs = db.query(Certificato).filter(Certificato.dipendente_id == emp.id).all()
            statuses = get_bulk_certificate_statuses(db, certs)
            
            cert_summary = []
            for cert in certs[:5]:  # Limit to 5 certs per employee
                status = statuses.get(cert.id, "attivo")
                scad = cert.data_scadenza_calcolata.strftime('%d/%m/%Y') if cert.data_scadenza_calcolata else "N/A"
                cert_summary.append(f"  - {cert.corso.nome_corso}: {status.upper()} (Scade: {scad})")
            
            emp_info = f"DIPENDENTE: {emp.cognome} {emp.nome}"
            if emp.matricola:
                emp_info += f" (Matricola: {emp.matricola})"
            if emp.data_nascita:
                emp_info += f" - Nato: {emp.data_nascita.strftime('%d/%m/%Y')}"
            
            if cert_summary:
                emp_info += f"\nCertificati ({len(certs)} totali):\n" + "\n".join(cert_summary)
            else:
                emp_info += "\n  Nessun certificato registrato."
            
            result.append(emp_info)
        
        return "\n\n".join(result)

    def get_rag_context(self, db: Session, user: User, user_message: str = "") -> str:
        """
        Retrieves context from the database to ground the AI.
        Optimized for performance and privacy.
        If user_message contains names, search for specific employees.
        """
        today = date.today()
        threshold_date = today + timedelta(days=settings.ALERT_THRESHOLD_DAYS)

        total_certs = db.query(func.count(Certificato.id)).scalar()
        total_employees = db.query(func.count(Dipendente.id)).scalar()
        
        # Check if user is asking about a specific employee
        employee_search_result = ""
        search_keywords = ["informazioni su", "info su", "cerca", "mostrami", "dimmi", "chi è", "chi e'"]
        for keyword in search_keywords:
            if keyword in user_message.lower():
                # Extract the name after the keyword
                idx = user_message.lower().find(keyword)
                potential_name = user_message[idx + len(keyword):].strip()
                # Clean up the name
                potential_name = potential_name.replace("?", "").replace("!", "").strip()
                if potential_name:
                    employee_search_result = self._search_employee_by_name(db, potential_name)
                break
        
        # Also try to match any capitalized words that could be names
        if not employee_search_result:
            import re
            # Look for sequences of 2+ capitalized words
            name_pattern = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', user_message)
            if name_pattern:
                for potential_name in name_pattern:
                    result = self._search_employee_by_name(db, potential_name)
                    if result:
                        employee_search_result = result
                        break
            
            # Also try lowercase patterns that might be names
            if not employee_search_result:
                words = user_message.split()
                if len(words) >= 2:
                    # Try combinations of adjacent words
                    for i in range(len(words) - 1):
                        potential_name = f"{words[i]} {words[i+1]}"
                        if len(potential_name) > 3:
                            result = self._search_employee_by_name(db, potential_name)
                            if result:
                                employee_search_result = result
                                break
        
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

        context = f"""
DATI DI CONTESTO ATTUALI (Aggiornati al {today.strftime('%d/%m/%Y')}):

UTENTE ATTUALE: {user.username}

STATISTICHE SISTEMA:
- Totale Dipendenti: {total_employees}
- Totale Documenti: {total_certs}
"""
        
        if employee_search_result:
            context += f"""
RISULTATO RICERCA DIPENDENTE:
{employee_search_result}
"""
        
        context += f"""
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
        return context

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
