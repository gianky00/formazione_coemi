import tkinter as tk
from tkinter import ttk, messagebox, Menu
import threading
import os
from desktop_app.utils import TaskRunner
from app.services.document_locator import find_document
from app.core.config import settings
from desktop_app.views.edit_certificato_dialog import EditCertificatoDialog

class DatabaseView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.data = []

        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        # Toolbar
        toolbar = tk.Frame(self, bg="#F3F4F6", pady=10)
        toolbar.pack(fill="x")

        # Search
        tk.Label(toolbar, text="Cerca:", bg="#F3F4F6").pack(side="left", padx=5)
        self.entry_search = ttk.Entry(toolbar)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<Return>", lambda e: self.filter_data())
        self.entry_search.bind("<KeyRelease>", lambda e: self.filter_data())

        # Filters
        tk.Label(toolbar, text="Stato:", bg="#F3F4F6").pack(side="left", padx=5)
        self.combo_status = ttk.Combobox(toolbar, values=["Tutti", "Attivo", "In Scadenza", "Scaduto"], state="readonly", width=12)
        self.combo_status.set("Tutti")
        self.combo_status.pack(side="left", padx=5)
        self.combo_status.bind("<<ComboboxSelected>>", lambda e: self.filter_data())

        tk.Button(toolbar, text="🔄 Aggiorna", command=self.refresh_data).pack(side="left", padx=10)

        # Treeview
        columns = ("id", "dipendente", "corso", "emissione", "scadenza", "stato")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="extended")

        self.tree.heading("id", text="ID")
        self.tree.heading("dipendente", text="Dipendente")
        self.tree.heading("corso", text="Documento")
        self.tree.heading("emissione", text="Data Rilascio")
        self.tree.heading("scadenza", text="Data Scadenza")
        self.tree.heading("stato", text="Stato")

        self.tree.column("id", width=50, stretch=False)
        self.tree.column("dipendente", width=200)
        self.tree.column("corso", width=200)
        self.tree.column("emissione", width=100)
        self.tree.column("scadenza", width=100)
        self.tree.column("stato", width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Context Menu
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="📂 Apri File", command=self.open_file)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="✏️ Modifica", command=self.edit_item) # Placeholder for future
        self.context_menu.add_command(label="🗑️ Elimina", command=self.delete_item)

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.open_file) # Double click opens file

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def refresh_data(self):
        runner = TaskRunner(self, "Caricamento", "Recupero dati in corso...")
        try:
            self.data = runner.run(self._fetch_data)
            self.filter_data()
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare i dati: {e}")

    def _fetch_data(self):
        return self.controller.api_client.get("certificati", params={"validated": "true"})

    def filter_data(self):
        query = self.entry_search.get().lower()
        status_filter = self.combo_status.get().lower()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for item in self.data:
            nome = str(item.get("nome") or "").lower()
            corso = str(item.get("corso") or "").lower()
            stato = str(item.get("stato_certificato") or "").lower()

            # Apply Filters
            if status_filter != "tutti" and status_filter != stato.replace("_", " "):
                 # Handle specific mappings if needed (e.g. "in_scadenza" vs "In Scadenza")
                 if status_filter == "in scadenza" and stato != "in_scadenza": continue
                 if status_filter == "scaduto" and stato != "scaduto": continue
                 if status_filter == "attivo" and stato != "attivo": continue

            if query in nome or query in corso:
                values = (
                    item.get("id"),
                    item.get("nome") or "N/D",
                    item.get("corso") or "N/D",
                    item.get("data_rilascio") or "",
                    item.get("data_scadenza") or "",
                    item.get("stato_certificato") or ""
                )
                self.tree.insert("", "end", values=values)

    def open_file(self, event=None):
        selected = self.tree.selection()
        if not selected: return

        item_vals = self.tree.item(selected[0], "values")
        cert_id = item_vals[0]

        # Find full object
        cert = next((x for x in self.data if str(x["id"]) == str(cert_id)), None)
        if not cert: return

        # Find path
        try:
            db_path = settings.DATABASE_PATH
            if not db_path:
                 messagebox.showerror("Errore", "Percorso Database non configurato.")
                 return

            # Helper for find_document (similar to ValidationView)
            search_data = {
                'nome': cert.get('nome'),
                'categoria': cert.get('categoria'),
                'data_scadenza': cert.get('data_scadenza')
            }

            path = find_document(db_path, search_data)
            if path and os.path.exists(path):
                os.startfile(path)
            else:
                messagebox.showwarning("Attenzione", f"File PDF non trovato.\nCercato in: {path or 'N/D'}")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile aprire il file: {e}")

    def edit_item(self):
        selected = self.tree.selection()
        if not selected: return

        item_vals = self.tree.item(selected[0], "values")
        cert_id = item_vals[0]

        cert = next((x for x in self.data if str(x["id"]) == str(cert_id)), None)
        if not cert: return

        EditCertificatoDialog(self, self.controller, cert)

    def delete_item(self):
        selected = self.tree.selection()
        if not selected: return
        if messagebox.askyesno("Conferma", "Eliminare il certificato selezionato?"):
            vals = self.tree.item(selected[0], "values")
            cert_id = vals[0]
            try:
                self.controller.api_client.delete_certificato(cert_id)
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Errore", str(e))
