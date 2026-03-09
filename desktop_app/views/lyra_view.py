import re
import threading
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QScrollArea, QFrame, QFileDialog, QMessageBox,
    QSizePolicy, QSpacerItem, QTextBrowser
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QSize
from PySide6.QtGui import QFont, QTextCursor, QColor

class LyraView(QWidget):
    QUICK_PROMPTS = [
        {"icon": "📊", "label": "Riepilogo", "prompt": "Fammi un riepilogo completo della situazione attuale: certificati scaduti, in scadenza, dipendenti con dati mancanti e suggerimenti per migliorare.", "color": "#3B82F6"},
        {"icon": "⚠", "label": "Scadenze", "prompt": "Quali certificati scadranno nei prossimi 30 giorni? Elencali per priorita con i nomi dei dipendenti.", "color": "#F59E0B"},
        {"icon": "📅", "label": "Piano Formazione", "prompt": "Suggerisci un piano di formazione ottimale per i prossimi 3 mesi, raggruppando i dipendenti per categoria di corso in scadenza.", "color": "#10B981"},
        {"icon": "👥", "label": "Dipendenti Incompleti", "prompt": "Quali dipendenti hanno dati anagrafici incompleti? Elenca nome, cognome e quali campi mancano.", "color": "#8B5CF6"},
        {"icon": "📈", "label": "Statistiche", "prompt": "Mostrami statistiche dettagliate: totale certificati per categoria, percentuale scaduti, media giorni alla scadenza, dipendenti piu a rischio.", "color": "#06B6D4"},
        {"icon": "🔍", "label": "Audit", "prompt": "Analizza gli ultimi log di audit e segnala eventuali anomalie o pattern sospetti nelle operazioni.", "color": "#EF4444"},
        {"icon": "📝", "label": "Report", "prompt": "Genera un report completo da inviare alla direzione con lo stato della formazione aziendale.", "color": "#EC4899"},
        {"icon": "💡", "label": "Suggerimenti", "prompt": "Quali azioni immediate mi consigli per migliorare la gestione dei certificati? Dai priorita ai problemi piu urgenti.", "color": "#F97316"},
    ]

    chat_signal = Signal(str, bool)
    loading_signal = Signal(bool)

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.history = []
        self.is_loading = False
        self.setStyleSheet("background-color: #F3F4F6;")
        
        self.setup_ui()
        self.chat_signal.connect(self._on_response_received)
        self.loading_signal.connect(self._set_loading_state)
        self._show_welcome_message()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: white; border-radius: 8px;")
        s_layout = QVBoxLayout(sidebar)
        
        s_header = QLabel("✨ Lyra IA")
        s_header.setAlignment(Qt.AlignCenter)
        s_header.setStyleSheet("background-color: #1E3A8A; color: white; font-weight: bold; font-size: 16px; border-radius: 4px; padding: 10px;")
        s_layout.addWidget(s_header)

        lbl_quick = QLabel("Azioni Rapide:")
        lbl_quick.setStyleSheet("font-weight: bold; color: #1F2937; margin-top: 10px;")
        s_layout.addWidget(lbl_quick)
        
        # Scroll Area for Quick Prompts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        for q in self.QUICK_PROMPTS:
            btn = QPushButton(f"{q['icon']} {q['label']}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {q['color']}; color: white; font-weight: bold;
                    text-align: left; padding: 10px; border-radius: 4px; border: none;
                }}
                QPushButton:hover {{ background-color: {self._lighten_color(q['color'])}; }}
            """)
            btn.clicked.connect(lambda checked=False, p=q['prompt']: self._send_prompt(p))
            scroll_layout.addWidget(btn)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        s_layout.addWidget(scroll)

        btn_new = QPushButton("Nuova Conversazione")
        btn_new.setStyleSheet("background-color: #6B7280; color: white; padding: 10px; border-radius: 4px;")
        btn_new.clicked.connect(self._clear_chat)
        s_layout.addWidget(btn_new)

        main_layout.addWidget(sidebar)

        # Chat Area
        chat_container = QWidget()
        c_layout = QVBoxLayout(chat_container)
        
        # Chat Header
        c_header = QFrame()
        c_header.setFixedHeight(50)
        c_header.setStyleSheet("background-color: white; border-radius: 8px;")
        ch_layout = QHBoxLayout(c_header)
        ch_layout.addWidget(QLabel("Chat con Lyra"))
        ch_layout.addStretch()
        btn_export = QPushButton("Esporta")
        btn_export.clicked.connect(self._export_chat)
        ch_layout.addWidget(btn_export)
        c_layout.addWidget(c_header)

        # History Browser
        self.txt_history = QTextBrowser()
        self.txt_history.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #D1D5DB; padding: 10px;")
        self.txt_history.setOpenExternalLinks(True)
        c_layout.addWidget(self.txt_history)

        # Input Area
        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #D1D5DB;")
        i_layout = QVBoxLayout(input_frame)
        
        self.entry_msg = QTextEdit()
        self.entry_msg.setPlaceholderText("Scrivi qui la tua domanda...")
        self.entry_msg.setFixedHeight(80)
        self.entry_msg.setStyleSheet("border: none; padding: 5px;")
        i_layout.addWidget(self.entry_msg)
        
        btn_row = QHBoxLayout()
        self.lbl_loading = QLabel("")
        self.lbl_loading.setStyleSheet("color: #6B7280; font-style: italic;")
        btn_row.addWidget(self.lbl_loading)
        btn_row.addStretch()
        self.btn_send = QPushButton("Invia")
        self.btn_send.setFixedWidth(100)
        self.btn_send.setStyleSheet("background-color: #1E3A8A; color: white; font-weight: bold; padding: 8px;")
        self.btn_send.clicked.connect(self._send_current_msg)
        btn_row.addWidget(self.btn_send)
        i_layout.addLayout(btn_row)
        
        c_layout.addWidget(input_frame)
        main_layout.addWidget(chat_container)

    def _lighten_color(self, hex):
        h = hex.lstrip('#')
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        return '#{:02x}{:02x}{:02x}'.format(*[min(255, c + 40) for c in rgb])

    def _show_welcome_message(self):
        welcome = "Ciao! Sono Lyra, il tuo assistente virtuale.<br>Posso aiutarti con l'analisi dei certificati, statistiche e suggerimenti."
        self._append_message("Lyra", welcome, "#059669")

    def _append_message(self, sender, text, color):
        timestamp = datetime.now().strftime("%H:%M")
        html = f'<div style="margin-bottom: 15px;">'
        html += f'<b style="color: {color}; font-size: 14px;">{sender}</b> <small style="color: #9CA3AF;">({timestamp})</small><br>'
        html += f'<div style="margin-top: 5px; padding: 12px; background-color: #F9FAFB; border-radius: 8px; border: 1px solid #E5E7EB; line-height: 1.5;">{text}</div>'
        html += '</div>'
        self.txt_history.append(html)
        self.txt_history.moveCursor(QTextCursor.End)

    def _send_current_msg(self):
        msg = self.entry_msg.toPlainText().strip()
        if msg: self._send_prompt(msg)

    def _send_prompt(self, prompt):
        if self.is_loading: return
        self.entry_msg.clear()
        self._append_message("Tu", prompt, "#1E3A8A")
        self.loading_signal.emit(True)
        threading.Thread(target=self._chat_worker, args=(prompt,), daemon=True).start()

    @Slot(bool)
    def _set_loading_state(self, loading):
        self.is_loading = loading
        self.btn_send.setEnabled(not loading)
        self.lbl_loading.setText("Lyra sta pensando..." if loading else "")

    def _build_context(self):
        """Costruisce il contesto completo dai dati reali (Ripristinato)."""
        context_parts = []
        try:
            certs = self.controller.api_client.get("certificati", params={"validated": "true"})
            pending = self.controller.api_client.get("certificati", params={"validated": "false"})
            
            today = datetime.now().date()
            expired, exp30, exp60, active = 0, 0, 0, 0
            for c in certs:
                scad = c.get("data_scadenza")
                if scad and scad.lower() not in ["none", "nessuna"]:
                    try:
                        dt = datetime.strptime(scad, "%d/%m/%Y").date()
                        days = (dt - today).days
                        if days < 0: expired += 1
                        elif days <= 30: exp30 += 1
                        elif days <= 60: exp60 += 1
                        else: active += 1
                    except: active += 1
                else: active += 1
            
            context_parts.append(f"CERTIFICATI: {len(certs)} validati, {len(pending)} da convalidare")
            context_parts.append(f"STATO: {expired} scaduti, {exp30} in scadenza (30gg), {exp60} in scadenza (60gg), {active} attivi")
            
            dipendenti = self.controller.api_client.get_dipendenti_list()
            context_parts.append(f"DIPENDENTI: {len(dipendenti)} totali")
        except Exception as e:
            context_parts.append(f"Errore recupero dati contesto: {e}")
        return "\n".join(context_parts)

    def _chat_worker(self, message):
        try:
            context = self._build_context()
            enhanced_message = f"CONTESTO SISTEMA:\n{context}\n\nDOMANDA UTENTE: {message}\n\nRispondi in italiano con markdown."
            response = self.controller.api_client.send_chat_message(enhanced_message, history=self.history[-10:])
            reply = response.get("response", "Errore nella risposta.")
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "model", "content": reply})
            self.chat_signal.emit(reply, False)
        except Exception as e:
            self.chat_signal.emit(str(e), True)
        finally:
            self.loading_signal.emit(False)

    @Slot(str, bool)
    def _on_response_received(self, text, is_error):
        color = "red" if is_error else "#059669"
        formatted_html = self._markdown_to_html(text)
        self._append_message("Lyra", formatted_html, color)

    def _markdown_to_html(self, text):
        """Converte markdown semplificato in HTML per QTextBrowser (Ripristinato e Migliorato)."""
        html = text
        # Tabelle
        if "|" in html:
            lines = html.split("\n")
            new_lines = []
            in_table = False
            table_html = '<table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0;">'
            for line in lines:
                if "|" in line:
                    if not in_table:
                        in_table = True
                    cells = [c.strip() for c in line.strip("|").split("|")]
                    if all(re.match(r"^[-:]+$", c) for c in cells): continue # skip separator
                    table_html += "<tr>" + "".join(f'<td style="padding: 5px; border: 1px solid #ddd;">{c}</td>' for c in cells) + "</tr>"
                else:
                    if in_table:
                        table_html += "</table>"
                        new_lines.append(table_html)
                        table_html = '<table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0;">'
                        in_table = False
                    new_lines.append(line)
            if in_table: new_lines.append(table_html + "</table>")
            html = "\n".join(new_lines)

        # Grassetti, Elenchi, Newlines
        html = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", html)
        html = re.sub(r"### (.*)", r"<h3 style='color: #1E3A8A;'>\1</h3>", html)
        html = re.sub(r"- (.*)", r"• \1", html)
        html = html.replace("\n", "<br>")
        return html

    def _clear_chat(self):
        self.txt_history.clear()
        self.history = []
        self._show_welcome_message()

    def _export_chat(self):
        path, _ = QFileDialog.getSaveFileName(self, "Esporta Chat", "conversazione_lyra.html", "HTML Files (*.html);;Text Files (*.txt)")
        if path:
            try:
                content = self.txt_history.toHtml() if path.endswith(".html") else self.txt_history.toPlainText()
                with open(path, "w", encoding="utf-8") as f: f.write(content)
                QMessageBox.information(self, "Esportato", "Conversazione salvata.")
            except Exception as e: QMessageBox.critical(self, "Errore", str(e))

    def refresh_data(self):
        pass
