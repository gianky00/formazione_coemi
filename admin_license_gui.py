import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
from datetime import date, timedelta
import os
import shutil

class LicenseAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestore Licenze (Metodo Disk Serial)")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))

        ttk.Label(root, text="Generatore Licenza - Disk Serial", font=("Segoe UI", 14, "bold")).pack(pady=15)

        # Container
        frm = ttk.LabelFrame(root, text="Dati Cliente", padding=20)
        frm.pack(fill="both", expand=True, padx=20, pady=5)

        # Disk Serial
        ttk.Label(frm, text="Seriale Disco (dal cliente):").pack(anchor="w")
        self.ent_disk = ttk.Entry(frm, width=60)
        self.ent_disk.pack(pady=5)
        ttk.Button(frm, text="Incolla dagli appunti", command=self.paste_disk).pack(anchor="e", pady=5)

        # Scadenza
        ttk.Label(frm, text="Data Scadenza (Default: 2 Mesi):").pack(anchor="w", pady=(15, 0))
        self.ent_date = ttk.Entry(frm, width=20)
        self.ent_date.pack(anchor="w", pady=5)
        
        # Default 60 giorni
        scadenza_default = (date.today() + timedelta(days=60)).strftime("%Y-%m-%d")
        self.ent_date.insert(0, scadenza_default)

        # Bottone Genera
        self.btn_gen = ttk.Button(root, text="GENERA LICENZA", command=self.generate)
        self.btn_gen.pack(fill="x", padx=20, pady=20, ipady=10)

    def paste_disk(self):
        try:
            self.ent_disk.delete(0, tk.END)
            self.ent_disk.insert(0, self.root.clipboard_get().strip())
        except: pass

    def generate(self):
        disk_serial = self.ent_disk.get().strip()
        expiry = self.ent_date.get().strip()

        if not disk_serial:
            messagebox.showerror("Errore", "Devi inserire il Seriale del Disco del cliente!")
            return

        # --- CORREZIONE DEFINITIVA ---
        # Usiamo '-b' (binding) invece di '--data'.
        # Questo dice a PyArmor: "Questa licenza vale SOLO per questo disco".
        cmd = [sys.executable, "-m", "pyarmor.cli", "gen", "key", 
               "-e", expiry, 
               "-b", disk_serial] 

        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            
            if res.returncode == 0:
                src = os.path.join("dist", "pyarmor.rkey")
                dst_dir = os.path.join("dist", "package")
                dst = os.path.join(dst_dir, "pyarmor.rkey")
                
                if os.path.exists(src):
                    if not os.path.exists(dst_dir): os.makedirs(dst_dir)
                    if os.path.exists(dst): os.remove(dst)
                    shutil.move(src, dst)
                    
                    msg = f"Licenza GENERATA!\n\nScadenza: {expiry}\nVincolo Hardware: {disk_serial}\n\nSalvata in: {dst}"
                    messagebox.showinfo("Successo", msg)
                else:
                    messagebox.showerror("Errore", "File licenza non trovato.")
            else:
                messagebox.showerror("Errore PyArmor", f"Dettagli errore:\n{res.stderr}")

        except Exception as e:
            messagebox.showerror("Errore", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    LicenseAdminApp(root)
    root.mainloop()