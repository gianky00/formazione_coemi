"""
Enhanced Lyra AI Assistant View for Intelleo.
Provides intelligent assistance with rich text formatting and proactive suggestions.
"""

import re
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk


class LyraView(tk.Frame):
    """
    Enhanced AI chat interface with rich formatting and quick actions.
    """

    QUICK_PROMPTS = [
        {
            "icon": "\U0001f4ca",
            "label": "Riepilogo",
            "prompt": "Fammi un riepilogo completo della situazione attuale: certificati scaduti, in scadenza, dipendenti con dati mancanti e suggerimenti per migliorare.",
            "color": "#3B82F6",
        },
        {
            "icon": "\u26a0",
            "label": "Scadenze",
            "prompt": "Quali certificati scadranno nei prossimi 30 giorni? Elencali per priorita con i nomi dei dipendenti.",
            "color": "#F59E0B",
        },
        {
            "icon": "\U0001f4c5",
            "label": "Piano Formazione",
            "prompt": "Suggerisci un piano di formazione ottimale per i prossimi 3 mesi, raggruppando i dipendenti per categoria di corso in scadenza.",
            "color": "#10B981",
        },
        {
            "icon": "\U0001f465",
            "label": "Dipendenti Incompleti",
            "prompt": "Quali dipendenti hanno dati anagrafici incompleti? Elenca nome, cognome e quali campi mancano.",
            "color": "#8B5CF6",
        },
        {
            "icon": "\U0001f4c8",
            "label": "Statistiche",
            "prompt": "Mostrami statistiche dettagliate: totale certificati per categoria, percentuale scaduti, media giorni alla scadenza, dipendenti piu a rischio.",
            "color": "#06B6D4",
        },
        {
            "icon": "\U0001f50d",
            "label": "Audit",
            "prompt": "Analizza gli ultimi log di audit e segnala eventuali anomalie o pattern sospetti nelle operazioni.",
            "color": "#EF4444",
        },
        {
            "icon": "\U0001f4dd",
            "label": "Report",
            "prompt": "Genera un report completo da inviare alla direzione con lo stato della formazione aziendale.",
            "color": "#EC4899",
        },
        {
            "icon": "\U0001f4a1",
            "label": "Suggerimenti",
            "prompt": "Quali azioni immediate mi consigli per migliorare la gestione dei certificati? Dai priorita ai problemi piu urgenti.",
            "color": "#F97316",
        },
    ]

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F3F4F6")

        self.history = []
        self.is_loading = False

        self.setup_ui()
        self.setup_tags()
        self._show_welcome_message()

    def setup_ui(self):
        # Main container with sidebar
        main_container = tk.Frame(self, bg="#F3F4F6")
        main_container.pack(fill="both", expand=True)

        # Sidebar with quick actions - more compact
        sidebar = tk.Frame(main_container, bg="#FFFFFF", width=200)
        sidebar.pack(side="left", fill="y", padx=(5, 0), pady=5)
        sidebar.pack_propagate(False)

        self._setup_sidebar(sidebar)

        # Chat area - less padding
        chat_container = tk.Frame(main_container, bg="#F3F4F6")
        chat_container.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self._setup_chat_area(chat_container)

    def _setup_sidebar(self, sidebar):
        """Setup sidebar with quick actions and info."""
        # Header
        header = tk.Frame(sidebar, bg="#1E3A8A", height=45)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="\U0001f4ab Lyra IA",
            font=("Segoe UI", 11, "bold"),
            bg="#1E3A8A",
            fg="white",
        ).pack(pady=10)

        # Quick actions label
        tk.Label(
            sidebar, text="Azioni Rapide", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#1F2937"
        ).pack(anchor="w", padx=10, pady=(8, 5))

        # Quick action buttons - compact
        btn_frame = tk.Frame(sidebar, bg="#FFFFFF")
        btn_frame.pack(fill="x", padx=5)

        for prompt_config in self.QUICK_PROMPTS:
            self._create_quick_button(btn_frame, prompt_config)

        # Separator
        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", pady=8, padx=8)

        # Info section - more compact with icons
        info_frame = tk.Frame(sidebar, bg="#F0F9FF", relief="flat", bd=1)
        info_frame.pack(fill="x", padx=8, pady=(0, 5))

        tk.Label(
            info_frame,
            text="\U0001f4e1 Dati Accessibili",
            font=("Segoe UI", 9, "bold"),
            bg="#F0F9FF",
            fg="#1E40AF",
        ).pack(anchor="w", padx=8, pady=(5, 3))

        data_items = [
            ("\U0001f4c4", "Certificati validati e da convalidare"),
            ("\U0001f465", "Anagrafiche dipendenti"),
            ("\U0001f4c5", "Scadenze e storico"),
            ("\U0001f50d", "Log di audit completi"),
            ("\U0001f4ca", "Statistiche in tempo reale"),
        ]

        for icon, text in data_items:
            row = tk.Frame(info_frame, bg="#F0F9FF")
            row.pack(fill="x", padx=8, pady=1)
            tk.Label(row, text=icon, font=("Segoe UI", 8), bg="#F0F9FF").pack(side="left")
            tk.Label(row, text=text, font=("Segoe UI", 8), bg="#F0F9FF", fg="#374151").pack(
                side="left", padx=3
            )

        tk.Frame(info_frame, height=5, bg="#F0F9FF").pack()  # Spacing

        # Clear chat button at bottom
        tk.Button(
            sidebar,
            text="Nuova Conversazione",
            bg="#6B7280",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            command=self._clear_chat,
        ).pack(side="bottom", fill="x", padx=8, pady=8)

    def _create_quick_button(self, parent, config):
        """Create a quick action button."""
        btn_frame = tk.Frame(parent, bg="#FFFFFF")
        btn_frame.pack(fill="x", pady=2)

        btn = tk.Button(
            btn_frame,
            text=f"{config['icon']} {config['label']}",
            bg=config["color"],
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            anchor="w",
            padx=10,
            cursor="hand2",
            command=lambda p=config["prompt"]: self._send_quick_prompt(p),
        )
        btn.pack(fill="x")

        # Hover effect
        btn.bind("<Enter>", lambda e, b=btn, c=config["color"]: b.config(bg=self._lighten_color(c)))
        btn.bind("<Leave>", lambda e, b=btn, c=config["color"]: b.config(bg=c))

    def _lighten_color(self, hex_color):
        """Lighten a hex color."""
        # Simple lighten - add to RGB values
        hex_color = hex_color.lstrip("#")
        rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        lightened = tuple(min(255, c + 30) for c in rgb)
        return "#{:02x}{:02x}{:02x}".format(*lightened)

    def _setup_chat_area(self, container):
        """Setup main chat area."""
        # Chat header
        chat_header = tk.Frame(container, bg="#FFFFFF", height=50)
        chat_header.pack(fill="x")
        chat_header.pack_propagate(False)

        tk.Label(
            chat_header,
            text="Chat con Lyra",
            font=("Segoe UI", 11, "bold"),
            bg="#FFFFFF",
            fg="#1F2937",
        ).pack(side="left", padx=15, pady=12)

        # Export button
        tk.Button(
            chat_header,
            text="Esporta",
            bg="#6B7280",
            fg="white",
            font=("Segoe UI", 8),
            relief="flat",
            command=self._export_chat,
        ).pack(side="right", padx=10, pady=10)

        # Chat history with custom text widget
        history_frame = tk.Frame(container, bg="#FFFFFF")
        history_frame.pack(fill="both", expand=True, pady=(5, 0))

        # Create text widget with scrollbar - increased font size
        self.txt_history = tk.Text(
            history_frame,
            wrap="word",
            font=("Segoe UI", 11),
            bg="#FFFFFF",
            relief="flat",
            padx=12,
            pady=8,
            state="disabled",
            cursor="arrow",
        )

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.txt_history.yview)
        self.txt_history.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.txt_history.pack(side="left", fill="both", expand=True)

        # Input area
        input_container = tk.Frame(container, bg="#FFFFFF")
        input_container.pack(fill="x", pady=(10, 0))

        # Formatting toolbar
        toolbar = tk.Frame(input_container, bg="#F9FAFB")
        toolbar.pack(fill="x", padx=10, pady=5)

        # Format buttons (for reference - output is formatted by Lyra)
        tk.Label(
            toolbar, text="Formattazione output:", font=("Segoe UI", 8), bg="#F9FAFB", fg="#6B7280"
        ).pack(side="left", padx=5)

        format_info = ["Tabelle", "Elenchi", "Grassetto", "Colori"]
        for fmt in format_info:
            lbl = tk.Label(
                toolbar, text=fmt, font=("Segoe UI", 8), bg="#E5E7EB", fg="#374151", padx=5, pady=2
            )
            lbl.pack(side="left", padx=2)

        # Input row
        input_row = tk.Frame(input_container, bg="#FFFFFF")
        input_row.pack(fill="x", padx=10, pady=10)

        # Text entry
        self.entry_msg = tk.Text(
            input_row, height=3, font=("Segoe UI", 10), wrap="word", relief="solid", borderwidth=1
        )
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_msg.bind("<Return>", self._on_enter)
        self.entry_msg.bind("<Shift-Return>", lambda e: None)  # Allow shift+enter for newline

        # Send button
        self.btn_send = tk.Button(
            input_row,
            text="Invia",
            bg="#1E3A8A",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            width=10,
            command=self.send_message,
        )
        self.btn_send.pack(side="right")

        # Loading indicator
        self.loading_label = tk.Label(
            input_container, text="", bg="#FFFFFF", fg="#6B7280", font=("Segoe UI", 9)
        )
        self.loading_label.pack(pady=5)

    def setup_tags(self):
        """Setup text tags for rich formatting."""
        # User message styling - increased font size
        self.txt_history.tag_configure(
            "user_header", foreground="#1E3A8A", font=("Segoe UI", 11, "bold")
        )
        self.txt_history.tag_configure(
            "user_msg",
            foreground="#1F2937",
            font=("Segoe UI", 11),
            background="#EFF6FF",
            lmargin1=10,
            lmargin2=10,
            rmargin=30,
            spacing1=3,
            spacing3=5,
        )

        # Lyra message styling - increased font size
        self.txt_history.tag_configure(
            "lyra_header", foreground="#059669", font=("Segoe UI", 11, "bold")
        )
        self.txt_history.tag_configure(
            "lyra_msg",
            foreground="#1F2937",
            font=("Segoe UI", 11),
            lmargin1=10,
            lmargin2=10,
            spacing1=3,
            spacing3=5,
        )

        # Rich text formatting - increased font sizes
        self.txt_history.tag_configure("bold", font=("Segoe UI", 11, "bold"))
        self.txt_history.tag_configure("italic", font=("Segoe UI", 11, "italic"))
        self.txt_history.tag_configure("code", font=("Consolas", 10), background="#F3F4F6")
        self.txt_history.tag_configure(
            "heading", font=("Segoe UI", 13, "bold"), foreground="#1E3A8A", spacing1=8, spacing3=4
        )
        self.txt_history.tag_configure(
            "subheading",
            font=("Segoe UI", 12, "bold"),
            foreground="#374151",
            spacing1=6,
            spacing3=2,
        )

        # Status colors
        self.txt_history.tag_configure("error", foreground="#EF4444", font=("Segoe UI", 10, "bold"))
        self.txt_history.tag_configure("warning", foreground="#F59E0B")
        self.txt_history.tag_configure("success", foreground="#10B981")
        self.txt_history.tag_configure("info", foreground="#3B82F6")

        # Table styling
        self.txt_history.tag_configure(
            "table_header", font=("Consolas", 9, "bold"), background="#E5E7EB"
        )
        self.txt_history.tag_configure("table_row", font=("Consolas", 9), background="#F9FAFB")
        self.txt_history.tag_configure("table_row_alt", font=("Consolas", 9), background="#FFFFFF")

        # List styling
        self.txt_history.tag_configure(
            "bullet", foreground="#3B82F6", font=("Segoe UI", 10, "bold")
        )
        self.txt_history.tag_configure(
            "number", foreground="#8B5CF6", font=("Segoe UI", 10, "bold")
        )

        # Timestamp
        self.txt_history.tag_configure("timestamp", foreground="#9CA3AF", font=("Segoe UI", 8))

        # System message
        self.txt_history.tag_configure(
            "system", foreground="#6B7280", font=("Segoe UI", 9, "italic"), justify="center"
        )

    def _show_welcome_message(self):
        """Show welcome message on startup."""
        self.txt_history.config(state="normal")

        welcome = (
            "Ciao! Sono Lyra, il tuo assistente virtuale per la gestione dei certificati.\n\n"
            "Posso aiutarti con:\n"
            "  - Analisi certificati scaduti e in scadenza\n"
            "  - Pianificazione corsi di formazione\n"
            "  - Verifica dati dipendenti\n"
            "  - Report e statistiche\n"
            "  - Suggerimenti proattivi\n\n"
            "Usa i pulsanti rapidi sulla sinistra o scrivi la tua domanda!"
        )

        self.txt_history.insert("end", "\U0001f4ab Lyra\n", "lyra_header")
        self.txt_history.insert("end", welcome + "\n\n", "lyra_msg")

        self.txt_history.config(state="disabled")

    def _on_enter(self, event):
        """Handle enter key - send message unless shift is held."""
        if not event.state & 0x1:  # Shift not pressed
            self.send_message()
            return "break"

    def send_message(self):
        """Send user message to Lyra."""
        msg = self.entry_msg.get("1.0", "end-1c").strip()
        if not msg or self.is_loading:
            return

        self.entry_msg.delete("1.0", "end")
        self._append_user_message(msg)

        # Show loading
        self.is_loading = True
        self.btn_send.config(state="disabled")
        self._animate_loading()

        # Send in background
        threading.Thread(target=self._chat_worker, args=(msg,), daemon=True).start()

    def _send_quick_prompt(self, prompt):
        """Send a quick prompt."""
        if self.is_loading:
            return

        self.entry_msg.delete("1.0", "end")
        self._append_user_message(prompt)

        self.is_loading = True
        self.btn_send.config(state="disabled")
        self._animate_loading()

        threading.Thread(target=self._chat_worker, args=(prompt,), daemon=True).start()

    def _append_user_message(self, msg):
        """Append user message to chat."""
        self.txt_history.config(state="normal")

        timestamp = datetime.now().strftime("%H:%M")
        self.txt_history.insert("end", "\U0001f464 Tu ", "user_header")
        self.txt_history.insert("end", f"({timestamp})\n", "timestamp")
        self.txt_history.insert("end", msg + "\n\n", "user_msg")

        self.txt_history.see("end")
        self.txt_history.config(state="disabled")

    def _animate_loading(self):
        """Animate loading indicator."""
        dots = [".", "..", "...", ""]

        def animate(i=0):
            if self.is_loading:
                self.loading_label.config(text=f"Lyra sta pensando{dots[i % 4]}")
                self.after(300, lambda: animate(i + 1))
            else:
                self.loading_label.config(text="")

        animate()

    def _chat_worker(self, message):
        """Background worker for chat API call."""
        try:
            # Build context with all available data
            context = self._build_context()

            # Prepare history
            hist_payload = self.history[-10:]

            # Enhanced prompt with context
            enhanced_message = f"""
            CONTESTO ATTUALE DEL SISTEMA:
            {context}

            DOMANDA DELL'UTENTE:
            {message}

            ISTRUZIONI:
            - Rispondi in italiano in modo professionale e chiaro
            - Usa formattazione markdown quando appropriato (tabelle, elenchi, grassetto)
            - Se ci sono problemi urgenti, evidenziali chiaramente
            - Fornisci suggerimenti pratici e actionable
            - Se mostri dati numerici, usa tabelle per chiarezza
            """

            response = self.controller.api_client.send_chat_message(
                enhanced_message, history=hist_payload
            )
            reply = response.get(
                "response", "Mi dispiace, non sono riuscita a elaborare la risposta."
            )

            # Update history
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "model", "content": reply})

            # Update UI on main thread
            self.after(0, lambda: self._append_lyra_message(reply))

        except Exception as e:
            error_msg = f"Si è verificato un errore: {e!s}"
            self.after(0, lambda: self._append_lyra_message(error_msg, is_error=True))

        finally:
            self.after(0, self._stop_loading)

    def _build_context(self):
        """Build context string with all system data."""
        context_parts = []

        try:
            # Get certificates summary
            certs = self.controller.api_client.get("certificati", params={"validated": "true"})
            pending = self.controller.api_client.get("certificati", params={"validated": "false"})

            # Count by status
            from datetime import datetime

            today = datetime.now().date()
            expired = 0
            expiring_30 = 0
            expiring_60 = 0
            active = 0

            for cert in certs:
                scad = cert.get("data_scadenza")
                if scad and scad.lower() not in ["none", "nessuna"]:
                    try:
                        exp_date = datetime.strptime(scad, "%d/%m/%Y").date()
                        days = (exp_date - today).days
                        if days < 0:
                            expired += 1
                        elif days <= 30:
                            expiring_30 += 1
                        elif days <= 60:
                            expiring_60 += 1
                        else:
                            active += 1
                    except:
                        active += 1
                else:
                    active += 1

            context_parts.append(
                f"CERTIFICATI: {len(certs)} totali validati, {len(pending)} da convalidare"
            )
            context_parts.append(
                f"STATO: {expired} scaduti, {expiring_30} in scadenza (30gg), {expiring_60} in scadenza (60gg), {active} attivi"
            )

            # Get employees
            dipendenti = self.controller.api_client.get_dipendenti_list()
            incomplete = sum(
                1
                for d in dipendenti
                if not d.get("matricola") or not d.get("data_nascita") or not d.get("mansione")
            )
            context_parts.append(
                f"DIPENDENTI: {len(dipendenti)} totali, {incomplete} con dati incompleti"
            )

            # Get categories distribution
            categories = {}
            for cert in certs:
                cat = cert.get("categoria", "ALTRO")
                categories[cat] = categories.get(cat, 0) + 1

            cat_str = ", ".join(
                [f"{k}: {v}" for k, v in sorted(categories.items(), key=lambda x: -x[1])[:5]]
            )
            context_parts.append(f"CATEGORIE TOP: {cat_str}")

            # Recent audit logs (if accessible - requires admin)
            try:
                audit_logs = self.controller.api_client.get("audit", params={"limit": "50"})
                if audit_logs and isinstance(audit_logs, list):
                    # Summarize audit activity
                    context_parts.append(f"\nAUDIT LOG ({len(audit_logs)} record recenti):")

                    # Group by category
                    categories = {}
                    users = {}
                    recent_details = []

                    for log in audit_logs[:50]:
                        cat = log.get("category", "OTHER")
                        categories[cat] = categories.get(cat, 0) + 1

                        user = log.get("username", "System")
                        users[user] = users.get(user, 0) + 1

                        # Keep first 10 for details
                        if len(recent_details) < 10:
                            timestamp = (
                                log.get("timestamp", "")[:16] if log.get("timestamp") else ""
                            )
                            action = log.get("action", "")
                            details = log.get("details", "")[:50] if log.get("details") else ""
                            recent_details.append(f"  - [{timestamp}] {action}: {details}")

                    # Category summary
                    cat_str = ", ".join(
                        [f"{k}: {v}" for k, v in sorted(categories.items(), key=lambda x: -x[1])]
                    )
                    context_parts.append(f"  Categorie: {cat_str}")

                    # User activity
                    user_str = ", ".join(
                        [f"{k}: {v}" for k, v in sorted(users.items(), key=lambda x: -x[1])[:5]]
                    )
                    context_parts.append(f"  Utenti attivi: {user_str}")

                    # Recent actions detail
                    context_parts.append("  Azioni recenti:")
                    context_parts.extend(recent_details)
            except Exception as audit_err:
                context_parts.append(f"AUDIT: Non accessibile o errore ({audit_err})")

        except Exception as e:
            context_parts.append(f"Errore nel recupero contesto: {e}")

        return "\n".join(context_parts)

    def _append_lyra_message(self, msg, is_error=False):
        """Append Lyra's message with rich formatting."""
        self.txt_history.config(state="normal")

        timestamp = datetime.now().strftime("%H:%M")
        self.txt_history.insert("end", "\U0001f4ab Lyra ", "lyra_header")
        self.txt_history.insert("end", f"({timestamp})\n", "timestamp")

        if is_error:
            self.txt_history.insert("end", msg + "\n\n", "error")
        else:
            # Parse and format the message
            self._insert_formatted_text(msg)
            self.txt_history.insert("end", "\n\n")

        self.txt_history.see("end")
        self.txt_history.config(state="disabled")

    def _insert_formatted_text(self, text):
        """Insert text with markdown-like formatting."""
        lines = text.split("\n")
        in_table = False
        table_rows = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Detect table
            if "|" in stripped and stripped.startswith("|"):
                if not in_table:
                    in_table = True
                    table_rows = []
                table_rows.append(stripped)
                continue
            elif in_table:
                # End of table, render it
                self._render_table(table_rows)
                in_table = False
                table_rows = []

            # Headings
            if stripped.startswith("### "):
                self.txt_history.insert("end", stripped[4:] + "\n", "subheading")
            elif stripped.startswith("## "):
                self.txt_history.insert("end", stripped[3:] + "\n", "subheading")
            elif stripped.startswith("# "):
                self.txt_history.insert("end", stripped[2:] + "\n", "heading")

            # Bullet points
            elif stripped.startswith("- ") or stripped.startswith("* "):
                self.txt_history.insert("end", "  \u2022 ", "bullet")
                self._insert_inline_formatted(stripped[2:])
                self.txt_history.insert("end", "\n")

            # Numbered lists
            elif re.match(r"^\d+\.\s", stripped):
                match = re.match(r"^(\d+\.)\s(.*)$", stripped)
                if match:
                    self.txt_history.insert("end", f"  {match.group(1)} ", "number")
                    self._insert_inline_formatted(match.group(2))
                    self.txt_history.insert("end", "\n")

            # Code blocks
            elif stripped.startswith("```"):
                continue  # Skip code fence markers

            # Regular text
            else:
                self._insert_inline_formatted(line)
                self.txt_history.insert("end", "\n")

        # Handle remaining table
        if in_table and table_rows:
            self._render_table(table_rows)

    def _insert_inline_formatted(self, text):
        """Insert text with inline formatting (bold, italic, code)."""
        # Process bold (**text** or __text__) - fixed regex to handle properly
        pattern = r"(\*\*[^*]+\*\*|__[^_]+__|`[^`]+`)"
        parts = re.split(pattern, text)

        for part in parts:
            if not part:
                continue
            if part.startswith("**") and part.endswith("**") and len(part) > 4:
                # Bold text - remove ** markers
                self.txt_history.insert("end", part[2:-2], "bold")
            elif part.startswith("__") and part.endswith("__") and len(part) > 4:
                # Bold with underscores
                self.txt_history.insert("end", part[2:-2], "bold")
            elif part.startswith("`") and part.endswith("`") and len(part) > 2:
                # Inline code
                self.txt_history.insert("end", part[1:-1], "code")
            else:
                # Regular text - also check for any remaining single asterisks for italic
                italic_pattern = r"(\*[^*]+\*)"
                italic_parts = re.split(italic_pattern, part)
                for ip in italic_parts:
                    if not ip:
                        continue
                    if (
                        ip.startswith("*")
                        and ip.endswith("*")
                        and len(ip) > 2
                        and not ip.startswith("**")
                    ):
                        self.txt_history.insert("end", ip[1:-1], "italic")
                    else:
                        self.txt_history.insert("end", ip, "lyra_msg")

    def _render_table(self, rows):
        """Render a markdown table."""
        if not rows:
            return

        # Parse rows
        parsed_rows = []
        for row in rows:
            cells = [c.strip() for c in row.strip("|").split("|")]
            if not all(c.replace("-", "").replace(":", "") == "" for c in cells):  # Skip separator
                parsed_rows.append(cells)

        if not parsed_rows:
            return

        # Calculate column widths
        num_cols = max(len(row) for row in parsed_rows)
        col_widths = [0] * num_cols
        for row in parsed_rows:
            for i, cell in enumerate(row):
                if i < num_cols:
                    col_widths[i] = max(col_widths[i], len(cell))

        # Render
        self.txt_history.insert("end", "\n")

        for row_idx, row in enumerate(parsed_rows):
            tag = (
                "table_header"
                if row_idx == 0
                else ("table_row" if row_idx % 2 == 1 else "table_row_alt")
            )

            line = " "
            for i, cell in enumerate(row):
                if i < num_cols:
                    line += cell.ljust(col_widths[i] + 2)
            line += "\n"

            self.txt_history.insert("end", line, tag)

        self.txt_history.insert("end", "\n")

    def _stop_loading(self):
        """Stop loading state."""
        self.is_loading = False
        self.btn_send.config(state="normal")
        self.loading_label.config(text="")

    def _clear_chat(self):
        """Clear chat history."""
        self.txt_history.config(state="normal")
        self.txt_history.delete("1.0", "end")
        self.txt_history.config(state="disabled")

        self.history = []
        self._show_welcome_message()

    def _export_chat(self):
        """Export chat history to file."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt"), ("HTML File", "*.html")],
            title="Esporta Conversazione",
        )

        if filepath:
            try:
                content = self.txt_history.get("1.0", "end")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"Conversazione Lyra - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(content)

                messagebox.showinfo("Esportato", f"Conversazione salvata in:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile salvare: {e}")

    def refresh_data(self):
        """Called when tab is selected - can show proactive suggestions."""
        pass  # Could add proactive suggestions here
