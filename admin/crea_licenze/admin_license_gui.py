import hashlib
import json
import os
import shutil
import subprocess
import sys
import tkinter as tk
from datetime import date, timedelta
from tkinter import messagebox, ttk

from cryptography.fernet import Fernet

# SECURITY WARNING: Keep this key secret!
LICENSE_SECRET_KEY = b"8kHs_rmwqaRUk1AQLGX65g4AEkWUDapWVsMFUQpN9Ek="


def _calculate_sha256(filepath):
    """Calculates the SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


class LicenseAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestore Licenze (Admin)")
        self.root.geometry("600x480")
        self.root.resizable(False, False)

        style = ttk.Style()
        style.theme_use("clam")
        # S1192: Use constant
        FONT_FAMILY = "Segoe UI"
        font_style = (FONT_FAMILY, 10)
        style.configure("TLabel", font=font_style)
        style.configure("TButton", font=(FONT_FAMILY, 10, "bold"))

        ttk.Label(root, text="Generatore Licenza Cliente", font=(FONT_FAMILY, 14, "bold")).pack(
            pady=15
        )

        # Container
        frm = ttk.LabelFrame(root, text="Dati Cliente", padding=20)
        frm.pack(fill="both", expand=True, padx=20, pady=5)

        # Disk Serial
        ttk.Label(frm, text="Seriale Disco Cliente (Hardware ID):").pack(anchor="w")
        self.ent_disk = ttk.Entry(frm, width=60)
        self.ent_disk.pack(pady=5)
        ttk.Button(frm, text="Incolla dagli appunti", command=self.paste_disk).pack(
            anchor="e", pady=5
        )

        # Nome Cliente (solo per organizzazione cartelle)
        ttk.Label(frm, text="Nome Riferimento Cliente (es. AziendaX):").pack(
            anchor="w", pady=(10, 0)
        )
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
        # S5754: Specify exception or at least be intentional about swallowing
        try:
            self.ent_disk.delete(0, tk.END)
            self.ent_disk.insert(0, self.root.clipboard_get().strip())
        except tk.TclError:
            pass  # Clipboard empty or unavailable

    def _prepare_paths(self, client_name, disk_serial):
        """Helper to prepare output paths."""
        if not client_name:
            client_name = disk_serial  # Fallback se non c'è nome

        # Pulisci il nome cliente per usarlo come cartella
        folder_name = "".join(
            [c for c in client_name if c.isalnum() or c in (" ", "_", "-")]
        ).strip()

        # Cartella di output organizzata
        base_output = os.path.dirname(os.path.abspath(__file__))
        client_dir = os.path.join(base_output, folder_name)
        target_dir = os.path.join(client_dir, "Licenza")

        return client_name, target_dir

    def _generate_encrypted_config(self, disk_serial, expiry, client_name, target_dir):
        # Format dates to DD/MM/YYYY
        try:
            expiry_obj = date.fromisoformat(expiry)
            expiry_str = expiry_obj.strftime("%d/%m/%Y")
        except ValueError:
            expiry_str = expiry  # Fallback if invalid format

        gen_date_str = date.today().strftime("%d/%m/%Y")
        clean_disk_serial = disk_serial.rstrip(".")

        payload = {
            "Hardware ID": clean_disk_serial,
            "Scadenza Licenza": expiry_str,
            "Generato il": gen_date_str,
            "Cliente": client_name,
        }

        json_payload = json.dumps(payload).encode("utf-8")
        cipher = Fernet(LICENSE_SECRET_KEY)
        encrypted_data = cipher.encrypt(json_payload)

        config_path = os.path.join(target_dir, "config.dat")
        with open(config_path, "wb") as f:
            f.write(encrypted_data)

        return config_path

    def generate(self):
        # S3776: Refactored
        disk_serial = self.ent_disk.get().strip()
        raw_client_name = self.ent_name.get().strip()
        expiry = self.ent_date.get().strip()

        if not disk_serial:
            messagebox.showerror("Errore", "Il Seriale del Disco è obbligatorio!")
            return

        client_name, target_dir = self._prepare_paths(raw_client_name, disk_serial)

        # Comando PyArmor (genera in cartella temporanea 'dist' locale allo script)
        cmd = [sys.executable, "-m", "pyarmor.cli", "gen", "key", "-e", expiry, "-b", disk_serial]

        try:
            # Esegui comando
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                messagebox.showerror("Errore PyArmor", f"Output errore:\n{res.stderr}")
                return

            self._process_generation_success(client_name, target_dir, disk_serial, expiry)

        except Exception as e:
            messagebox.showerror("Eccezione", str(e))

    def _process_generation_success(self, client_name, target_dir, disk_serial, expiry):
        """Handles post-generation tasks (move, encrypt, manifest)."""
        key_filename = "pyarmor.rkey"
        src_default = os.path.join("dist", key_filename)

        if not os.path.exists(src_default):
            messagebox.showerror("Errore", f"File generato non trovato in {src_default}")
            return

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # 1. Sposta il file di licenza
        dst_lic = os.path.join(target_dir, key_filename)
        if os.path.exists(dst_lic):
            os.remove(dst_lic)
        shutil.move(src_default, dst_lic)

        if os.path.exists("dist"):
            shutil.rmtree("dist", ignore_errors=True)

        # 2. GENERAZIONE FILE CRITTOGRAFATO
        config_path = self._generate_encrypted_config(disk_serial, expiry, client_name, target_dir)

        # 3. GENERAZIONE MANIFEST
        self._generate_manifest(target_dir, dst_lic, config_path, key_filename)

        self._show_success_message(client_name, disk_serial, target_dir, key_filename)

    def _generate_manifest(self, target_dir, dst_lic, config_path, key_filename):
        manifest = {
            key_filename: _calculate_sha256(dst_lic),
            "config.dat": _calculate_sha256(config_path),
        }
        manifest_path = os.path.join(target_dir, "manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=4)

    def _show_success_message(self, client_name, disk_serial, target_dir, key_filename):
        msg = (
            f"Licenza GENERATA con successo!\n\n"
            f"Cliente: {client_name}\n"
            f"Hardware ID: {disk_serial}\n\n"
            f"FILE SALVATI IN:\n{target_dir}\n"
            f"(Troverai '{key_filename}', 'config.dat' e 'manifest.json')\n\n"
            f"ISTRUZIONI PER L'AUTO-UPDATE:\n"
            f"1. Apri il repository GitHub privato delle licenze.\n"
            f"2. Crea una nuova cartella nominandola ESATTAMENTE come l'Hardware ID del cliente.\n"
            f"3. Carica i 3 file generati ('{key_filename}', 'config.dat', 'manifest.json') in questa nuova cartella."
        )


import platform


def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

        # ... inside _show_success_message
        messagebox.showinfo("Successo", msg)
        open_file(target_dir)


if __name__ == "__main__":
    root = tk.Tk()
    LicenseAdminApp(root)
    root.mainloop()
