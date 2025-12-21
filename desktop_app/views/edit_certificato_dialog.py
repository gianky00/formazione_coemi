import tkinter as tk
from tkinter import ttk, messagebox
import requests

class EditCertificatoDialog(tk.Toplevel):
    """
    Dialog for editing certificate details.
    Used by DatabaseView.
    """
    def __init__(self, parent, controller, cert_data):
        super().__init__(parent)
        self.controller = controller
        self.cert = cert_data
        self.parent_view = parent

        self.title(f"Modifica Certificato #{cert_data.get('id')}")
        self.geometry("500x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.setup_ui()

        # Center
        self.update_idletasks()
        try:
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (250)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (250)
            self.geometry(f"+{x}+{y}")
        except:
            pass # Fallback if parent not fully drawn

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

        tk.Label(frame, text="Categoria:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.entry_cat = tk.Entry(frame, width=40)
        self.entry_cat.insert(0, self.cert.get("categoria") or "")
        self.entry_cat.pack(anchor="w", pady=(0, 10))

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

        tk.Button(btn_frame, text="SALVA MODIFICHE", bg="#1D4ED8", fg="white", font=("Segoe UI", 10, "bold"),
                  command=self.save).pack(side="right", padx=5)

        tk.Button(btn_frame, text="ANNULLA", command=self.destroy).pack(side="right", padx=5)

    def save(self):
        # Prepare data
        update_data = {
            "nome": self.entry_dip.get(),
            "corso": self.entry_corso.get(),
            "categoria": self.entry_cat.get(),
            "data_rilascio": self.entry_ril.get(),
            "data_scadenza": self.entry_scad.get()
        }

        if not update_data['nome']:
            messagebox.showerror("Errore", "Il nome dipendente è obbligatorio.")
            return

        try:
            # Call API to update
            self.controller.api_client.update_certificato(self.cert['id'], update_data)

            messagebox.showinfo("Successo", "Certificato aggiornato.")
            if hasattr(self.parent_view, 'refresh_data'):
                self.parent_view.refresh_data()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare: {e}")
