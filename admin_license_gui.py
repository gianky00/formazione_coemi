import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from datetime import date, timedelta

class LicenseAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestore Licenze PyArmor")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        style = ttk.Style()
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10))

        # --- Header ---
        lbl_header = ttk.Label(root, text="Generatore Licenze", font=("Segoe UI", 16, "bold"))
        lbl_header.pack(pady=20)

        # --- Form ---
        frm_container = ttk.Frame(root, padding=20)
        frm_container.pack(fill="both", expand=True)

        # HW ID
        ttk.Label(frm_container, text="Hardware ID (Opzionale):").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_hwid = ttk.Entry(frm_container, width=50)
        self.ent_hwid.grid(row=0, column=1, pady=5, padx=5)
        self.ent_hwid.bind("<Control-v>", lambda e: self.paste_hwid()) # Bind paste shortcut
        ttk.Button(frm_container, text="Incolla", command=self.paste_hwid).grid(row=0, column=2, padx=5)

        # Expiration
        ttk.Label(frm_container, text="Scadenza (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_date = ttk.Entry(frm_container, width=20)
        self.ent_date.grid(row=1, column=1, sticky="w", pady=5, padx=5)
        self.ent_date.insert(0, (date.today() + timedelta(days=365)).strftime("%Y-%m-%d"))

        # Output Path
        ttk.Label(frm_container, text="Output:").grid(row=2, column=0, sticky="w", pady=5)
        self.lbl_output = ttk.Label(frm_container, text="dist/pyarmor.rkey", foreground="gray")
        self.lbl_output.grid(row=2, column=1, sticky="w", pady=5, padx=5)

        # --- Actions ---
        frm_actions = ttk.Frame(root, padding=20)
        frm_actions.pack(fill="x", side="bottom")

        self.btn_gen = ttk.Button(frm_actions, text="Genera Licenza", command=self.generate)
        self.btn_gen.pack(side="right", padx=5)

        ttk.Button(frm_actions, text="Chiudi", command=root.quit).pack(side="right", padx=5)

    def paste_hwid(self):
        try:
            text = self.root.clipboard_get()
            self.ent_hwid.delete(0, tk.END)
            self.ent_hwid.insert(0, text)
        except:
            pass

    def generate(self):
        hw_id = self.ent_hwid.get().strip()
        expiry = self.ent_date.get().strip()

        if not expiry:
            messagebox.showerror("Errore", "La data di scadenza è obbligatoria.")
            return

        # Check if pyarmor is available
        # Use sys.executable -m pyarmor.cli to ensure we use the installed module
        cmd = [sys.executable, "-m", "pyarmor.cli", "gen", "key", "-e", expiry]
        if hw_id:
            cmd.extend(["-b", hw_id])

        try:
            # Ensure dist folder exists or let pyarmor create it
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                msg = f"Licenza generata con successo!\n\nPercorso: dist/pyarmor.rkey\nScadenza: {expiry}"
                if hw_id:
                    msg += f"\nVincolata a HWID: {hw_id}"
                messagebox.showinfo("Successo", msg)
            else:
                messagebox.showerror("Errore PyArmor", f"Impossibile generare la licenza:\n{result.stderr}\n{result.stdout}")

        except FileNotFoundError:
            messagebox.showerror("Errore", "Eseguibile 'pyarmor' non trovato nel PATH.\nAssicurati di aver installato pyarmor.")
        except Exception as e:
            messagebox.showerror("Errore Imprevisto", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = LicenseAdminApp(root)
    root.mainloop()
