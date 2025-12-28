import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from desktop_app.utils import TaskRunner, open_file
from desktop_app.widgets.advanced_filter import setup_filterable_treeview
import os
import threading


class ScadenzarioView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.data = []

        self.setup_ui()
        self.setup_keyboard_shortcuts()

    def setup_ui(self):
        # Toolbar
        toolbar = tk.Frame(self, bg="#F3F4F6", pady=10)
        toolbar.pack(fill="x")

        tk.Button(toolbar, text="Aggiorna", command=self.refresh_data).pack(side="left", padx=10)

        # Actions
        tk.Button(toolbar, text="Esporta PDF", bg="#2563EB", fg="white", command=self.export_pdf).pack(side="left", padx=10)
        tk.Button(toolbar, text="Invia Email Report", bg="#2563EB", fg="white", command=self.send_email).pack(side="left", padx=10)

        # Search
        tk.Label(toolbar, text="Cerca:", bg="#F3F4F6").pack(side="left", padx=(20, 5))
        self.entry_search = ttk.Entry(toolbar, width=25)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<KeyRelease>", lambda e: self.filter_data())

        # Category Filter (populated dynamically from data) - increased width
        tk.Label(toolbar, text="Categoria:", bg="#F3F4F6").pack(side="left", padx=(15, 5))
        self.combo_categoria = ttk.Combobox(toolbar, values=["Tutte"], state="readonly", width=28)
        self.combo_categoria.set("Tutte")
        self.combo_categoria.pack(side="left", padx=5)
        self.combo_categoria.bind("<<ComboboxSelected>>", lambda e: self.filter_data())

        # Status Filter (populated dynamically from data) - increased width
        tk.Label(toolbar, text="Stato:", bg="#F3F4F6").pack(side="left", padx=(15, 5))
        self.combo_status = ttk.Combobox(toolbar, values=["Tutti"], state="readonly", width=15)
        self.combo_status.set("Tutti")
        self.combo_status.pack(side="left", padx=5)
        self.combo_status.bind("<<ComboboxSelected>>", lambda e: self.filter_data())

        # Reset filters button
        self.btn_reset = tk.Button(toolbar, text="Reset Filtri", bg="#6B7280", fg="white",
                                    font=("Segoe UI", 8), command=self._reset_filters)
        self.btn_reset.pack(side="left", padx=10)
        self.btn_reset.config(state="disabled")  # Initially disabled

        # Legend and count
        self.lbl_count = tk.Label(toolbar, text="", bg="#F3F4F6", font=("Segoe UI", 9))
        self.lbl_count.pack(side="right", padx=10)

        # Active filter indicator
        self.lbl_filter_indicator = tk.Label(toolbar, text="", bg="#F3F4F6", fg="#DC2626", font=("Segoe UI", 8, "bold"))
        self.lbl_filter_indicator.pack(side="right", padx=5)

        tk.Label(toolbar, text="Rosso=Scaduto | Arancio=In Scadenza | Verde=Valido", bg="#F3F4F6", font=("Segoe UI", 8)).pack(side="right", padx=20)

        # Treeview
        columns = ("dipendente", "corso", "categoria", "scadenza", "giorni_rimanenti")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="extended")

        self.tree.heading("dipendente", text="Dipendente")
        self.tree.heading("corso", text="Documento")
        self.tree.heading("categoria", text="Categoria")
        self.tree.heading("scadenza", text="Scadenza")
        self.tree.heading("giorni_rimanenti", text="Giorni Rimanenti")

        # Optimized column widths
        self.tree.column("dipendente", width=200, minwidth=150)
        self.tree.column("corso", width=300, minwidth=150)
        self.tree.column("categoria", width=150, minwidth=100)
        self.tree.column("scadenza", width=100, minwidth=80, anchor="center")
        self.tree.column("giorni_rimanenti", width=120, minwidth=80, anchor="center")

        # Tags for colors
        self.tree.tag_configure("scaduto", background="#FECACA")  # Red-200
        self.tree.tag_configure("in_scadenza", background="#FED7AA")  # Orange-200
        self.tree.tag_configure("valido", background="#BBF7D0")  # Green-200

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Column sorting
        self.sort_column = None
        self.sort_reverse = False
        for col in columns:
            self.tree.heading(col, command=lambda c=col: self.sort_by_column(c))

        # Setup advanced column filters (right-click on headers)
        column_names = {
            "dipendente": "Dipendente",
            "corso": "Documento",
            "categoria": "Categoria",
            "scadenza": "Data Scadenza",
            "giorni_rimanenti": "Giorni Rimanenti"
        }
        setup_filterable_treeview(self.tree, column_names)
        self.tree.bind("<<FilterChanged>>", lambda e: self._on_filter_changed())

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common actions."""
        self.tree.bind("<F5>", lambda e: self.refresh_data())
        self.tree.bind("<Control-a>", self.select_all)
        self.tree.bind("<Control-f>", lambda e: self.entry_search.focus_set())
        self.tree.bind("<Control-e>", lambda e: self.export_pdf())
        self.tree.bind("<Escape>", lambda e: self._reset_filters())

    def _on_filter_changed(self):
        """Handle filter changes and update UI."""
        self.filter_data()
        self._update_filter_indicator()

    def _update_filter_indicator(self):
        """Update the filter indicator and reset button state."""
        has_filters = hasattr(self.tree, 'has_filters') and self.tree.has_filters()
        has_search = bool(self.entry_search.get())
        has_cat = self.combo_categoria.get() != "Tutte"
        has_status = self.combo_status.get() != "Tutti"

        if has_filters or has_search or has_cat or has_status:
            self.btn_reset.config(state="normal", bg="#DC2626")
            active = []
            if has_search:
                active.append("Cerca")
            if has_cat:
                active.append("Categoria")
            if has_status:
                active.append("Stato")
            if has_filters:
                active.append("Colonne")
            self.lbl_filter_indicator.config(text=f"Filtri attivi: {', '.join(active)}")
        else:
            self.btn_reset.config(state="disabled", bg="#6B7280")
            self.lbl_filter_indicator.config(text="")

    def _reset_filters(self):
        """Reset all filters."""
        # Reset search
        self.entry_search.delete(0, tk.END)

        # Reset comboboxes
        self.combo_categoria.set("Tutte")
        self.combo_status.set("Tutti")

        # Reset column filters
        if hasattr(self.tree, 'clear_filters'):
            self.tree.clear_filters()

        # Refresh display
        self.filter_data()
        self._update_filter_indicator()

    def select_all(self, event=None):
        """Select all items in the tree."""
        self.tree.selection_set(self.tree.get_children())
        return "break"

    def sort_by_column(self, col):
        """Sort treeview by column."""
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        items = [(self.tree.item(item)["values"], item) for item in self.tree.get_children()]
        col_idx = list(self.tree["columns"]).index(col)

        # Special sorting for numeric days column
        if col == "giorni_rimanenti":
            def sort_key(x):
                val = x[0][col_idx]
                try:
                    return int(val) if val != "N/D" else 99999
                except:
                    return 99999
            items.sort(key=sort_key, reverse=self.sort_reverse)
        else:
            items.sort(key=lambda x: str(x[0][col_idx]).lower() if x[0][col_idx] else "", reverse=self.sort_reverse)

        for idx, (vals, item) in enumerate(items):
            self.tree.move(item, "", idx)

        # Update heading to show sort direction
        arrow = " ▼" if self.sort_reverse else " ▲"
        headings = {"dipendente": "Dipendente", "corso": "Documento",
                   "categoria": "Categoria", "scadenza": "Scadenza", "giorni_rimanenti": "Giorni Rimanenti"}
        for c in self.tree["columns"]:
            heading_text = headings.get(c, c)
            if c == col:
                self.tree.heading(c, text=heading_text + arrow)
            else:
                self.tree.heading(c, text=heading_text)

    def refresh_data(self):
        def fetch():
            try:
                new_data = self.controller.api_client.get("certificati", params={"validated": "true"})
                if self.winfo_exists():
                    self.after(0, lambda: self._update_data(new_data))
            except Exception as e:
                if self.winfo_exists():
                    self.after(0, lambda: messagebox.showerror("Errore", str(e)))

        threading.Thread(target=fetch, daemon=True).start()

    def _update_data(self, new_data):
        self.data = new_data
        self._update_filter_options()
        self.filter_data()

    def _update_filter_options(self):
        """Update filter dropdowns to show only available options in current data."""
        categories = set()
        statuses = set()

        for item in self.data:
            cat = item.get("categoria")
            if cat:
                categories.add(cat.upper())
            status = item.get("stato_certificato")
            if status:
                statuses.add(status.lower())

        # Update category combobox
        current_cat = self.combo_categoria.get()
        cat_values = ["Tutte"] + sorted(categories)
        self.combo_categoria["values"] = cat_values
        if current_cat not in cat_values:
            self.combo_categoria.set("Tutte")

        # Update status combobox
        current_status = self.combo_status.get()
        status_map = {"attivo": "Valido", "in_scadenza": "In Scadenza", "scaduto": "Scaduto"}
        status_values = ["Tutti"] + [status_map.get(s, s.title()) for s in sorted(statuses)]
        self.combo_status["values"] = status_values
        if current_status not in status_values:
            self.combo_status.set("Tutti")

    def filter_data(self):
        query = self.entry_search.get().lower()
        cat_filter = self.combo_categoria.get()
        status_filter = self.combo_status.get().lower()

        for item in self.tree.get_children():
            self.tree.delete(item)

        def get_date_key(d):
            val = d.get("data_scadenza")
            return val if val else "9999-99-99"

        sorted_data = sorted(self.data, key=get_date_key)

        from datetime import datetime
        today = datetime.now().date()

        count = 0
        for item in sorted_data:
            nome = str(item.get("nome") or "").lower()
            corso = str(item.get("corso") or "").lower()
            categoria = str(item.get("categoria") or "").lower()

            # Apply Category Filter
            if cat_filter != "Tutte" and (item.get("categoria") or "").upper() != cat_filter.upper():
                continue

            scadenza_str = item.get("data_scadenza")
            status = item.get("stato_certificato")

            # Simple color logic
            tag = "valido"
            if status == "scaduto":
                tag = "scaduto"
            elif status == "in_scadenza":
                tag = "in_scadenza"

            # Apply Status Filter
            if status_filter != "tutti":
                if status_filter == "in scadenza" and tag != "in_scadenza":
                    continue
                if status_filter == "scaduto" and tag != "scaduto":
                    continue
                if status_filter == "valido" and tag != "valido":
                    continue

            # Apply Search Filter
            if query and query not in nome and query not in corso and query not in categoria:
                continue

            # Calc days remaining - show empty for certificates without expiry (like NOMINA)
            days_str = ""
            if scadenza_str and scadenza_str.lower() != "none":
                try:
                    dt = datetime.strptime(scadenza_str, "%d/%m/%Y").date()
                    delta = (dt - today).days
                    days_str = str(delta)
                except:
                    pass
            else:
                scadenza_str = ""  # Empty cell instead of "NESSUNA"

            values = (
                item.get("nome"),
                item.get("corso"),
                item.get("categoria") or "ALTRO",
                scadenza_str,
                days_str
            )
            self.tree.insert("", "end", values=values, tags=(tag,))
            count += 1

        self.lbl_count.config(text=f"{count} certificati")

    def export_pdf(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not file_path:
            return

        runner = TaskRunner(self, "Esportazione", "Generazione PDF in corso...")
        try:
            def task():
                import requests
                url = f"{self.controller.api_client.base_url}/notifications/export-report"
                res = requests.get(url, headers=self.controller.api_client._get_headers())
                res.raise_for_status()
                with open(file_path, "wb") as f:
                    f.write(res.content)

            runner.run(task)
            messagebox.showinfo("Successo", f"PDF salvato in: {file_path}")
            open_file(file_path)

        except Exception as e:
            messagebox.showerror("Errore", f"Errore esportazione: {e}")

    def send_email(self):
        if messagebox.askyesno("Conferma", "Inviare il report scadenze via email agli indirizzi configurati?"):
            runner = TaskRunner(self, "Invio Email", "Invio in corso...")
            try:
                def task():
                    import requests
                    url = f"{self.controller.api_client.base_url}/notifications/send-manual-alert"
                    res = requests.post(url, headers=self.controller.api_client._get_headers())
                    res.raise_for_status()

                runner.run(task)
                messagebox.showinfo("Successo", "Email inviata correttamente.")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore invio email: {e}")
