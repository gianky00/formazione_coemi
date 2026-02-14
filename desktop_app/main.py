import contextlib
import os
import sqlite3
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

from app import __version__ as app_version
from app.core.config import settings
from desktop_app.api_client import APIClient
from desktop_app.services.license_manager import LicenseManager
from desktop_app.services.notification_center import NotificationCenter
from desktop_app.services.proactive_service import ProactiveService
from desktop_app.services.toast_service import ToastManager
from desktop_app.services.update_checker import UpdateChecker
from desktop_app.services.voice_service import VoiceService

# Import Config/Dipendenti Views
from desktop_app.views.login_view import LoginView

# Dashboard imported deferred


class ApplicationController:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Intelleo")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)

        # Maximize window on startup (show taskbar)
        self.root.state("zoomed")

        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure fonts
        default_font = ("Segoe UI", 10)
        self.root.option_add("*Font", default_font)

        self.api_client = APIClient()
        self.voice_service = VoiceService()
        self.current_view: Any = None
        self.toast_manager = ToastManager(self.root)
        self.notification_center = NotificationCenter(self)
        self.proactive_service: Any = None  # Will be initialized after login

        # Inactivity Timer
        self.inactivity_timer: str | None = None
        self.INACTIVITY_TIMEOUT_MS = 3600 * 1000  # 1 hour
        self.root.bind_all("<Any-KeyPress>", self._reset_inactivity_timer)
        self.root.bind_all("<Any-ButtonPress>", self._reset_inactivity_timer)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start(self) -> None:
        self.root.withdraw()  # Hide root during checks

        # 1. License Check
        if not self._check_license():
            sys.exit(1)

        # 2. Database Check
        if not self._check_database():
            sys.exit(1)

        # 3. Update Check (Async)
        self._check_updates()

        self.root.deiconify()  # Show root
        self.show_login()
        self._reset_inactivity_timer()
        self.root.mainloop()

    def _check_updates(self) -> None:
        checker = UpdateChecker(app_version)

        def on_update(has_update: bool, version: str, url: str) -> None:
            if has_update:
                self.root.after(0, lambda: self._prompt_update(version, url))

        checker.check_for_updates(on_update)

    def _prompt_update(self, version: str, url: str) -> None:
        if messagebox.askyesno(
            "Aggiornamento Disponibile", f"Nuova versione {version} disponibile. Scaricare ora?"
        ):
            import webbrowser

            webbrowser.open(url)

    def _check_license(self) -> bool:
        # Physical check
        try:
            data = LicenseManager.get_license_data()
            if not data:
                # If reading failed, try to regenerate/update or fail
                pass
            return True
        except Exception as e:
            messagebox.showerror("Errore Licenza", f"Impossibile avviare l'applicazione:\n{e}")
            return False

    def _check_database(self) -> bool:
        db_path = settings.DATABASE_PATH
        path_obj = Path(db_path) if db_path else None

        if path_obj and path_obj.exists() and path_obj.is_file():
            return True
        return self._prompt_db_recovery(path_obj)

    def _prompt_db_recovery(self, current_path: Path | None) -> bool:
        msg = f"Il database non è stato trovato al percorso:\n{current_path}\n\nÈ necessario selezionare un database esistente o crearne uno nuovo."
        response = messagebox.askyesno(
            "Database Mancante", msg + "\n\nSì = Seleziona Esistente\nNo = Crea Nuovo"
        )

        if response:  # Yes -> Browse
            path = filedialog.askopenfilename(
                title="Seleziona Database", filetypes=[("SQLite DB", "*.db"), ("All Files", "*.*")]
            )
            if path:
                self._update_db_setting(path)
                return True
        else:  # No -> Create
            dir_path = filedialog.askdirectory(title="Seleziona Cartella per Nuovo Database")
            if dir_path:
                new_path = os.path.join(dir_path, "database_documenti.db")
                self._initialize_new_database(new_path)
                self._update_db_setting(new_path)
                return True

        return False

    def _update_db_setting(self, path: str) -> None:
        settings.save_mutable_settings({"DATABASE_PATH": str(path)})
        messagebox.showinfo(
            "Riavvio Richiesto",
            "La configurazione del database è cambiata. L'applicazione verrà riavviata.",
        )
        self._restart_app()

    def _initialize_new_database(self, path_str: str) -> None:
        try:
            conn = sqlite3.connect(path_str)
            conn.execute("PRAGMA journal_mode=DELETE;")
            conn.commit()
            conn.close()

            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            from app.db.models import Base
            from app.db.seeding import seed_database

            db_url = f"sqlite:///{path_str}"
            engine = create_engine(db_url)
            Base.metadata.create_all(bind=engine)

            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            seed_database(db)
            db.close()

        except Exception as e:
            messagebox.showerror("Errore Creazione", f"Impossibile creare il database:\n{e}")
            sys.exit(1)

    def _restart_app(self) -> None:
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def show_login(self) -> None:
        if self.current_view:
            self.current_view.destroy()

        self.current_view = LoginView(self.root, self)
        self.current_view.pack(fill="both", expand=True)

    def show_dashboard(self) -> None:
        if self.current_view:
            self.current_view.destroy()

        from desktop_app.views.dashboard_view import DashboardView

        self.current_view = DashboardView(self.root, self)
        self.current_view.pack(fill="both", expand=True)

        # Voice Welcome
        name = (
            self.api_client.user_info.get("account_name", "") if self.api_client.user_info else ""
        )
        self.voice_service.speak(f"Benvenuto {name}")

        # Initialize and run proactive analysis
        self.proactive_service = ProactiveService(
            self, self.toast_manager, self.notification_center
        )
        self.proactive_service.run_startup_analysis()

    def on_login_success(self, user_info: dict[str, Any]) -> None:
        # 503 Fix: Check Read Only Status
        is_read_only = user_info.get("read_only", False)
        lock_owner = user_info.get("lock_owner")

        if is_read_only:
            owner_str = str(lock_owner) if lock_owner else "un altro utente"
            messagebox.showwarning(
                "Modalità Sola Lettura",
                f"Il database è attualmente bloccato da {owner_str}.\n"
                "L'applicazione funzionerà in modalità limitata (niente modifiche).",
            )

        self.api_client.set_token(user_info)
        self.show_dashboard()
        self._reset_inactivity_timer()

    def logout(self) -> None:
        with contextlib.suppress(Exception):
            self.api_client.logout()
        self.show_login()

    def on_close(self) -> None:
        if messagebox.askokcancel("Esci", "Vuoi davvero uscire?"):
            self.logout()
            self.voice_service.cleanup()
            self.root.destroy()
            sys.exit(0)

    # --- Toast Notifications ---
    def show_toast(
        self,
        title: str,
        message: str,
        toast_type: str = "info",
        duration: int = 5000,
        on_click: Any = None,
    ) -> None:
        """Show a toast notification."""
        if self.toast_manager:
            self.toast_manager.show(title, message, toast_type, duration, on_click)

    # --- Inactivity ---
    def _reset_inactivity_timer(self, event: Any = None) -> None:
        if self.inactivity_timer:
            self.root.after_cancel(self.inactivity_timer)
        self.inactivity_timer = self.root.after(self.INACTIVITY_TIMEOUT_MS, self._on_inactivity)

    def _on_inactivity(self) -> None:
        if isinstance(self.current_view, LoginView):
            return  # Don't timeout on login screen

        messagebox.showwarning("Sessione Scaduta", "Disconnessione per inattività.")
        self.logout()


if __name__ == "__main__":
    app = ApplicationController()
    app.start()
