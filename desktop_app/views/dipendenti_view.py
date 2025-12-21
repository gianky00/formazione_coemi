import tkinter as tk
from tkinter import ttk, messagebox
from desktop_app.utils import TaskRunner

class DipendentiView(tk.Frame):
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
        tk.Button(toolbar, text="➕ Nuovo Dipendente", bg="#10B981", fg="white", command=self.add_dipendente).pack(side="left", padx=10)

        # Search
        tk.Label(toolbar, text="Cerca:", bg="#F3F4F6").pack(side="left", padx=10)
        self.entry_search = tk.Entry(toolbar)
        self.entry_search.pack(side="left")
        self.entry_search.bind("<KeyRelease>", lambda e: self.filter_data())

        # Treeview
        columns = ("id", "matricola", "nome", "data_nascita", "mansione")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("matricola", text="Matricola")
        self.tree.heading("nome", text="Nome e Cognome")
        self.tree.heading("data_nascita", text="Data Nascita")
        self.tree.heading("mansione", text="Mansione")

        self.tree.column("id", width=50)
        self.tree.column("matricola", width=100)
        self.tree.column("nome", width=250)
        self.tree.column("data_nascita", width=100)
        self.tree.column("mansione", width=150)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Double-1>", self.on_double_click)

    def refresh_data(self):
        runner = TaskRunner(self, "Caricamento", "Recupero anagrafica...")
        try:
            self.data = runner.run(self.controller.api_client.get_dipendenti_list)
            self.filter_data()
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare dati: {e}")

    def filter_data(self):
        query = self.entry_search.get().lower()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for d in self.data:
            nome = (d.get("nome") or "").lower()
            matricola = (d.get("matricola") or "").lower()

            if query in nome or query in matricola:
                values = (
                    d.get("id"),
                    d.get("matricola") or "",
                    d.get("nome") or "",
                    d.get("data_nascita") or "",
                    d.get("mansione") or ""
                )
                self.tree.insert("", "end", values=values)

    def add_dipendente(self):
        DipendenteDialog(self, self.controller)

    def on_double_click(self, event):
        item = self.tree.selection()
        if not item: return

        # Get ID
        vals = self.tree.item(item, "values")
        dip_id = vals[0]

        # Find full object
        dip_obj = next((x for x in self.data if str(x["id"]) == str(dip_id)), None)
        if dip_obj:
            DipendenteDialog(self, self.controller, dip_obj)

class DipendenteDialog(tk.Toplevel):
    def __init__(self, parent, controller, dip_data=None):
        super().__init__(parent)
        self.controller = controller
        self.dip_data = dip_data
        self.parent_view = parent

        self.title("Dipendente" if dip_data else "Nuovo Dipendente")
        self.geometry("400x400")

        self.setup_ui()

        # Center
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (200)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (200)
        self.geometry(f"+{x}+{y}")

    def setup_ui(self):
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        self.entry_nome = self._add_field(frame, "Nome e Cognome:", self.dip_data.get("nome") if self.dip_data else "")
        self.entry_matricola = self._add_field(frame, "Matricola:", self.dip_data.get("matricola") if self.dip_data else "")
        self.entry_nascita = self._add_field(frame, "Data Nascita (YYYY-MM-DD):", self.dip_data.get("data_nascita") if self.dip_data else "")
        self.entry_mansione = self._add_field(frame, "Mansione:", self.dip_data.get("mansione") if self.dip_data else "")
        self.entry_reparto = self._add_field(frame, "Reparto:", self.dip_data.get("reparto") if self.dip_data else "")

        # Buttons
        btn_frame = tk.Frame(frame, pady=20)
        btn_frame.pack(fill="x", side="bottom")

        tk.Button(btn_frame, text="SALVA", bg="#1D4ED8", fg="white", font=("Segoe UI", 10, "bold"),
                  command=self.save).pack(side="right", padx=5)

        if self.dip_data:
            tk.Button(btn_frame, text="ELIMINA", bg="#DC2626", fg="white", font=("Segoe UI", 10, "bold"),
                      command=self.delete).pack(side="left", padx=5)

    def _add_field(self, parent, label, value):
        tk.Label(parent, text=label, anchor="w").pack(fill="x", pady=(10, 0))
        e = tk.Entry(parent)
        if value:
            e.insert(0, str(value))
        e.pack(fill="x", pady=(0, 5))
        return e

    def save(self):
        data = {
            "nome": self.entry_nome.get(),
            "matricola": self.entry_matricola.get(),
            "data_nascita": self.entry_nascita.get(), # Backend handles format validation
            "mansione": self.entry_mansione.get(),
            "reparto": self.entry_reparto.get()
        }

        if not data["nome"]:
            messagebox.showerror("Errore", "Il nome è obbligatorio.")
            return

        try:
            if self.dip_data:
                self.controller.api_client.update_dipendente(self.dip_data["id"], data)
            else:
                self.controller.api_client.create_dipendente(data)

            self.parent_view.refresh_data()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare: {e}")

    def delete(self):
        if messagebox.askyesno("Conferma", "Eliminare definitivamente questo dipendente?"):
            try:
                self.controller.api_client.delete_dipendente(self.dip_data["id"])
                self.parent_view.refresh_data()
                self.destroy()
            except Exception as e:
                messagebox.showerror("Errore", str(e))
