import threading
from datetime import datetime
from typing import ClassVar

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class LyraView(QWidget):
    QUICK_PROMPTS: ClassVar[list[dict[str, str]]] = [
        {
            "icon": "📊",
            "label": "Riepilogo",
            "prompt": "Fammi un riepilogo completo della situazione attuale...",
            "color": "#3B82F6",
        },
        {
            "icon": "⚠",
            "label": "Scadenze",
            "prompt": "Quali certificati scadranno nei prossimi 30 giorni?...",
            "color": "#F59E0B",
        },
        {
            "icon": "📅",
            "label": "Piano",
            "prompt": "Suggerisci un piano di formazione...",
            "color": "#10B981",
        },
        {
            "icon": "👥",
            "label": "Incompleti",
            "prompt": "Quali dipendenti hanno dati incompleti?...",
            "color": "#8B5CF6",
        },
        {
            "icon": "📈",
            "label": "Statistiche",
            "prompt": "Mostrami statistiche dettagliate...",
            "color": "#06B6D4",
        },
        {
            "icon": "🔍",
            "label": "Audit",
            "prompt": "Analizza gli ultimi log di audit...",
            "color": "#EF4444",
        },
        {
            "icon": "📝",
            "label": "Report",
            "prompt": "Genera un report completo...",
            "color": "#EC4899",
        },
        {
            "icon": "💡",
            "label": "Consigli",
            "prompt": "Quali azioni immediate consigli?...",
            "color": "#F97316",
        },
    ]

    chat_signal = Signal(str, bool)
    loading_signal = Signal(bool)

    def __init__(self, controller):
        super().__init__(controller)
        self.controller, self.history, self.is_loading = controller, [], False
        self.setup_ui()
        self.chat_signal.connect(self._on_response_received)
        self.loading_signal.connect(self._set_loading_state)
        self._show_welcome_message()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("SidebarFrame")
        sidebar.setFixedWidth(220)
        s_layout = QVBoxLayout(sidebar)

        s_header = QLabel("✨ Lyra IA")
        s_header.setObjectName("HeaderFrame")  # reusing header style
        s_header.setAlignment(Qt.AlignCenter)
        s_header.setStyleSheet(
            "color: white; font-weight: bold; border-radius: 4px; padding: 10px;"
        )
        s_layout.addWidget(s_header)

        s_layout.addWidget(QLabel("Azioni Rapide:"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        for q in self.QUICK_PROMPTS:
            btn = QPushButton(f"{q['icon']} {q['label']}")
            btn.setProperty("class", "QuickPromptButton")
            btn.setStyleSheet(f"background-color: {q['color']};")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda chk=False, p=q["prompt"]: self._send_prompt(p))
            scroll_layout.addWidget(btn)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        s_layout.addWidget(scroll)

        btn_new = QPushButton("Nuova Conversazione")
        btn_new.clicked.connect(self._clear_chat)
        s_layout.addWidget(btn_new)

        main_layout.addWidget(sidebar)

        # Chat
        container = QWidget()
        c_layout = QVBoxLayout(container)

        self.txt_history = QTextBrowser()
        c_layout.addWidget(self.txt_history)

        input_frame = QFrame()
        input_frame.setObjectName("ChatInputFrame")
        i_layout = QVBoxLayout(input_frame)
        self.entry_msg = QTextEdit()
        self.entry_msg.setPlaceholderText("Chiedi a Lyra...")
        self.entry_msg.setFixedHeight(80)
        self.entry_msg.setStyleSheet("border: none;")
        i_layout.addWidget(self.entry_msg)

        btn_row = QHBoxLayout()
        self.lbl_loading = QLabel("")
        btn_row.addWidget(self.lbl_loading)
        btn_row.addStretch()
        self.btn_send = QPushButton("Invia")
        self.btn_send.setProperty("class", "PrimaryButton")
        self.btn_send.clicked.connect(self._send_current_msg)
        btn_row.addWidget(self.btn_send)
        i_layout.addLayout(btn_row)

        c_layout.addWidget(input_frame)
        main_layout.addWidget(container)

    def _append_message(self, sender, text, color):
        ts = datetime.now().strftime("%H:%M")
        html = f'<div style="margin-bottom: 15px;"><b style="color: {color};">{sender}</b> <small style="color: #999;">({ts})</small><br>'
        html += f'<div style="margin-top: 5px; padding: 10px; background-color: #f9f9f9; border-radius: 8px;">{text}</div></div>'
        self.txt_history.append(html)
        self.txt_history.moveCursor(QTextCursor.End)

    def _send_current_msg(self):
        msg = self.entry_msg.toPlainText().strip()
        if msg:
            self._send_prompt(msg)

    def _send_prompt(self, prompt):
        if self.is_loading:
            return
        self.entry_msg.clear()
        self._append_message("Tu", prompt, "#1E3A8A")
        self.loading_signal.emit(True)
        threading.Thread(target=self._chat_worker, args=(prompt,), daemon=True).start()

    @Slot(bool)
    def _set_loading_state(self, loading):
        self.is_loading = loading
        self.btn_send.setEnabled(not loading)
        self.lbl_loading.setText("Lyra sta pensando..." if loading else "")

    def _chat_worker(self, message):
        try:
            res = self.controller.api_client.send_chat_message(message, history=self.history[-10:])
            reply = res.get("response", "Errore.")
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "model", "content": reply})
            self.chat_signal.emit(reply, False)
        except Exception as e:
            self.chat_signal.emit(str(e), True)
        finally:
            self.loading_signal.emit(False)

    @Slot(str, bool)
    def _on_response_received(self, text, is_error):
        self._append_message("Lyra", text.replace("\n", "<br>"), "red" if is_error else "#059669")

    def _show_welcome_message(self):
        self._append_message("Lyra", "Ciao! Come posso aiutarti oggi?", "#059669")

    def _clear_chat(self):
        self.txt_history.clear()
        self.history = []
        self._show_welcome_message()

    def refresh_data(self):
        pass
