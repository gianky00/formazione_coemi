import tkinter as tk
from tkinter import ttk, messagebox
from desktop_app.utils import TaskRunner

class ScadenzarioView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.data = []
        
        self.setup_ui()
        # self.refresh_data() # Lazy load when tab selected? Or explicit refresh.

    def setup_ui(self):
        # Toolbar
        toolbar = tk.Frame(self, bg="#F3F4F6", pady=10)
        toolbar.pack(fill="x")
        
        tk.Button(toolbar, text="🔄 Aggiorna", command=self.refresh_data).pack(side="left", padx=10)
        tk.Label(toolbar, text="Legenda: 🔴 Scaduto  🟠 In Scadenza (<90gg)  🟢 Valido", bg="#F3F4F6").pack(side="left", padx=20)

        # Treeview
        columns = ("dipendente", "corso", "scadenza", "giorni_rimanenti")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        self.tree.heading("dipendente", text="Dipendente")
        self.tree.heading("corso", text="Documento")
        self.tree.heading("scadenza", text="Scadenza")
        self.tree.heading("giorni_rimanenti", text="Giorni Rimanenti")
        
        # Tags for colors
        self.tree.tag_configure("scaduto", background="#FECACA") # Red-200
        self.tree.tag_configure("in_scadenza", background="#FED7AA") # Orange-200
        self.tree.tag_configure("valido", background="#BBF7D0") # Green-200

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

    def refresh_data(self):
        runner = TaskRunner(self, "Caricamento", "Analisi scadenze...")
        try:
            self.data = runner.run(self._fetch_data)
            self._populate_tree()
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare scadenze: {e}")

    def _fetch_data(self):
        # Fetch validated certificates
        # Sort logic handles locally or backend? Backend logic is better but we use API list.
        # We can sort in python.
        return self.controller.api_client.get("certificati", params={"validated": "true"})

    def _populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Filter logic: Show expired or expiring
        # Assuming backend returns 'stato_certificato' as 'scaduto' or 'in_scadenza'
        # But user might want to see all sorted by date.

        # Sort by expiration date
        def get_date_key(d):
            val = d.get("data_scadenza")
            return val if val else "9999-99-99"

        sorted_data = sorted(self.data, key=get_date_key)

        from datetime import datetime
        today = datetime.now().date()
        
        for item in sorted_data:
            scadenza_str = item.get("data_scadenza")
            status = item.get("stato_certificato")
            
            # Simple color logic
            tag = "valido"
            if status == "scaduto":
                tag = "scaduto"
            elif status == "in_scadenza":
                tag = "in_scadenza"

            # Calc days remaining
            days_str = "N/D"
            if scadenza_str:
                try:
                    # Assuming YYYY-MM-DD from API
                    dt = datetime.strptime(scadenza_str, "%Y-%m-%d").date()
                    delta = (dt - today).days
                    days_str = str(delta)
                except:
                    pass

            values = (
                item.get("nome_dipendente"),
                item.get("nome_corso"),
                scadenza_str,
                days_str
            )
            self.tree.insert("", "end", values=values, tags=(tag,))
