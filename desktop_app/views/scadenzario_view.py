import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from desktop_app.utils import TaskRunner
import os

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

        # Actions
        tk.Button(toolbar, text="📄 Esporta PDF", bg="#2563EB", fg="white", command=self.export_pdf).pack(side="left", padx=10)
        tk.Button(toolbar, text="📧 Invia Email Report", bg="#2563EB", fg="white", command=self.send_email).pack(side="left", padx=10)

        tk.Label(toolbar, text="Legenda: 🔴 Scaduto  🟠 In Scadenza (<90gg)  🟢 Valido", bg="#F3F4F6").pack(side="right", padx=20)

        # Treeview
        columns = ("dipendente", "corso", "scadenza", "giorni_rimanenti")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        self.tree.heading("dipendente", text="Dipendente")
        self.tree.heading("corso", text="Documento")
        self.tree.heading("scadenza", text="Scadenza")
        self.tree.heading("giorni_rimanenti", text="Giorni Rimanenti")

        self.tree.column("dipendente", width=250)
        self.tree.column("corso", width=300)
        self.tree.column("scadenza", width=120)
        self.tree.column("giorni_rimanenti", width=120)

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
        return self.controller.api_client.get("certificati", params={"validated": "true"})

    def _populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

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
                    dt = datetime.strptime(scadenza_str, "%d/%m/%Y").date()
                    delta = (dt - today).days
                    days_str = str(delta)
                except:
                    pass

            values = (
                item.get("nome"),
                item.get("corso"),
                scadenza_str,
                days_str
            )
            self.tree.insert("", "end", values=values, tags=(tag,))

    def export_pdf(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not file_path:
            return

        runner = TaskRunner(self, "Esportazione", "Generazione PDF in corso...")
        try:
            # We need to call API to get PDF bytes
            # GET /notifications/export-report
            # api_client.get returns JSON. We need raw bytes.
            # We use requests manually here or extend api_client.
            # I'll use manual requests for binary download to keep api_client simple for now (or I could add download_file).

            def task():
                import requests
                url = f"{self.controller.api_client.base_url}/notifications/export-report"
                res = requests.get(url, headers=self.controller.api_client._get_headers())
                res.raise_for_status()
                with open(file_path, "wb") as f:
                    f.write(res.content)

            runner.run(task)
            messagebox.showinfo("Successo", f"PDF salvato in: {file_path}")
            os.startfile(file_path)

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
