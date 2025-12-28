import tkinter as tk
from tkinter import ttk, messagebox, Menu
import threading
import os
from desktop_app.utils import TaskRunner, ProgressTaskRunner, open_file
from desktop_app.widgets.advanced_filter import setup_filterable_treeview
from app.services.document_locator import find_document
from app.core.config import settings
from desktop_app.views.edit_certificato_dialog import EditCertificatoDialog


class DatabaseView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.data = []

        self.setup_ui()
        self.setup_keyboard_shortcuts()
        self.refresh_data()

    def setup_ui(self):
        # Toolbar
        toolbar = tk.Frame(self, bg="#F3F4F6", pady=10)
        toolbar.pack(fill="x")

        # Search
        tk.Label(toolbar, text="Cerca:", bg="#F3F4F6").pack(side="left", padx=5)
        self.entry_search = ttk.Entry(toolbar, width=25)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<KeyRelease>", lambda e: self.filter_data())

        # Category Filter (populated dynamically from data) - increased width
        tk.Label(toolbar, text="Categoria:", bg="#F3F4F6").pack(side="left", padx=(15, 5))
        self.combo_categoria = ttk.Combobox(toolbar, values=["Tutte"], state="readonly", width=28)
        self.combo_categoria.set("Tutte")
        self.combo_categoria.pack(side="left", padx=5)
        self.combo_categoria.bind("<<ComboboxSelected>>", lambda e: self.filter_data())

        # Status Filter - increased width
        tk.Label(toolbar, text="Stato:", bg="#F3F4F6").pack(side="left", padx=(15, 5))
        self.combo_status = ttk.Combobox(toolbar, values=["Tutti", "Attivo", "In Scadenza", "Scaduto"], state="readonly", width=15)
        self.combo_status.set("Tutti")
        self.combo_status.pack(side="left", padx=5)
        self.combo_status.bind("<<ComboboxSelected>>", lambda e: self.filter_data())

        tk.Button(toolbar, text="Aggiorna", command=self.refresh_data).pack(side="left", padx=10)

        # Results count label
        self.lbl_count = tk.Label(toolbar, text="", bg="#F3F4F6", font=("Segoe UI", 9))
        self.lbl_count.pack(side="right", padx=10)

        # Treeview
        columns = ("id", "dipendente", "corso", "categoria", "emissione", "scadenza", "stato")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="extended")

        self.tree.heading("id", text="ID")
        self.tree.heading("dipendente", text="Dipendente")
        self.tree.heading("corso", text="Documento")
        self.tree.heading("categoria", text="Categoria")
        self.tree.heading("emissione", text="Data Rilascio")
        self.tree.heading("scadenza", text="Data Scadenza")
        self.tree.heading("stato", text="Stato")

        # Optimized column widths
        self.tree.column("id", width=50, minwidth=40, stretch=False, anchor="center")
        self.tree.column("dipendente", width=180, minwidth=120)
        self.tree.column("corso", width=280, minwidth=150)
        self.tree.column("categoria", width=150, minwidth=100)
        self.tree.column("emissione", width=100, minwidth=80, anchor="center")
        self.tree.column("scadenza", width=100, minwidth=80, anchor="center")
        self.tree.column("stato", width=100, minwidth=70, anchor="center")

        # Row color tags
        self.tree.tag_configure("scaduto", background="#FECACA")  # Red
        self.tree.tag_configure("in_scadenza", background="#FED7AA")  # Orange
        self.tree.tag_configure("attivo", background="#BBF7D0")  # Green

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Context Menu
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Apri File PDF", command=self.open_file, accelerator="Enter")
        self.context_menu.add_command(label="Apri Cartella", command=self.open_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Modifica Dati", command=self.edit_item, accelerator="F2")
        self.context_menu.add_command(label="Elimina", command=self.delete_item, accelerator="Del")

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.open_file)

        # Column sorting
        self.sort_column = None
        self.sort_reverse = False
        for col in columns:
            self.tree.heading(col, command=lambda c=col: self.sort_by_column(c))

        # Setup advanced column filters (right-click on headers)
        column_names = {
            "id": "ID",
            "dipendente": "Dipendente",
            "corso": "Documento",
            "categoria": "Categoria",
            "emissione": "Data Rilascio",
            "scadenza": "Data Scadenza",
            "stato": "Stato"
        }
        setup_filterable_treeview(self.tree, column_names)
        self.tree.bind("<<FilterChanged>>", lambda e: self.filter_data())

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common actions."""
        self.tree.bind("<Return>", self.open_file)  # Enter to open file
        self.tree.bind("<Delete>", lambda e: self.delete_item())  # Delete key
        self.tree.bind("<F2>", lambda e: self.edit_item())  # F2 to edit
        self.tree.bind("<F5>", lambda e: self.refresh_data())  # F5 to refresh
        self.tree.bind("<Control-a>", self.select_all)  # Ctrl+A select all
        self.tree.bind("<Control-f>", lambda e: self.entry_search.focus_set())  # Ctrl+F focus search

    def sort_by_column(self, col):
        """Sort treeview by column."""
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        # Get all items with values
        items = [(self.tree.item(item)["values"], item) for item in self.tree.get_children()]

        # Get column index
        col_idx = list(self.tree["columns"]).index(col)

        # Sort
        items.sort(key=lambda x: str(x[0][col_idx]).lower() if x[0][col_idx] else "", reverse=self.sort_reverse)

        # Rearrange items
        for idx, (vals, item) in enumerate(items):
            self.tree.move(item, "", idx)

        # Update heading to show sort direction
        arrow = " ▼" if self.sort_reverse else " ▲"
        headings = {"id": "ID", "dipendente": "Dipendente", "corso": "Documento",
                   "categoria": "Categoria", "emissione": "Data Rilascio",
                   "scadenza": "Data Scadenza", "stato": "Stato"}
        for c in self.tree["columns"]:
            heading_text = headings.get(c, c)
            if c == col:
                self.tree.heading(c, text=heading_text + arrow)
            else:
                self.tree.heading(c, text=heading_text)

    def select_all(self, event=None):
        """Select all items in the tree."""
        self.tree.selection_set(self.tree.get_children())
        return "break"

    def show_context_menu(self, event):
        # Only show context menu if clicking on a row, not header
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading":
            return  # Let the filter popup handle header clicks

        item = self.tree.identify_row(event.y)
        if item:
            # Add to selection instead of replacing
            if item not in self.tree.selection():
                self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def refresh_data(self):
        def fetch():
            try:
                new_data = self.controller.api_client.get("certificati", params={"validated": "true"})
                if self.winfo_exists():
                    self.after(0, lambda: self._update_data(new_data))
            except Exception as e:
                if self.winfo_exists():
                    self.after(0, lambda: messagebox.showerror("Errore", f"Errore: {e}"))

        threading.Thread(target=fetch, daemon=True).start()

    def _update_data(self, new_data):
        self.data = new_data
        self._update_filter_options()
        self.filter_data()

    def _update_filter_options(self):
        """Update filter dropdowns to show only available options in current data."""
        # Get unique categories from data
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
        status_map = {"attivo": "Attivo", "in_scadenza": "In Scadenza", "scaduto": "Scaduto"}
        status_values = ["Tutti"] + [status_map.get(s, s.title()) for s in sorted(statuses)]
        self.combo_status["values"] = status_values
        if current_status not in status_values:
            self.combo_status.set("Tutti")

    def filter_data(self):
        query = self.entry_search.get().lower()
        status_filter = self.combo_status.get().lower()
        cat_filter = self.combo_categoria.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        count = 0
        for item in self.data:
            nome = str(item.get("nome") or "").lower()
            corso = str(item.get("corso") or "").lower()
            categoria = str(item.get("categoria") or "").lower()
            stato = str(item.get("stato_certificato") or "").lower()

            # Apply Category Filter
            if cat_filter != "Tutte" and (item.get("categoria") or "").upper() != cat_filter.upper():
                continue

            # Apply Status Filter
            if status_filter != "tutti":
                if status_filter == "in scadenza" and stato != "in_scadenza":
                    continue
                if status_filter == "scaduto" and stato != "scaduto":
                    continue
                if status_filter == "attivo" and stato != "attivo":
                    continue

            # Apply Search Filter
            if query and query not in nome and query not in corso and query not in categoria:
                continue

            scad = item.get("data_scadenza")
            if not scad or scad.lower() == "none":
                scad = "NESSUNA"

            # Prepare values
            values = (
                item.get("id"),
                item.get("nome") or "N/D",
                item.get("corso") or "N/D",
                item.get("categoria") or "ALTRO",
                item.get("data_rilascio") or "",
                scad,
                stato.replace("_", " ").upper()
            )

            # Check advanced column filters
            if hasattr(self.tree, 'check_filter'):
                columns = ["id", "dipendente", "corso", "categoria", "emissione", "scadenza", "stato"]
                skip = False
                for col_idx, col in enumerate(columns):
                    if not self.tree.check_filter(col, values[col_idx]):
                        skip = True
                        break
                if skip:
                    continue

            # Determine row tag for coloring
            tag = stato.replace(" ", "_") if stato in ["attivo", "in_scadenza", "scaduto"] else ""

            self.tree.insert("", "end", values=values, tags=(tag,))
            count += 1

        self.lbl_count.config(text=f"{count} certificati")

    def open_file(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        item_vals = self.tree.item(selected[0], "values")
        cert_id = item_vals[0]

        # Find full object
        cert = next((x for x in self.data if str(x["id"]) == str(cert_id)), None)
        if not cert:
            return

        # Find path
        try:
            db_path = settings.DOCUMENTS_FOLDER
            if not db_path:
                messagebox.showerror("Errore", "Percorso Database non configurato.")
                return

            # Helper for find_document
            search_data = {
                'nome': cert.get('nome'),
                'matricola': cert.get('matricola'),
                'categoria': cert.get('categoria'),
                'data_scadenza': cert.get('data_scadenza')
            }

            path = find_document(db_path, search_data)
            if path and os.path.exists(path):
                open_file(path)
            else:
                # Build helpful message
                msg = "File PDF non trovato.\n\n"
                msg += f"Dipendente: {search_data.get('nome', 'N/D')}\n"
                msg += f"Matricola: {search_data.get('matricola', 'N/D')}\n"
                msg += f"Categoria: {search_data.get('categoria', 'N/D')}\n"
                msg += f"\nPercorso database: {db_path}\n"
                msg += "\nAssicurarsi che il file PDF sia stato importato correttamente."
                messagebox.showwarning("Attenzione", msg)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile aprire il file: {e}")

    def open_folder(self, event=None):
        """Open the folder containing the PDF file."""
        selected = self.tree.selection()
        if not selected:
            return

        item_vals = self.tree.item(selected[0], "values")
        cert_id = item_vals[0]

        cert = next((x for x in self.data if str(x["id"]) == str(cert_id)), None)
        if not cert:
            return

        try:
            db_path = settings.DOCUMENTS_FOLDER
            if not db_path:
                messagebox.showerror("Errore", "Percorso Database non configurato.")
                return

            search_data = {
                'nome': cert.get('nome'),
                'matricola': cert.get('matricola'),
                'categoria': cert.get('categoria'),
                'data_scadenza': cert.get('data_scadenza')
            }

            path = find_document(db_path, search_data)
            if path and os.path.exists(path):
                folder = os.path.dirname(path)
                open_file(folder)
            else:
                # Open base documents folder
                docs_folder = os.path.join(db_path, "DOCUMENTI DIPENDENTI")
                if os.path.exists(docs_folder):
                    open_file(docs_folder)
                else:
                    open_file(db_path)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile aprire la cartella: {e}")

    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            return

        item_vals = self.tree.item(selected[0], "values")
        cert_id = item_vals[0]

        cert = next((x for x in self.data if str(x["id"]) == str(cert_id)), None)
        if not cert:
            return

        EditCertificatoDialog(self, self.controller, cert)

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            return

        count = len(selected)
        msg = f"Eliminare {count} certificato/i selezionato/i?" if count > 1 else "Eliminare il certificato selezionato?"

        if not messagebox.askyesno("Conferma", msg):
            return

        # Get cert IDs
        cert_ids = []
        for sel in selected:
            vals = self.tree.item(sel, "values")
            cert_ids.append(vals[0])

        if count == 1:
            # Single delete - no progress bar needed
            try:
                self.controller.api_client.delete_certificato(cert_ids[0])
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Errore", str(e))
        else:
            # Batch delete with progress bar
            runner = ProgressTaskRunner(
                self,
                "Eliminazione in corso",
                f"Eliminazione di {count} certificati..."
            )

            try:
                result = runner.run(self._delete_single_cert, cert_ids)

                success = sum(1 for r in result.get("results", []) if r.get("success"))
                errors = [r.get("error") for r in result.get("results", []) if not r.get("success")]

                msg = f"Eliminati: {success}/{count}"
                if errors:
                    msg += f"\n\nErrori: {len(errors)}"

                messagebox.showinfo("Risultato", msg)
                self.refresh_data()

            except Exception as e:
                messagebox.showerror("Errore", str(e))

    def _delete_single_cert(self, cert_id):
        """Delete a single certificate."""
        self.controller.api_client.delete_certificato(cert_id)
        return cert_id
