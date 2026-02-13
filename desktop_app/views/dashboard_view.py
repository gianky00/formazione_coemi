import logging
import sys
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

from app import __version__ as app_version
from app.core.path_resolver import get_asset_path
from desktop_app.services.notification_center import NotificationBell, NotificationPanel
from desktop_app.views.config_view import ConfigView
from desktop_app.views.database_view import DatabaseView
from desktop_app.views.dipendenti_view import DipendentiView
from desktop_app.views.import_view import ImportView
from desktop_app.views.lyra_view import LyraView
from desktop_app.views.scadenzario_view import ScadenzarioView
from desktop_app.views.validation_view import ValidationView

logger = logging.getLogger(__name__)


class DashboardView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F3F4F6")

        self.setup_ui()
        self.setup_keyboard_shortcuts()

    def setup_ui(self):
        # Header
        header = tk.Frame(self, bg="#1E3A8A", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Logo/Title - increased font size
        lbl_title = tk.Label(
            header, text="Intelleo", font=("Segoe UI", 18, "bold"), bg="#1E3A8A", fg="white"
        )
        lbl_title.pack(side="left", padx=20, pady=10)

        # User Info - increased font size
        user_info = self.controller.api_client.user_info or {}
        username = user_info.get("account_name") or user_info.get("username") or "Utente"

        lbl_user = tk.Label(
            header, text=f"  {username}", font=("Segoe UI", 11), bg="#1E3A8A", fg="white"
        )
        lbl_user.pack(side="right", padx=10, pady=10)

        # Logout Button - increased font size
        btn_logout = tk.Button(
            header,
            text="Esci",
            bg="#DC2626",
            fg="white",
            relief="flat",
            font=("Segoe UI", 10),
            command=self.controller.logout,
        )
        btn_logout.pack(side="right", padx=5, pady=10)

        # Guide Button - increased font size
        btn_guide = tk.Button(
            header,
            text="Guida",
            bg="#059669",
            fg="white",
            relief="flat",
            font=("Segoe UI", 10),
            command=self.open_guide,
        )
        btn_guide.pack(side="right", padx=10, pady=10)

        # Notification Bell
        if hasattr(self.controller, "notification_center") and self.controller.notification_center:
            self.notification_bell = NotificationBell(
                header, self.controller.notification_center, on_click=self._show_notification_panel
            )
            self.notification_bell.pack(side="right", padx=5)

        # Read-Only Warning Banner (if applicable)
        if user_info.get("read_only"):
            warning_frame = tk.Frame(self, bg="#FEF3C7", height=30)
            warning_frame.pack(fill="x")
            tk.Label(
                warning_frame,
                text="MODALITA SOLA LETTURA - Il database e bloccato da un altro utente",
                bg="#FEF3C7",
                fg="#92400E",
                font=("Segoe UI", 9, "bold"),
            ).pack(pady=5)

        # Footer with version
        footer = tk.Frame(self, bg="#F3F4F6", height=25)
        footer.pack(side="bottom", fill="x")
        footer.pack_propagate(False)

        lbl_version = tk.Label(
            footer, text=f"v{app_version}", font=("Segoe UI", 9), bg="#F3F4F6", fg="#6B7280"
        )
        lbl_version.pack(side="left", padx=15, pady=3)

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        # Create tabs
        self.tab_import = ImportView(self.notebook, self.controller)
        self.tab_validation = ValidationView(self.notebook, self.controller)
        self.tab_database = DatabaseView(self.notebook, self.controller)
        self.tab_scadenzario = ScadenzarioView(self.notebook, self.controller)
        self.tab_dipendenti = DipendentiView(self.notebook, self.controller)
        self.tab_lyra = LyraView(self.notebook, self.controller)
        self.tab_config = ConfigView(self.notebook, self.controller)

        # Add tabs to notebook (order: Importa, Convalida, Database, Scadenzario, Dipendenti, Lyra IA, Configurazione)
        self.notebook.add(self.tab_import, text=" Importa")
        self.notebook.add(self.tab_validation, text=" Convalida")
        self.notebook.add(self.tab_database, text=" Database")
        self.notebook.add(self.tab_scadenzario, text=" Scadenzario")
        self.notebook.add(self.tab_dipendenti, text=" Dipendenti")
        self.notebook.add(self.tab_lyra, text=" Lyra IA")
        self.notebook.add(self.tab_config, text=" Configurazione")

        # Tab Change Event - Refresh data when switching tabs
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # No auto-refresh for import tab (first tab)

    def setup_keyboard_shortcuts(self):
        """Setup global keyboard shortcuts."""
        # Tab navigation with Ctrl+1-7 (Importa, Convalida, Database, Scadenzario, Dipendenti, Lyra IA, Config)
        self.bind_all("<Control-Key-1>", lambda e: self.notebook.select(0))  # Importa
        self.bind_all("<Control-Key-2>", lambda e: self.notebook.select(1))  # Convalida
        self.bind_all("<Control-Key-3>", lambda e: self.notebook.select(2))  # Database
        self.bind_all("<Control-Key-4>", lambda e: self.notebook.select(3))  # Scadenzario
        self.bind_all("<Control-Key-5>", lambda e: self.notebook.select(4))  # Dipendenti
        self.bind_all("<Control-Key-6>", lambda e: self.notebook.select(5))  # Lyra IA
        self.bind_all("<Control-Key-7>", lambda e: self.notebook.select(6))  # Configurazione

        # F1 for guide
        self.bind_all("<F1>", lambda e: self.open_guide())

        # Ctrl+Q to logout
        self.bind_all("<Control-q>", lambda e: self.controller.logout())

    def on_tab_changed(self, event):
        """Refreshes the data of the selected tab."""
        selected_tab = self.notebook.select()
        tab_widget = self.notebook.nametowidget(selected_tab)

        if hasattr(tab_widget, "refresh_data"):
            tab_widget.refresh_data()

    def _show_notification_panel(self):
        """Show the notification panel dropdown."""
        if hasattr(self.controller, "notification_center") and self.controller.notification_center:
            NotificationPanel(
                self.notification_bell, self.controller.notification_center, self.controller
            )

    def open_guide(self):
        """
        Locates and opens the interactive guide in the system browser.
        Uses path_resolver for universal compatibility.
        """
        # Try different locations via path_resolver
        candidates = [
            "guide/index.html",  # Nuitka frozen mapping
            "guide_frontend/dist/index.html",  # Dev/Manual mapping
        ]

        found_uri = None
        for rel_path in candidates:
            try:
                path = get_asset_path(rel_path)
                if path.exists():
                    found_uri = path.absolute().as_uri()
                    break
            except Exception:
                continue

        if found_uri:
            webbrowser.open(found_uri)
        else:
            # Last fallback: Try opening Vite dev server if local
            if not getattr(sys, "frozen", False):
                webbrowser.open("http://localhost:5173")
            else:
                # Silently log instead of showing error (guide is optional)
                logger.debug("Guida interattiva non trovata")
                messagebox.showinfo(
                    "Guida",
                    "La guida interattiva non e disponibile.\nContattare l'assistenza tecnica per maggiori informazioni.",
                )
