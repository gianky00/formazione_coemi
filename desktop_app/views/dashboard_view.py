import tkinter as tk
from tkinter import ttk
import webbrowser
from desktop_app.views.database_view import DatabaseView
from desktop_app.views.import_view import ImportView
from desktop_app.views.validation_view import ValidationView
from desktop_app.views.scadenzario_view import ScadenzarioView
from desktop_app.views.config_view import ConfigView
from desktop_app.views.dipendenti_view import DipendentiView
from desktop_app.views.chat_view import ChatView
from desktop_app.views.audit_view import AuditView

class DashboardView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F3F4F6")

        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self, bg="#1E3A8A", height=50)
        header.pack(fill="x", side="top")

        # App Title in Header
        lbl_app = tk.Label(header, text="Intelleo Desktop", bg="#1E3A8A", fg="white", font=("Segoe UI", 12, "bold"))
        lbl_app.pack(side="left", padx=20, pady=10)

        # User Info
        user_info = self.controller.api_client.user_info
        username = user_info.get("account_name", "Utente") if user_info else "Utente"

        lbl_user = tk.Label(header, text=f"Utente: {username}", bg="#1E3A8A", fg="#93C5FD", font=("Segoe UI", 10))
        lbl_user.pack(side="right", padx=20)

        # Logout Button
        btn_logout = tk.Button(header, text="Esci", bg="#B91C1C", fg="white", relief="flat",
                               font=("Segoe UI", 9), command=self.controller.logout)
        btn_logout.pack(side="right", padx=10, pady=10)

        # Guide Button
        btn_guide = tk.Button(header, text="Guida", bg="#059669", fg="white", relief="flat",
                              font=("Segoe UI", 9), command=self.open_guide)
        btn_guide.pack(side="right", padx=10, pady=10)

        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Initialize Tabs
        self.tab_db = DatabaseView(self.notebook, self.controller)
        self.tab_scadenzario = ScadenzarioView(self.notebook, self.controller)
        self.tab_validation = ValidationView(self.notebook, self.controller)
        self.tab_import = ImportView(self.notebook, self.controller)
        self.tab_dipendenti = DipendentiView(self.notebook, self.controller)
        self.tab_chat = ChatView(self.notebook, self.controller)
        self.tab_config = ConfigView(self.notebook, self.controller)
        self.tab_audit = AuditView(self.notebook, self.controller)

        # Add Tabs
        self.notebook.add(self.tab_db, text="🗄️ Database")
        self.notebook.add(self.tab_scadenzario, text="📅 Scadenzario")
        self.notebook.add(self.tab_validation, text="✅ Convalida")
        self.notebook.add(self.tab_dipendenti, text="👥 Anagrafica")
        self.notebook.add(self.tab_import, text="📥 Importazione")
        self.notebook.add(self.tab_chat, text="💬 Lyra AI")

        # Only show Config/Audit if Admin
        is_admin = user_info.get("is_admin", False) if user_info else False
        if is_admin:
            self.notebook.add(self.tab_audit, text="🛡️ Log Attività")
            self.notebook.add(self.tab_config, text="⚙️ Configurazione")

        # Select first tab
        self.notebook.select(self.tab_db)

    def open_guide(self):
        webbrowser.open("http://localhost:5173") # TODO: Point to real URL or file path in prod
