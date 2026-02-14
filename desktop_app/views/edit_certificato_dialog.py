import tkinter as tk
from tkinter import messagebox, ttk

from app.core.constants import CATEGORIE_STATICHE


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
        self.geometry("500x550")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.setup_ui()

        # Center
        self.update_idletasks()
        try:
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (250)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (275)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass  # Fallback if parent not fully drawn

    def setup_ui(self):
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        # Fields
        tk.Label(frame, text="Dipendente (Cognome Nome):", font=("Segoe UI", 9, "bold")).pack(
            anchor="w"
        )
        self.entry_dip = tk.Entry(frame, width=40)
        self.entry_dip.insert(0, self.cert.get("nome") or "")
        self.entry_dip.pack(anchor="w", pady=(0, 10))

        tk.Label(frame, text="Corso:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.entry_corso = tk.Entry(frame, width=40)
        self.entry_corso.insert(0, self.cert.get("corso") or "")
        self.entry_corso.pack(anchor="w", pady=(0, 10))

        # Categoria as Dropdown
        tk.Label(frame, text="Categoria:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.combo_categoria = ttk.Combobox(
            frame, values=sorted(CATEGORIE_STATICHE), state="readonly", width=37
        )
        current_cat = self.cert.get("categoria") or "ALTRO"
        if current_cat in CATEGORIE_STATICHE:
            self.combo_categoria.set(current_cat)
        else:
            self.combo_categoria.set("ALTRO")
        self.combo_categoria.pack(anchor="w", pady=(0, 10))

        tk.Label(frame, text="Data Rilascio (DD/MM/YYYY):", font=("Segoe UI", 9, "bold")).pack(
            anchor="w"
        )
        self.entry_ril = tk.Entry(frame, width=40)
        self.entry_ril.insert(0, self.cert.get("data_rilascio") or "")
        self.entry_ril.pack(anchor="w", pady=(0, 10))

        tk.Label(frame, text="Data Scadenza (DD/MM/YYYY):", font=("Segoe UI", 9, "bold")).pack(
            anchor="w"
        )
        self.entry_scad = tk.Entry(frame, width=40)
        self.entry_scad.insert(0, self.cert.get("data_scadenza") or "")
        self.entry_scad.pack(anchor="w", pady=(0, 10))

        # Buttons
        btn_frame = tk.Frame(frame, pady=20)
        btn_frame.pack(fill="x", side="bottom")

        tk.Button(
            btn_frame,
            text="SALVA MODIFICHE",
            bg="#1D4ED8",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.save,
        ).pack(side="right", padx=5)

        tk.Button(btn_frame, text="ANNULLA", command=self.destroy).pack(side="right", padx=5)

    def save(self):
        # Prepare data
        update_data = {
            "nome": self.entry_dip.get(),
            "corso": self.entry_corso.get(),
            "categoria": self.combo_categoria.get(),
            "data_rilascio": self.entry_ril.get(),
            "data_scadenza": self.entry_scad.get(),
        }

        if not update_data["nome"]:
            messagebox.showerror("Errore", "Il nome dipendente e obbligatorio.")
            return

        try:
            # Call API to update
            self.controller.api_client.update_certificato(self.cert["id"], update_data)

            messagebox.showinfo("Successo", "Certificato aggiornato.")
            if hasattr(self.parent_view, "refresh_data"):
                self.parent_view.refresh_data()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare: {e}")
