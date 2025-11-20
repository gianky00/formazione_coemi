import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
from datetime import date, timedelta
import os

class LicenseAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestore Licenze PyArmor")
        self.root.geometry("750x600") # Increased size
        self.root.resizable(True, True)

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

        row = 0

        # 1. Disk Serial
        ttk.Label(frm_container, text="Disk Serial (dal .bat):").grid(row=row, column=0, sticky="w", pady=5)
        self.ent_disk = ttk.Entry(frm_container, width=60)
        self.ent_disk.grid(row=row, column=1, pady=5, padx=5)
        ttk.Button(frm_container, text="Incolla", command=lambda: self.paste_to(self.ent_disk)).grid(row=row, column=2, padx=5)
        row += 1

        # 2. MAC Address
        ttk.Label(frm_container, text="MAC Address (dal .bat):").grid(row=row, column=0, sticky="w", pady=5)
        self.ent_mac = ttk.Entry(frm_container, width=60)
        self.ent_mac.grid(row=row, column=1, pady=5, padx=5)
        ttk.Button(frm_container, text="Incolla", command=lambda: self.paste_to(self.ent_mac)).grid(row=row, column=2, padx=5)
        row += 1

        # Separator
        ttk.Separator(frm_container, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky="ew", pady=15)
        row += 1

        # 3. PyArmor ID (Advanced/Default)
        ttk.Label(frm_container, text="PyArmor Machine ID (Hash):").grid(row=row, column=0, sticky="w", pady=5)
        self.ent_hwid = ttk.Entry(frm_container, width=60)
        self.ent_hwid.grid(row=row, column=1, pady=5, padx=5)

        # Buttons for PyArmor ID
        frm_btns = ttk.Frame(frm_container)
        frm_btns.grid(row=row, column=2, padx=5, sticky="w")
        ttk.Button(frm_btns, text="Incolla", command=lambda: self.paste_to(self.ent_hwid)).pack(side="left", padx=2)
        ttk.Button(frm_btns, text="Rileva Locale", command=self.get_local_id).pack(side="left", padx=2)
        row += 1

        # Info Label
        lbl_info = ttk.Label(frm_container, text="Nota: Se inserisci più ID, la licenza sarà valida per chiunque ne possieda ALMENO uno.", foreground="gray", font=("Segoe UI", 9, "italic"))
        lbl_info.grid(row=row, column=0, columnspan=3, sticky="w", pady=(0, 10))
        row += 1

        # Expiration
        ttk.Label(frm_container, text="Scadenza (YYYY-MM-DD):").grid(row=row, column=0, sticky="w", pady=5)
        self.ent_date = ttk.Entry(frm_container, width=20)
        self.ent_date.grid(row=row, column=1, sticky="w", pady=5, padx=5)
        self.ent_date.insert(0, (date.today() + timedelta(days=365)).strftime("%Y-%m-%d"))
        row += 1

        # Output Path
        ttk.Label(frm_container, text="Output:").grid(row=row, column=0, sticky="w", pady=5)
        self.lbl_output = ttk.Label(frm_container, text="dist/pyarmor.rkey", foreground="gray")
        self.lbl_output.grid(row=row, column=1, sticky="w", pady=5, padx=5)

        # --- Actions ---
        frm_actions = ttk.Frame(root, padding=20)
        frm_actions.pack(fill="x", side="bottom")

        self.btn_gen = ttk.Button(frm_actions, text="Genera Licenza", command=self.generate)
        self.btn_gen.pack(side="right", padx=5)

        ttk.Button(frm_actions, text="Chiudi", command=root.quit).pack(side="right", padx=5)

    def paste_to(self, entry):
        try:
            text = self.root.clipboard_get()
            entry.delete(0, tk.END)
            entry.insert(0, text)
        except:
            pass

    def get_local_id(self):
        # Try to get ID from built application
        import os
        try:
            # 1. Try Executable
            exe_path = os.path.join("dist", "package", "Intelleo.exe")
            if os.path.exists(exe_path):
                # Run with --hwid
                startupinfo = None
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                res = subprocess.run([exe_path, "--hwid"], capture_output=True, text=True, startupinfo=startupinfo)
                hwid = res.stdout.strip()
                lines = hwid.splitlines()
                if lines:
                    hwid = lines[-1] # Assume last line is the ID

                if hwid and "Error" not in hwid and "N/A" not in hwid:
                    self.ent_hwid.delete(0, tk.END)
                    self.ent_hwid.insert(0, hwid)
                    messagebox.showinfo("Info", f"ID recuperato dall'eseguibile: {hwid}")
                    return
                else:
                    # Show full output for debugging
                    debug_info = f"Output: {res.stdout}\nError: {res.stderr}"
                    messagebox.showwarning("Debug Info", f"Impossibile trovare ID valido.\n{debug_info}\n\nControlla il file 'debug_hwid.log' nella cartella dist/package.")
                    return

            # 2. Try Obfuscated Script (if exe not found)
            launcher_path = os.path.join("dist", "obfuscated", "launcher.py")
            if os.path.exists(launcher_path):
                 res = subprocess.run([sys.executable, launcher_path, "--hwid"], capture_output=True, text=True)
                 hwid = res.stdout.strip()
                 if hwid:
                     lines = hwid.splitlines()
                     hwid = lines[-1]

                 if "N/A" not in hwid and hwid and "Error" not in hwid:
                     self.ent_hwid.delete(0, tk.END)
                     self.ent_hwid.insert(0, hwid)
                     messagebox.showinfo("Info", f"ID recuperato dagli script: {hwid}")
                     return

            messagebox.showwarning("Attenzione", "Impossibile recuperare l'ID Locale.\n\n1. Assicurati di aver compilato l'applicazione (python build_dist.py).\n2. L'ID è disponibile solo nell'applicazione protetta (offuscata).")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante il recupero dell'ID: {e}")

    def generate(self):
        disk = self.ent_disk.get().strip()
        mac = self.ent_mac.get().strip()
        hwid = self.ent_hwid.get().strip()
        expiry = self.ent_date.get().strip()

        if not expiry:
            messagebox.showerror("Errore", "La data di scadenza è obbligatoria.")
            return

        if not (disk or mac or hwid):
             if not messagebox.askyesno("Conferma", "Non hai inserito nessun ID Hardware.\nLa licenza non sarà vincolata all'hardware.\nVuoi procedere?"):
                 return

        # Use sys.executable -m pyarmor.cli to ensure we use the installed module
        cmd = [sys.executable, "-m", "pyarmor.cli", "gen", "key", "-e", expiry]

        # Add bindings
        # PyArmor allows multiple -b. License is valid if ANY matches.
        if disk: cmd.extend(["-b", disk])
        if mac: cmd.extend(["-b", mac])
        if hwid: cmd.extend(["-b", hwid])

        try:
            # Ensure dist folder exists or let pyarmor create it
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                msg = f"Licenza generata con successo!\n\nPercorso: dist/pyarmor.rkey\nScadenza: {expiry}"
                if disk: msg += f"\nDisk Serial: {disk}"
                if mac: msg += f"\nMAC Address: {mac}"
                if hwid: msg += f"\nPyArmor Hash: {hwid}"
                messagebox.showinfo("Successo", msg)
            else:
                messagebox.showerror("Errore PyArmor", f"Impossibile generare la licenza:\n{result.stderr}\n{result.stdout}")

        except FileNotFoundError:
            messagebox.showerror("Errore", "Eseguibile 'pyarmor' non trovato.")
        except Exception as e:
            messagebox.showerror("Errore Imprevisto", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = LicenseAdminApp(root)
    root.mainloop()
