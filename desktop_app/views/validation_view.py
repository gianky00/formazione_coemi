import tkinter as tk
from tkinter import ttk, messagebox, Menu
from desktop_app.utils import TaskRunner, ProgressTaskRunner, open_file
from desktop_app.widgets.advanced_filter import setup_filterable_treeview
import requests
import os
import threading
from app.services.document_locator import find_document
from app.core.config import settings
from app.core.constants import CATEGORIE_STATICHE  # Used in ValidationDialog


class ValidationView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.data = []
        self.orphan_data = []

        self.setup_ui()
        self.setup_keyboard_shortcuts()

    def setup_ui(self):
        # Sub-notebook for "Da Convalidare" and "Orfani"
        self.sub_notebook = ttk.Notebook(self)
        self.sub_notebook.pack(fill="both", expand=True)

        # Tab 1: Da Convalidare
        self.tab_validate = tk.Frame(self.sub_notebook)
        self.sub_notebook.add(self.tab_validate, text=" Da Convalidare")

        # Tab 2: Orfani
        self.tab_orphans = tk.Frame(self.sub_notebook)
        self.sub_notebook.add(self.tab_orphans, text=" Orfani (Non Associati)")

        self._setup_validation_tab()
        self._setup_orphans_tab()

        # Tab change binding
        self.sub_notebook.bind("<<NotebookTabChanged>>", self._on_subtab_changed)

    def _setup_validation_tab(self):
        """Setup the main validation tab."""
        # Toolbar
        toolbar = tk.Frame(self.tab_validate, bg="#F3F4F6", pady=10)
        toolbar.pack(fill="x")

        tk.Button(toolbar, text="Aggiorna", command=self.refresh_data).pack(side="left", padx=10)
        tk.Label(toolbar, text="Certificati in attesa di convalida", bg="#F3F4F6", font=("Segoe UI", 10, "italic")).pack(side="left", padx=10)

        # Search
        tk.Label(toolbar, text="Cerca:", bg="#F3F4F6").pack(side="left", padx=(20, 5))
        self.entry_search = ttk.Entry(toolbar, width=25)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<KeyRelease>", lambda e: self.filter_data())

        # Category Filter (populated dynamically from data)
        tk.Label(toolbar, text="Categoria:", bg="#F3F4F6").pack(side="left", padx=(15, 5))
        self.combo_categoria = ttk.Combobox(toolbar, values=["Tutte"], state="readonly", width=25)
        self.combo_categoria.set("Tutte")
        self.combo_categoria.pack(side="left", padx=5)
        self.combo_categoria.bind("<<ComboboxSelected>>", lambda e: self.filter_data())

        # Results count
        self.lbl_count = tk.Label(toolbar, text="", bg="#F3F4F6", font=("Segoe UI", 9))
        self.lbl_count.pack(side="right", padx=10)

        # Treeview
        columns = ("id", "dipendente", "corso", "categoria", "emissione", "scadenza")
        self.tree = ttk.Treeview(self.tab_validate, columns=columns, show="headings", selectmode="extended")

        self.tree.heading("id", text="ID")
        self.tree.heading("dipendente", text="Dipendente")
        self.tree.heading("corso", text="Documento")
        self.tree.heading("categoria", text="Categoria")
        self.tree.heading("emissione", text="Data Rilascio")
        self.tree.heading("scadenza", text="Data Scadenza")

        # Optimized column widths
        self.tree.column("id", width=50, minwidth=40, stretch=False, anchor="center")
        self.tree.column("dipendente", width=180, minwidth=120)
        self.tree.column("corso", width=300, minwidth=150)
        self.tree.column("categoria", width=150, minwidth=100)
        self.tree.column("emissione", width=100, minwidth=80, anchor="center")
        self.tree.column("scadenza", width=100, minwidth=80, anchor="center")

        # Row color tags (alternating for better readability)
        self.tree.tag_configure("odd", background="#F9FAFB")
        self.tree.tag_configure("even", background="#FFFFFF")

        scrollbar = ttk.Scrollbar(self.tab_validate, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Context Menu
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Apri File PDF", command=self.open_file, accelerator="Enter")
        self.context_menu.add_command(label="Apri Cartella", command=self.open_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Convalida", command=lambda: self.on_double_click(None), accelerator="F2")
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Elimina", command=self.delete_selected, accelerator="Del")

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.on_double_click)

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
            "scadenza": "Data Scadenza"
        }
        setup_filterable_treeview(self.tree, column_names)
        self.tree.bind("<<FilterChanged>>", lambda e: self.filter_data())

    def _setup_orphans_tab(self):
        """Setup the orphan certificates tab."""
        # Toolbar
        toolbar = tk.Frame(self.tab_orphans, bg="#FEF3C7", pady=10)
        toolbar.pack(fill="x")

        tk.Button(toolbar, text="Aggiorna", command=self.refresh_data).pack(side="left", padx=10)

        # Warning message
        tk.Label(toolbar, text="\u26A0 Certificati non associati a nessun dipendente",
                 bg="#FEF3C7", fg="#92400E", font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)

        # Action buttons
        tk.Button(toolbar, text="Assegna a Dipendente", bg="#2563EB", fg="white",
                  font=("Segoe UI", 9), command=self._assign_orphan).pack(side="right", padx=10)
        tk.Button(toolbar, text="Elimina Selezionati", bg="#DC2626", fg="white",
                  font=("Segoe UI", 9), command=self._delete_orphans).pack(side="right", padx=5)

        # Count label
        self.lbl_orphan_count = tk.Label(toolbar, text="", bg="#FEF3C7", font=("Segoe UI", 9))
        self.lbl_orphan_count.pack(side="right", padx=10)

        # Treeview for orphans
        columns = ("id", "nome_raw", "corso", "categoria", "emissione", "scadenza")
        self.tree_orphans = ttk.Treeview(self.tab_orphans, columns=columns, show="headings", selectmode="extended")

        self.tree_orphans.heading("id", text="ID")
        self.tree_orphans.heading("nome_raw", text="Nome Rilevato (PDF)")
        self.tree_orphans.heading("corso", text="Documento")
        self.tree_orphans.heading("categoria", text="Categoria")
        self.tree_orphans.heading("emissione", text="Data Rilascio")
        self.tree_orphans.heading("scadenza", text="Data Scadenza")

        self.tree_orphans.column("id", width=50, minwidth=40, stretch=False, anchor="center")
        self.tree_orphans.column("nome_raw", width=200, minwidth=150)
        self.tree_orphans.column("corso", width=280, minwidth=150)
        self.tree_orphans.column("categoria", width=150, minwidth=100)
        self.tree_orphans.column("emissione", width=100, minwidth=80, anchor="center")
        self.tree_orphans.column("scadenza", width=100, minwidth=80, anchor="center")

        # Tag for orphan rows
        self.tree_orphans.tag_configure("orphan", background="#FEF3C7")

        scrollbar = ttk.Scrollbar(self.tab_orphans, orient="vertical", command=self.tree_orphans.yview)
        self.tree_orphans.configure(yscroll=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree_orphans.pack(fill="both", expand=True)

        # Double-click to assign
        self.tree_orphans.bind("<Double-1>", lambda e: self._assign_orphan())

    def _on_subtab_changed(self, event):
        """Handle sub-tab changes."""
        pass  # Data is loaded together in refresh_data

    def _assign_orphan(self):
        """Open dialog to assign orphan certificate to an employee."""
        selected = self.tree_orphans.selection()
        if not selected:
            messagebox.showwarning("Attenzione", "Seleziona almeno un certificato orfano da assegnare.")
            return

        # Get list of employees for selection
        try:
            dipendenti = self.controller.api_client.get_dipendenti_list()
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare dipendenti: {e}")
            return

        AssignOrphanDialog(self, self.controller, selected, self.orphan_data, dipendenti)

    def _delete_orphans(self):
        """Delete selected orphan certificates."""
        selected = self.tree_orphans.selection()
        if not selected:
            messagebox.showwarning("Attenzione", "Seleziona almeno un certificato da eliminare.")
            return

        count = len(selected)
        if not messagebox.askyesno("Conferma", f"Eliminare {count} certificato/i orfano/i?"):
            return

        # Get cert IDs
        cert_ids = []
        for sel in selected:
            vals = self.tree_orphans.item(sel, "values")
            cert_ids.append(vals[0])

        try:
            from desktop_app.utils import ProgressTaskRunner
            runner = ProgressTaskRunner(self, "Eliminazione", f"Eliminazione di {count} certificati...")
            runner.run(self._delete_single_cert, cert_ids)
            self.refresh_data()
            messagebox.showinfo("Completato", f"Eliminati {count} certificati orfani.")
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common actions."""
        self.tree.bind("<Return>", self.open_file)
        self.tree.bind("<F2>", lambda e: self.on_double_click(None))
        self.tree.bind("<F5>", lambda e: self.refresh_data())
        self.tree.bind("<Delete>", lambda e: self.delete_selected())
        self.tree.bind("<Control-a>", self.select_all)
        self.tree.bind("<Control-f>", lambda e: self.entry_search.focus_set())

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
        for c in self.tree["columns"]:
            heading_text = {"id": "ID", "dipendente": "Dipendente", "corso": "Documento",
                           "categoria": "Categoria", "emissione": "Data Rilascio", "scadenza": "Data Scadenza"}.get(c, c)
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
            if item not in self.tree.selection():
                self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def open_file(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        item_vals = self.tree.item(selected[0], "values")
        cert_id = item_vals[0]

        cert = next((x for x in self.data if str(x.get("id")) == str(cert_id)), None)
        if not cert:
            return

        try:
            db_path = settings.DOCUMENTS_FOLDER
            if not db_path:
                messagebox.showerror("Errore", "Percorso Database non configurato.")
                return

            search_name = cert.get('nome') or cert.get('nome_dipendente_raw')

            search_data = {
                'nome': search_name,
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

        cert = next((x for x in self.data if str(x.get("id")) == str(cert_id)), None)
        if not cert:
            return

        try:
            db_path = settings.DOCUMENTS_FOLDER
            if not db_path:
                messagebox.showerror("Errore", "Percorso Database non configurato.")
                return

            search_name = cert.get('nome') or cert.get('nome_dipendente_raw')

            search_data = {
                'nome': search_name,
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

    def delete_selected(self, event=None):
        """Delete selected certificates."""
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
            try:
                self.controller.api_client.delete_certificato(cert_ids[0])
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Errore", str(e))
        else:
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

    def refresh_data(self):
        def fetch():
            try:
                new_data = self.controller.api_client.get("certificati", params={"validated": "false"})
                if self.winfo_exists():
                    self.after(0, lambda: self._update_data(new_data))
            except Exception as e:
                if self.winfo_exists():
                    self.after(0, lambda: messagebox.showerror("Errore", str(e)))

        threading.Thread(target=fetch, daemon=True).start()

    def _update_data(self, new_data):
        # Separate orphans from regular pending certificates
        self.data = [c for c in new_data if c.get("dipendente_id") or c.get("matricola")]
        self.orphan_data = [c for c in new_data if not c.get("dipendente_id") and not c.get("matricola")]

        self._update_filter_options()
        self.filter_data()
        self._filter_orphans()

    def _update_filter_options(self):
        """Update filter dropdown to show only available options in current data."""
        # Get unique categories from data
        categories = set()

        for item in self.data:
            cat = item.get("categoria")
            if cat:
                categories.add(cat.upper())

        # Update category combobox
        current_cat = self.combo_categoria.get()
        cat_values = ["Tutte"] + sorted(categories)
        self.combo_categoria["values"] = cat_values
        if current_cat not in cat_values:
            self.combo_categoria.set("Tutte")

    def filter_data(self):
        query = self.entry_search.get().lower()
        cat_filter = self.combo_categoria.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        count = 0
        for idx, item in enumerate(self.data):
            nome = str(item.get("nome") or "").lower()
            corso = str(item.get("corso") or "").lower()
            categoria = str(item.get("categoria") or "").lower()

            # Apply Category Filter
            if cat_filter != "Tutte" and (item.get("categoria") or "").upper() != cat_filter.upper():
                continue

            # Apply Search Filter
            if query and query not in nome and query not in corso and query not in categoria:
                continue

            scad = item.get("data_scadenza")
            if not scad or scad.lower() == "none":
                scad = "NESSUNA"

            # Apply advanced column filters
            values = (
                item.get("id"),
                item.get("nome") or "N/D",
                item.get("corso") or "N/D",
                item.get("categoria") or "ALTRO",
                item.get("data_rilascio") or "",
                scad
            )

            # Check column filters
            if hasattr(self.tree, 'check_filter'):
                columns = ["id", "dipendente", "corso", "categoria", "emissione", "scadenza"]
                skip = False
                for col_idx, col in enumerate(columns):
                    if not self.tree.check_filter(col, values[col_idx]):
                        skip = True
                        break
                if skip:
                    continue

            # Alternating row colors
            tag = "odd" if count % 2 == 0 else "even"

            self.tree.insert("", "end", values=values, tags=(tag,))
            count += 1

        self.lbl_count.config(text=f"{count} da convalidare")

    def _filter_orphans(self):
        """Update the orphan certificates tree."""
        # Clear existing items
        for item in self.tree_orphans.get_children():
            self.tree_orphans.delete(item)

        count = 0
        for item in self.orphan_data:
            scad = item.get("data_scadenza")
            if not scad or scad.lower() == "none":
                scad = ""

            values = (
                item.get("id"),
                item.get("nome_dipendente_raw") or item.get("nome") or "Non identificato",
                item.get("corso") or "",
                item.get("categoria") or "ALTRO",
                item.get("data_rilascio") or "",
                scad
            )
            self.tree_orphans.insert("", "end", values=values, tags=("orphan",))
            count += 1

        self.lbl_orphan_count.config(text=f"{count} orfani")

        # Update tab label with count
        if count > 0:
            self.sub_notebook.tab(1, text=f" Orfani ({count})")
        else:
            self.sub_notebook.tab(1, text=" Orfani (Non Associati)")

    def on_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        # Handle multiple selection - validate each one
        if len(selected) > 1:
            self.batch_validate(selected)
        else:
            # Single selection - open dialog
            vals = self.tree.item(selected[0], "values")
            cert_id = vals[0]
            self.open_validation_dialog(cert_id)

    def batch_validate(self, selected_items):
        """Handle batch validation for multiple selected items with progress bar."""
        count = len(selected_items)
        if not messagebox.askyesno("Conferma", f"Convalidare {count} certificati selezionati?"):
            return

        # Get cert IDs from selection
        cert_ids = []
        for item in selected_items:
            vals = self.tree.item(item, "values")
            cert_ids.append(vals[0])

        runner = ProgressTaskRunner(
            self,
            "Convalida in corso",
            f"Convalida di {count} certificati..."
        )

        try:
            result = runner.run(self._validate_single_cert, cert_ids)

            success = sum(1 for r in result.get("results", []) if r.get("success"))
            errors = [r.get("error") for r in result.get("results", []) if not r.get("success")]

            msg = f"Convalidati: {success}/{count}"
            if errors:
                msg += f"\n\nErrori: {len(errors)}"
                if len(errors) <= 3:
                    msg += "\n" + "\n".join(errors)

            messagebox.showinfo("Risultato", msg)
            self.refresh_data()

        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def _validate_single_cert(self, cert_id):
        """Validate a single certificate."""
        url_val = f"{self.controller.api_client.base_url}/certificati/{cert_id}/valida"
        res = requests.put(url_val, headers=self.controller.api_client._get_headers())
        res.raise_for_status()
        return cert_id

    def open_validation_dialog(self, cert_id):
        try:
            cert = next((x for x in self.data if str(x.get("id")) == str(cert_id)), None)
            if not cert:
                return

            ValidationDialog(self, self.controller, cert)
        except Exception as e:
            messagebox.showerror("Errore", str(e))


class ValidationDialog(tk.Toplevel):
    def __init__(self, parent, controller, cert_data):
        super().__init__(parent)
        self.controller = controller
        self.cert = cert_data
        self.parent_view = parent

        self.title(f"Convalida Certificato #{cert_data.get('id')}")
        self.geometry("500x550")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.setup_ui()

        # Center
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (250)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (275)
        self.geometry(f"+{x}+{y}")

    def setup_ui(self):
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        # Fields
        tk.Label(frame, text="Dipendente (Cognome Nome):", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.entry_dip = tk.Entry(frame, width=40)
        self.entry_dip.insert(0, self.cert.get("nome") or "")
        self.entry_dip.pack(anchor="w", pady=(0, 10))

        tk.Label(frame, text="Corso:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.entry_corso = tk.Entry(frame, width=40)
        self.entry_corso.insert(0, self.cert.get("corso") or "")
        self.entry_corso.pack(anchor="w", pady=(0, 10))

        # Categoria as Dropdown
        tk.Label(frame, text="Categoria:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.combo_categoria = ttk.Combobox(frame, values=sorted(CATEGORIE_STATICHE), state="readonly", width=37)
        current_cat = self.cert.get("categoria") or "ALTRO"
        if current_cat in CATEGORIE_STATICHE:
            self.combo_categoria.set(current_cat)
        else:
            self.combo_categoria.set("ALTRO")
        self.combo_categoria.pack(anchor="w", pady=(0, 10))

        tk.Label(frame, text="Data Rilascio (DD/MM/YYYY):", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.entry_ril = tk.Entry(frame, width=40)
        self.entry_ril.insert(0, self.cert.get("data_rilascio") or "")
        self.entry_ril.pack(anchor="w", pady=(0, 10))

        tk.Label(frame, text="Data Scadenza (DD/MM/YYYY):", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.entry_scad = tk.Entry(frame, width=40)
        self.entry_scad.insert(0, self.cert.get("data_scadenza") or "")
        self.entry_scad.pack(anchor="w", pady=(0, 10))

        # Buttons
        btn_frame = tk.Frame(frame, pady=20)
        btn_frame.pack(fill="x", side="bottom")

        tk.Button(btn_frame, text="CONVALIDA", bg="#10B981", fg="white", font=("Segoe UI", 10, "bold"),
                  command=self.validate).pack(side="right", padx=5)

        tk.Button(btn_frame, text="ELIMINA", bg="#DC2626", fg="white", font=("Segoe UI", 10, "bold"),
                  command=self.delete).pack(side="left", padx=5)

    def validate(self):
        # Prepare data
        update_data = {
            "nome": self.entry_dip.get(),
            "corso": self.entry_corso.get(),
            "categoria": self.combo_categoria.get(),
            "data_rilascio": self.entry_ril.get(),
            "data_scadenza": self.entry_scad.get()
        }

        try:
            # 1. Update
            self.controller.api_client.update_certificato(self.cert['id'], update_data)

            # 2. Validate Endpoint (Using PUT as per backend)
            url_val = f"{self.controller.api_client.base_url}/certificati/{self.cert['id']}/valida"
            requests.put(url_val, headers=self.controller.api_client._get_headers())

            messagebox.showinfo("Successo", "Certificato convalidato.")
            self.parent_view.refresh_data()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante la convalida: {e}")

    def delete(self):
        if messagebox.askyesno("Conferma", "Eliminare definitivamente questo certificato?"):
            try:
                self.controller.api_client.delete_certificato(self.cert['id'])
                messagebox.showinfo("Eliminato", "Certificato eliminato.")
                self.parent_view.refresh_data()
                self.destroy()
            except Exception as e:
                messagebox.showerror("Errore", str(e))


class AssignOrphanDialog(tk.Toplevel):
    """Dialog to assign orphan certificates to an employee."""

    def __init__(self, parent, controller, selected_items, orphan_data, dipendenti):
        super().__init__(parent)
        self.controller = controller
        self.parent_view = parent
        self.selected_items = selected_items
        self.orphan_data = orphan_data
        self.dipendenti = dipendenti

        self.title(f"Assegna {len(selected_items)} Certificato/i Orfano/i")
        self.geometry("550x450")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.setup_ui()

        # Center
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (275)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (225)
        self.geometry(f"+{x}+{y}")

    def setup_ui(self):
        frame = tk.Frame(self, padx=20, pady=15)
        frame.pack(fill="both", expand=True)

        # Info about selected certificates
        tk.Label(frame, text=f"Certificati selezionati: {len(self.selected_items)}",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")

        # List of selected certs (summary)
        cert_list = tk.Frame(frame, bg="#FEF3C7", relief="solid", bd=1)
        cert_list.pack(fill="x", pady=10)

        for i, sel in enumerate(self.selected_items[:5]):  # Show max 5
            vals = self.parent_view.tree_orphans.item(sel, "values")
            tk.Label(cert_list, text=f"  \u2022 {vals[1]} - {vals[2]}",
                     bg="#FEF3C7", font=("Segoe UI", 9), anchor="w").pack(fill="x")

        if len(self.selected_items) > 5:
            tk.Label(cert_list, text=f"  ... e altri {len(self.selected_items) - 5}",
                     bg="#FEF3C7", font=("Segoe UI", 9, "italic"), anchor="w").pack(fill="x")

        # Separator
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)

        # Search for employee
        tk.Label(frame, text="Cerca Dipendente:", font=("Segoe UI", 10, "bold")).pack(anchor="w")

        search_frame = tk.Frame(frame)
        search_frame.pack(fill="x", pady=5)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._filter_employees)
        tk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side="left", fill="x", expand=True)

        # Employee listbox
        list_frame = tk.Frame(frame)
        list_frame.pack(fill="both", expand=True, pady=10)

        self.employee_listbox = tk.Listbox(list_frame, font=("Segoe UI", 10), selectmode="single")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.employee_listbox.yview)
        self.employee_listbox.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.employee_listbox.pack(side="left", fill="both", expand=True)

        # Populate employee list
        self._populate_employees()

        # Buttons
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill="x", pady=10)

        tk.Button(btn_frame, text="Annulla", command=self.destroy,
                  font=("Segoe UI", 10), width=12).pack(side="left")

        tk.Button(btn_frame, text="Assegna", bg="#10B981", fg="white",
                  font=("Segoe UI", 10, "bold"), width=15,
                  command=self._assign).pack(side="right")

    def _populate_employees(self, filter_text=""):
        """Populate employee listbox."""
        self.employee_listbox.delete(0, tk.END)
        self.filtered_dipendenti = []

        filter_text = filter_text.lower()

        for dip in self.dipendenti:
            cognome = dip.get("cognome", "")
            nome = dip.get("nome", "")
            matricola = dip.get("matricola", "")
            display = f"{cognome} {nome}".strip()
            if matricola:
                display += f" ({matricola})"

            if filter_text and filter_text not in display.lower():
                continue

            self.employee_listbox.insert(tk.END, display)
            self.filtered_dipendenti.append(dip)

    def _filter_employees(self, *args):
        """Filter employees based on search."""
        self._populate_employees(self.search_var.get())

    def _assign(self):
        """Assign selected certificates to selected employee."""
        selection = self.employee_listbox.curselection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un dipendente.")
            return

        selected_dip = self.filtered_dipendenti[selection[0]]
        dip_id = selected_dip.get("id")
        dip_name = f"{selected_dip.get('cognome', '')} {selected_dip.get('nome', '')}".strip()

        # Confirm
        count = len(self.selected_items)
        if not messagebox.askyesno("Conferma",
                                    f"Assegnare {count} certificato/i a:\n{dip_name}?"):
            return

        # Get cert IDs
        cert_ids = []
        for sel in self.selected_items:
            vals = self.parent_view.tree_orphans.item(sel, "values")
            cert_ids.append(vals[0])

        success = 0
        errors = []

        for cert_id in cert_ids:
            try:
                # Update the certificate with the dipendente_id
                update_data = {
                    "dipendente_id": dip_id,
                    "nome": dip_name
                }
                self.controller.api_client.update_certificato(cert_id, update_data)
                success += 1
            except Exception as e:
                errors.append(str(e))

        # Show result
        if success == count:
            messagebox.showinfo("Completato", f"Assegnati {success} certificati a {dip_name}.")
        else:
            messagebox.showwarning("Parziale", f"Assegnati {success}/{count}.\nErrori: {len(errors)}")

        self.parent_view.refresh_data()
        self.destroy()
