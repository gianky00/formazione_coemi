import tkinter as tk
from tkinter import ttk, messagebox
import threading
from desktop_app.utils import TaskRunner

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
        self.entry_search.bind("<KeyRelease>", lambda e: self.filter_data()) # Real-time filter

        # Refresh
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

    def refresh_data(self):
        # Use TaskRunner to fetch data safely
        runner = TaskRunner(self, "Caricamento", "Recupero dati in corso...")
        try:
            self.data = runner.run(self._fetch_data)
            self.filter_data()
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare i dati: {e}")

    def _fetch_data(self):
        # Only fetch validated certificates for the main DB view
        return self.controller.api_client.get("certificati", params={"validated": "true"})

    def filter_data(self):
        query = self.entry_search.get().lower()

        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        for item in self.data:
            # Safe access to fields
            nome = str(item.get("nome_dipendente") or "").lower()
            corso = str(item.get("nome_corso") or "").lower()

            if query in nome or query in corso:
                values = (
                    item.get("id"),
                    item.get("nome_dipendente") or "N/D",
                    item.get("nome_corso") or "N/D",
                    item.get("data_rilascio") or "",
                    item.get("data_scadenza") or "",
                    item.get("stato_certificato") or ""
                )
                self.tree.insert("", "end", values=values)

