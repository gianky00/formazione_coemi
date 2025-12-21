import tkinter as tk
from tkinter import ttk, messagebox
from desktop_app.utils import TaskRunner

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
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        # -- Paths Section --
        lbl_paths = tk.Label(self, text="Percorsi Sistema", font=("Segoe UI", 12, "bold"), bg="white")
        lbl_paths.pack(anchor="w", pady=(0, 10))

        f_db = tk.Frame(self, bg="white")
        f_db.pack(fill="x", pady=5)
        tk.Label(f_db, text="Database Path:", width=15, anchor="w", bg="white").pack(side="left")
        self.entry_db = tk.Entry(f_db)
        self.entry_db.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_db.config(state="readonly") # Managed via logic, not direct edit usually

        # -- Email Section --
        tk.Label(self, text="Configurazione Email (SMTP)", font=("Segoe UI", 12, "bold"), bg="white").pack(anchor="w", pady=(20, 10))

        # Presets
        f_pre = tk.Frame(self, bg="white")
        f_pre.pack(fill="x", pady=5)
        tk.Label(f_pre, text="Preset:", bg="white").pack(side="left")
        ttk.Button(f_pre, text="Gmail", command=lambda: self.apply_preset("gmail")).pack(side="left", padx=5)
        ttk.Button(f_pre, text="Outlook", command=lambda: self.apply_preset("outlook")).pack(side="left", padx=5)

        # Fields
        self.entry_server = self._add_field("Server SMTP:")
        self.entry_port = self._add_field("Porta:")
        self.entry_email = self._add_field("Email Mittente:")
        self.entry_password = self._add_field("Password (App Pwd):", show="*")

        # Test Button
        tk.Button(self, text="Invia Email di Prova", command=self.test_email).pack(anchor="w", pady=10)

        # -- Save Button --
        tk.Button(self, text="SALVA IMPOSTAZIONI", bg="#1D4ED8", fg="white", font=("Segoe UI", 10, "bold"),
                  command=self.save_settings, padx=20, pady=10).pack(anchor="e", pady=20)

    def _add_field(self, label, show=None):
        f = tk.Frame(self, bg="white")
        f.pack(fill="x", pady=2)
        tk.Label(f, text=label, width=20, anchor="w", bg="white").pack(side="left")
        e = tk.Entry(f, show=show)
        e.pack(side="left", fill="x", expand=True)
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
            # We need an endpoint for mutable config.
            # Assuming GET /app_config/config exists and returns JSON.
            data = self.controller.api_client.get_mutable_config()

            self.entry_db.config(state="normal")
            self.entry_db.delete(0, "end")
            self.entry_db.insert(0, data.get("DATABASE_PATH", ""))
            self.entry_db.config(state="readonly")

            self.entry_server.delete(0, "end"); self.entry_server.insert(0, data.get("SMTP_SERVER", ""))
            self.entry_port.delete(0, "end"); self.entry_port.insert(0, str(data.get("SMTP_PORT", "")))
            self.entry_email.delete(0, "end"); self.entry_email.insert(0, data.get("SMTP_USERNAME", ""))
            # Password usually not returned for security or masked.

        except Exception as e:
            pass # Silent fail on load or default

    def save_settings(self):
        data = {
            "SMTP_SERVER": self.entry_server.get(),
            "SMTP_PORT": int(self.entry_port.get()) if self.entry_port.get().isdigit() else 587,
            "SMTP_USERNAME": self.entry_email.get(),
            "SMTP_PASSWORD": self.entry_password.get()
        }

        try:
            self.controller.api_client.update_mutable_config(data)
            messagebox.showinfo("Successo", "Impostazioni salvate correttamente.")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore salvataggio: {e}")

    def test_email(self):
        # Trigger test email endpoint
        # POST /notifications/test-email
        try:
            # Manual request
            url = f"{self.controller.api_client.base_url}/notifications/test-email"
            import requests
            requests.post(url, json={"email": self.entry_email.get()}, headers=self.controller.api_client._get_headers())
            messagebox.showinfo("Inviata", "Email di prova inviata.")
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
