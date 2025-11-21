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
        self.root.title("Gestore Licenze (Admin)")
        self.root.geometry("600x480")
        self.root.resizable(False, False)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))

        ttk.Label(root, text="Generatore Licenza Cliente", font=("Segoe UI", 14, "bold")).pack(pady=15)

        # Container
        frm = ttk.LabelFrame(root, text="Dati Cliente", padding=20)
        frm.pack(fill="both", expand=True, padx=20, pady=5)

        # Disk Serial
        ttk.Label(frm, text="Seriale Disco Cliente (Hardware ID):").pack(anchor="w")
        self.ent_disk = ttk.Entry(frm, width=60)
        self.ent_disk.pack(pady=5)
        ttk.Button(frm, text="Incolla dagli appunti", command=self.paste_disk).pack(anchor="e", pady=5)

        # Nome Cliente (solo per organizzazione cartelle)
        ttk.Label(frm, text="Nome Riferimento Cliente (es. AziendaX):").pack(anchor="w", pady=(10, 0))
        self.ent_name = ttk.Entry(frm, width=60)
        self.ent_name.pack(pady=5)

        # Scadenza
        ttk.Label(frm, text="Data Scadenza (YYYY-MM-DD):").pack(anchor="w", pady=(15, 0))
        self.ent_date = ttk.Entry(frm, width=20)
        self.ent_date.pack(anchor="w", pady=5)
        
        # Default 60 giorni
        scadenza_default = (date.today() + timedelta(days=60)).strftime("%Y-%m-%d")
        self.ent_date.insert(0, scadenza_default)

        # Bottone Genera
        self.btn_gen = ttk.Button(root, text="GENERA FILE LICENZA", command=self.generate)
        self.btn_gen.pack(fill="x", padx=20, pady=20, ipady=10)

    def paste_disk(self):
        try:
            self.ent_disk.delete(0, tk.END)
            self.ent_disk.insert(0, self.root.clipboard_get().strip())
        except: pass

    def generate(self):
        disk_serial = self.ent_disk.get().strip()
        client_name = self.ent_name.get().strip()
        expiry = self.ent_date.get().strip()

        if not disk_serial:
            messagebox.showerror("Errore", "Il Seriale del Disco è obbligatorio!")
            return
        
        if not client_name:
            client_name = disk_serial # Fallback se non c'è nome

        # Pulisci il nome cliente per usarlo come cartella
        folder_name = "".join([c for c in client_name if c.isalnum() or c in (' ', '_', '-')]).strip()
        
        # Cartella di output organizzata
        base_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_LICENZE_CLIENTI")
        target_dir = os.path.join(base_output, folder_name)

        # Comando PyArmor (genera in cartella temporanea 'dist' locale allo script)
        cmd = [sys.executable, "-m", "pyarmor.cli", "gen", "key", 
               "-e", expiry, 
               "-b", disk_serial] 

        try:
            # Esegui comando
            res = subprocess.run(cmd, capture_output=True, text=True)
            
            if res.returncode == 0:
                # PyArmor di default mette l'output in "dist/pyarmor.rkey" relativo alla CWD
                src_default = os.path.join("dist", "pyarmor.rkey")
                
                if os.path.exists(src_default):
                    # Crea cartella destinazione
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    
                    # 1. Sposta il file di licenza
                    dst_lic = os.path.join(target_dir, "pyarmor.rkey")
                    if os.path.exists(dst_lic): os.remove(dst_lic)
                    shutil.move(src_default, dst_lic)
                    
                    # 2. Crea file TXT con i dettagli ID
                    txt_path = os.path.join(target_dir, "dettagli_licenza.txt")
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(f"Cliente: {client_name}\n")
                        f.write(f"Hardware ID (Disk Serial): {disk_serial}\n")
                        f.write(f"Scadenza Licenza: {expiry}\n")
                        f.write(f"Generato il: {date.today().strftime('%Y-%m-%d')}\n")

                    # Istruzioni per l'utente
                    msg = (f"Licenza GENERATA con successo!\n\n"
                           f"Cliente: {client_name}\n"
                           f"Scadenza: {expiry}\n"
                           f"Vincolo Hardware: {disk_serial}\n\n"
                           f"FILE SALVATI IN:\n{target_dir}\n"
                           f"(Troverai 'pyarmor.rkey' e 'dettagli_licenza.txt')\n\n"
                           f"ISTRUZIONI: Invia 'pyarmor.rkey' al cliente.")
                    
                    messagebox.showinfo("Successo", msg)
                    
                    # Apre la cartella automaticamente
                    os.startfile(target_dir)
                else:
                    messagebox.showerror("Errore", f"File generato non trovato in {src_default}")
            else:
                messagebox.showerror("Errore PyArmor", f"Output errore:\n{res.stderr}")

        except Exception as e:
            messagebox.showerror("Eccezione", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    LicenseAdminApp(root)
    root.mainloop()