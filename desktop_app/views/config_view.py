import tkinter as tk
from tkinter import ttk, messagebox
from desktop_app.utils import TaskRunner
from app.core.config import settings as local_settings

class ConfigView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F3F4F6")

        # Main Notebook for sub-sections
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_settings = SettingsTab(self.notebook, controller)
        self.tab_users = UsersTab(self.notebook, controller)

        self.notebook.add(self.tab_settings, text="⚙️ Impostazioni")
        self.notebook.add(self.tab_users, text="👥 Gestione Utenti")

class SettingsTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="white", padx=20, pady=20)

        # Scrollable Frame for settings if they get too long
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.setup_ui(self.scrollable_frame)
        self.load_settings()

    def setup_ui(self, parent):
        # -- Paths --
        self._add_section_header(parent, "Percorsi Sistema")
        self.entry_db = self._add_field(parent, "Database Path:", readonly=True)

        # -- AI Integration --
        self._add_section_header(parent, "Integrazione AI")
        self.entry_gemini_analysis = self._add_field(parent, "Gemini API Key (Analisi):", show="*")
        self.entry_gemini_chat = self._add_field(parent, "Gemini API Key (Chat):", show="*")

        # Voice Toggle
        self.var_voice = tk.BooleanVar(value=True)
        f_voice = tk.Frame(parent, bg="white")
        f_voice.pack(fill="x", pady=5)
        tk.Checkbutton(f_voice, text="Abilita Assistente Vocale", variable=self.var_voice, bg="white").pack(side="left")

        # -- Email --
        self._add_section_header(parent, "Configurazione Email (SMTP)")
        # Presets
        f_pre = tk.Frame(parent, bg="white")
        f_pre.pack(fill="x", pady=5)
        tk.Label(f_pre, text="Preset:", bg="white").pack(side="left")
        ttk.Button(f_pre, text="Gmail", command=lambda: self.apply_preset("gmail")).pack(side="left", padx=5)
        ttk.Button(f_pre, text="Outlook", command=lambda: self.apply_preset("outlook")).pack(side="left", padx=5)

        self.entry_server = self._add_field(parent, "Server SMTP:")
        self.entry_port = self._add_field(parent, "Porta:")
        self.entry_email = self._add_field(parent, "Email Mittente:")
        self.entry_password = self._add_field(parent, "Password (App Pwd):", show="*")

        tk.Button(parent, text="Invia Email di Prova", command=self.test_email).pack(anchor="w", pady=5)

        # -- Scadenze & Avvisi --
        self._add_section_header(parent, "Scadenze e Avvisi")
        self.entry_alert_days = self._add_field(parent, "Giorni Preavviso (Generale):")
        self.entry_alert_visite = self._add_field(parent, "Giorni Preavviso (Visite):")

        # -- Manutenzione --
        self._add_section_header(parent, "Manutenzione")
        tk.Button(parent, text="🛠️ Esegui Backup e Manutenzione", command=self.trigger_maintenance, bg="#F59E0B", fg="white").pack(anchor="w", pady=5)

        # -- Save --
        tk.Button(parent, text="SALVA TUTTO", bg="#1D4ED8", fg="white", font=("Segoe UI", 10, "bold"),
                  command=self.save_settings, padx=20, pady=10).pack(pady=20, fill="x")

    def _add_section_header(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 11, "bold"), bg="white", fg="#1E3A8A").pack(anchor="w", pady=(15, 5))
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=(0, 5))

    def _add_field(self, parent, label, show=None, readonly=False):
        f = tk.Frame(parent, bg="white")
        f.pack(fill="x", pady=2)
        tk.Label(f, text=label, width=25, anchor="w", bg="white").pack(side="left")
        e = tk.Entry(f, show=show)
        e.pack(side="left", fill="x", expand=True)
        if readonly:
            e.config(state="readonly")
        return e

    def apply_preset(self, provider):
        if provider == "gmail":
            self.entry_server.delete(0, "end"); self.entry_server.insert(0, "smtp.gmail.com")
            self.entry_port.delete(0, "end"); self.entry_port.insert(0, "587")
        elif provider == "outlook":
            self.entry_server.delete(0, "end"); self.entry_server.insert(0, "smtp.office365.com")
            self.entry_port.delete(0, "end"); self.entry_port.insert(0, "587")

    def load_settings(self):
        try:
            data = self.controller.api_client.get_mutable_config()

            # DB Path
            self.entry_db.config(state="normal")
            self.entry_db.delete(0, "end")
            self.entry_db.insert(0, data.get("DATABASE_PATH", ""))
            self.entry_db.config(state="readonly")

            # AI
            self.entry_gemini_analysis.delete(0, "end"); self.entry_gemini_analysis.insert(0, data.get("GEMINI_API_KEY_ANALYSIS", ""))
            self.entry_gemini_chat.delete(0, "end"); self.entry_gemini_chat.insert(0, data.get("GEMINI_API_KEY_CHAT", ""))
            self.var_voice.set(data.get("VOICE_ASSISTANT_ENABLED", True))

            # Email
            self.entry_server.delete(0, "end"); self.entry_server.insert(0, data.get("SMTP_SERVER", ""))
            self.entry_port.delete(0, "end"); self.entry_port.insert(0, str(data.get("SMTP_PORT", "")))
            self.entry_email.delete(0, "end"); self.entry_email.insert(0, data.get("SMTP_USERNAME", ""))
            # Password hidden/masked logic if needed

            # Thresholds
            self.entry_alert_days.delete(0, "end"); self.entry_alert_days.insert(0, str(data.get("ALERT_THRESHOLD_DAYS", 60)))
            self.entry_alert_visite.delete(0, "end"); self.entry_alert_visite.insert(0, str(data.get("ALERT_THRESHOLD_DAYS_VISITE", 30)))

        except Exception:
            pass

    def save_settings(self):
        data = {
            "GEMINI_API_KEY_ANALYSIS": self.entry_gemini_analysis.get(),
            "GEMINI_API_KEY_CHAT": self.entry_gemini_chat.get(),
            "VOICE_ASSISTANT_ENABLED": self.var_voice.get(),
            "SMTP_SERVER": self.entry_server.get(),
            "SMTP_PORT": int(self.entry_port.get()) if self.entry_port.get().isdigit() else 587,
            "SMTP_USERNAME": self.entry_email.get(),
            "SMTP_PASSWORD": self.entry_password.get(),
            "ALERT_THRESHOLD_DAYS": int(self.entry_alert_days.get()) if self.entry_alert_days.get().isdigit() else 60,
            "ALERT_THRESHOLD_DAYS_VISITE": int(self.entry_alert_visite.get()) if self.entry_alert_visite.get().isdigit() else 30
        }

        try:
            # 1. Update Backend (Persist)
            self.controller.api_client.update_mutable_config(data)

            # 2. Update Local Frontend State (Immediate Effect)
            local_settings.save_mutable_settings(data)

            messagebox.showinfo("Successo", "Impostazioni salvate correttamente.")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore salvataggio: {e}")

    def test_email(self):
        try:
            url = f"{self.controller.api_client.base_url}/notifications/test-email"
            import requests
            requests.post(url, json={"email": self.entry_email.get()}, headers=self.controller.api_client._get_headers())
            messagebox.showinfo("Inviata", "Email di prova inviata.")
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def trigger_maintenance(self):
        try:
            self.controller.api_client.trigger_maintenance()
            messagebox.showinfo("Avviata", "Manutenzione e backup in background avviati.")
        except Exception as e:
            messagebox.showerror("Errore", str(e))

class UsersTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="white", padx=20, pady=20)
        self.setup_ui()
        self.refresh_users()

    def setup_ui(self):
        # Toolbar
        toolbar = tk.Frame(self, bg="white")
        toolbar.pack(fill="x", pady=10)
        tk.Button(toolbar, text="➕ Nuovo Utente", bg="#10B981", fg="white", command=self.add_user).pack(side="left")
        tk.Button(toolbar, text="🔄 Aggiorna", command=self.refresh_users).pack(side="left", padx=10)

        # List
        columns = ("id", "username", "role", "last_login")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("username", text="Username")
        self.tree.heading("role", text="Ruolo")
        self.tree.heading("last_login", text="Ultimo Accesso")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_edit_user)

    def refresh_users(self):
        try:
            users = self.controller.api_client.get_users()
            for item in self.tree.get_children():
                self.tree.delete(item)

            for u in users:
                role = "Admin" if u.get("is_admin") else "User"
                self.tree.insert("", "end", values=(u["id"], u["username"], role, u.get("last_login", "")))
        except Exception as e:
            pass

    def add_user(self):
        UserDialog(self, self.controller)

    def on_edit_user(self, event):
        item = self.tree.selection()
        if not item: return
        vals = self.tree.item(item, "values")
        user_id = vals[0]
        # Fetch full user?
        # Just open dialog with ID
        UserDialog(self, self.controller, user_id=user_id, username=vals[1], is_admin=(vals[2]=="Admin"))

class UserDialog(tk.Toplevel):
    def __init__(self, parent, controller, user_id=None, username="", is_admin=False):
        super().__init__(parent)
        self.controller = controller
        self.user_id = user_id
        self.parent_view = parent

        self.title("Utente" if user_id else "Nuovo Utente")
        self.geometry("300x300")

        tk.Label(self, text="Username:").pack(pady=5)
        self.entry_user = tk.Entry(self)
        self.entry_user.insert(0, username)
        self.entry_user.pack()

        tk.Label(self, text="Password:").pack(pady=5)
        self.entry_pass = tk.Entry(self, show="*")
        self.entry_pass.pack()
        if user_id:
            tk.Label(self, text="(Lasciare vuoto per non cambiare)", font=("Arial", 8)).pack()

        self.var_admin = tk.BooleanVar(value=is_admin)
        tk.Checkbutton(self, text="Amministratore", variable=self.var_admin).pack(pady=10)

        tk.Button(self, text="SALVA", command=self.save).pack(pady=10)
        if user_id:
            tk.Button(self, text="ELIMINA", bg="red", fg="white", command=self.delete).pack()

    def save(self):
        data = {
            "username": self.entry_user.get(),
            "is_admin": self.var_admin.get()
        }
        pwd = self.entry_pass.get()

        try:
            if self.user_id:
                if pwd: data["password"] = pwd
                self.controller.api_client.update_user(self.user_id, data)
            else:
                if not pwd:
                    messagebox.showerror("Errore", "Password richiesta")
                    return
                self.controller.api_client.create_user(data["username"], pwd, is_admin=data["is_admin"])

            self.parent_view.refresh_users()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def delete(self):
        if messagebox.askyesno("Conferma", "Eliminare utente?"):
            try:
                self.controller.api_client.delete_user(self.user_id)
                self.parent_view.refresh_users()
                self.destroy()
            except Exception as e:
                messagebox.showerror("Errore", str(e))
