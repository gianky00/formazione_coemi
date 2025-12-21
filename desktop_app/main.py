import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
import sqlite3
from pathlib import Path

from desktop_app.api_client import APIClient
from desktop_app.views.login_view import LoginView
from desktop_app.services.license_manager import LicenseManager
from app.core.config import settings
from desktop_app.utils import TaskRunner

# Import Config/Dipendenti Views
from desktop_app.views.config_view import ConfigView
from desktop_app.views.dipendenti_view import DipendentiView
# Dashboard imported deferred

class ApplicationController:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Intelleo")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)
        
        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Configure fonts
        default_font = ("Segoe UI", 10)
        self.root.option_add("*Font", default_font)
        
        self.api_client = APIClient()
        self.current_view = None

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start(self):
        self.root.withdraw() # Hide root during checks

        # 1. License Check
        if not self._check_license():
            sys.exit(1)

        # 2. Database Check
        if not self._check_database():
            sys.exit(1)

        self.root.deiconify() # Show root
        self.show_login()
        self.root.mainloop()

    def _check_license(self):
        # Physical check
        try:
            data = LicenseManager.get_license_data()
            if not data:
                raise ValueError("Licenza non trovata o invalida.")
            return True
        except Exception as e:
            # Try recovery? For now just error as per simplified plan
            messagebox.showerror("Errore Licenza", f"Impossibile avviare l'applicazione:\n{e}")
            return False

    def _check_database(self):
        # Check if DB exists and is valid
        # If API is running, we can check via API health or config?
        # But API connects to DB. If DB path is wrong, API might fail startup or return error.
        # However, backend reads DATABASE_PATH from settings.json.

        # We need to check if the file pointed by settings exists.
        db_path = settings.DATABASE_PATH
        path_obj = Path(db_path) if db_path else None

        if path_obj and path_obj.exists() and path_obj.is_file():
            # Assume valid for now (Backend will validate integrity on connect)
            return True

        # If missing, prompt user
        return self._prompt_db_recovery(path_obj)

    def _prompt_db_recovery(self, current_path):
        # Show dialog
        # Create a temp toplevel since root is hidden? No, just use messagebox/filedialog with root as parent (even if hidden)

        msg = f"Il database non è stato trovato al percorso:\n{current_path}\n\nÈ necessario selezionare un database esistente o crearne uno nuovo."
        response = messagebox.askyesno("Database Mancante", msg + "\n\nSì = Seleziona Esistente\nNo = Crea Nuovo")

        if response: # Yes -> Browse
            path = filedialog.askopenfilename(title="Seleziona Database", filetypes=[("SQLite DB", "*.db"), ("All Files", "*.*")])
            if path:
                self._update_db_setting(path)
                return True
        else: # No -> Create
            dir_path = filedialog.askdirectory(title="Seleziona Cartella per Nuovo Database")
            if dir_path:
                new_path = os.path.join(dir_path, "database_documenti.db")
                self._initialize_new_database(new_path)
                self._update_db_setting(new_path)
                return True

        return False

    def _update_db_setting(self, path):
        # Update settings.json directly since API might be using old path or not fully ready
        settings.save_mutable_settings({"DATABASE_PATH": str(path)})
        # We should restart the backend?
        # Since backend runs in separate thread started by launcher, updating settings might not affect it instantly if it already cached config.
        # But settings.json is re-read on request usually? Or at startup?
        # Backend reads settings at startup.
        # We must tell user to restart or force restart.
        messagebox.showinfo("Riavvio Richiesto", "La configurazione del database è cambiata. L'applicazione verrà riavviata.")
        self._restart_app()

    def _initialize_new_database(self, path_str):
        # Initialize SQLite file
        try:
            conn = sqlite3.connect(path_str)
            conn.execute("PRAGMA journal_mode=DELETE;")
            conn.commit()
            conn.close()

            # Apply Schema via SQLAlchemy (Backend code usage)
            from sqlalchemy import create_engine
            from app.db.models import Base
            from app.db.seeding import seed_database
            from sqlalchemy.orm import sessionmaker

            db_url = f"sqlite:///{path_str}"
            engine = create_engine(db_url)
            Base.metadata.create_all(bind=engine)

            # Seed
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            seed_database(db)
            db.close()

        except Exception as e:
            messagebox.showerror("Errore Creazione", f"Impossibile creare il database:\n{e}")
            sys.exit(1)

    def _restart_app(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def show_login(self):
        if self.current_view:
            self.current_view.destroy()

        self.current_view = LoginView(self.root, self)
        self.current_view.pack(fill="both", expand=True)

    def show_dashboard(self):
        if self.current_view:
            self.current_view.destroy()

        # Deferred import to avoid circular dependency
        from desktop_app.views.dashboard_view import DashboardView
        self.current_view = DashboardView(self.root, self)
        self.current_view.pack(fill="both", expand=True)

    def on_login_success(self, user_info):
        self.api_client.set_token(user_info)
        self.show_dashboard()

    def logout(self):
        try:
            self.api_client.logout()
        except Exception:
            pass
        self.show_login()

    def on_close(self):
        if messagebox.askokcancel("Esci", "Vuoi davvero uscire?"):
            self.logout()
            self.root.destroy()
            sys.exit(0)

if __name__ == "__main__":
    app = ApplicationController()
    app.start()
