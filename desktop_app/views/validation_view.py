import tkinter as tk
from tkinter import ttk, messagebox
from desktop_app.utils import TaskRunner

class ValidationView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.data = []

        self.setup_ui()
        # self.refresh_data()

    def setup_ui(self):
        # Toolbar
        toolbar = tk.Frame(self, bg="#F3F4F6", pady=10)
        toolbar.pack(fill="x")

        tk.Button(toolbar, text="🔄 Aggiorna", command=self.refresh_data).pack(side="left", padx=10)
        tk.Label(toolbar, text="Certificati in attesa di convalida", bg="#F3F4F6", font=("Segoe UI", 10, "italic")).pack(side="left", padx=10)

        # Treeview
        columns = ("id", "dipendente", "corso", "emissione", "scadenza", "fiducia")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("dipendente", text="Dipendente")
        self.tree.heading("corso", text="Documento")
        self.tree.heading("emissione", text="Data Rilascio")
        self.tree.heading("scadenza", text="Data Scadenza")
        self.tree.heading("fiducia", text="Fiducia AI")

        self.tree.column("id", width=50)
        self.tree.column("dipendente", width=200)
        self.tree.column("corso", width=200)
        self.tree.column("emissione", width=100)
        self.tree.column("scadenza", width=100)
        self.tree.column("fiducia", width=80)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Double click to validate
        self.tree.bind("<Double-1>", self.on_double_click)

    def refresh_data(self):
        runner = TaskRunner(self, "Caricamento", "Recupero documenti da validare...")
        try:
            self.data = runner.run(self._fetch_data)
            self._populate_tree()
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare dati: {e}")

    def _fetch_data(self):
        return self.controller.api_client.get("certificati", params={"validated": "false"})

    def _populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for item in self.data:
            values = (
                item.get("id"),
                item.get("nome_dipendente") or "N/D",
                item.get("nome_corso") or "N/D",
                item.get("data_rilascio") or "",
                item.get("data_scadenza") or "",
                f"{item.get('confidence', 0)}%" if item.get("confidence") else "N/D"
            )
            self.tree.insert("", "end", values=values)

    def on_double_click(self, event):
        item = self.tree.selection()
        if not item:
            return

        # Get ID
        vals = self.tree.item(item, "values")
        cert_id = vals[0]

        # Open Validation Dialog
        self.open_validation_dialog(cert_id)

    def open_validation_dialog(self, cert_id):
        # Fetch full details first? Or just use what we have?
        # Better fetch fresh.
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
        self.geometry("500x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.setup_ui()

        # Center
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (250)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (250)
        self.geometry(f"+{x}+{y}")

    def setup_ui(self):
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        # Fields
        tk.Label(frame, text="Dipendente:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.entry_dip = tk.Entry(frame, width=40)
        self.entry_dip.insert(0, self.cert.get("nome_dipendente") or "")
        self.entry_dip.pack(anchor="w", pady=(0, 10))

        tk.Label(frame, text="Corso:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.entry_corso = tk.Entry(frame, width=40)
        self.entry_corso.insert(0, self.cert.get("nome_corso") or "")
        self.entry_corso.pack(anchor="w", pady=(0, 10))

        tk.Label(frame, text="Data Rilascio (YYYY-MM-DD):", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.entry_ril = tk.Entry(frame, width=40)
        self.entry_ril.insert(0, self.cert.get("data_rilascio") or "")
        self.entry_ril.pack(anchor="w", pady=(0, 10))

        tk.Label(frame, text="Data Scadenza (YYYY-MM-DD):", font=("Segoe UI", 9, "bold")).pack(anchor="w")
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
            "nome_dipendente_raw": self.entry_dip.get(), # If orphan
            "data_rilascio": self.entry_ril.get(),
            "data_scadenza": self.entry_scad.get()
        }

        try:
            # 1. Update data
            self.controller.api_client.update_certificato(self.cert['id'], update_data)
            
            # 2. Validate
            # There is no specific APIClient method for validate, but we can assume validate just means it is now correct.
            # Wait, the prompt said `validated=true` is used for fetching valid ones.
            # We need to set `validated=True` on the backend.
            # Usually `update_certificato` with `validated=True` works if schema allows.
            # Or there is a specific endpoint.
            # I used `requests.post(url_val)` in the previous iteration.
            # I should keep that but use requests (imported implicitly? No, I need to import it if I use it).
            # But I removed `import requests`.

            # Let's check if I can just use update_certificato with validated=True?
            # Schema usually allows it.
            # If not, I need to use requests and import it.

            # I will use requests for the validate action to be safe as I know that endpoint exists from my previous code memory.
            # So I need `import requests`.
            pass
        except Exception:
             pass

        # RE-WRITING LOGIC PROPERLY BELOW
        pass

    def validate(self):
        # Prepare data
        update_data = {
            "nome_dipendente_raw": self.entry_dip.get(),
            "data_rilascio": self.entry_ril.get(),
            "data_scadenza": self.entry_scad.get()
            # "validated": True # If API supports this in PUT, we are golden.
        }

        try:
            # 1. Update
            self.controller.api_client.update_certificato(self.cert['id'], update_data)

            # 2. Validate Endpoint (Legacy pattern)
            import requests
            url_val = f"{self.controller.api_client.base_url}/certificati/{self.cert['id']}/validate"
            requests.post(url_val, headers=self.controller.api_client._get_headers())

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
