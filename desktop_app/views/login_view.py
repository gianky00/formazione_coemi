import tkinter as tk
from tkinter import ttk
import threading
from desktop_app.services.license_manager import LicenseManager
from app import __version__ as app_version

class LoginView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F0F8FF") # Light blue background
        
        self.setup_ui()

    def setup_ui(self):
        # Center container
        container = tk.Frame(self, bg="white", padx=40, pady=40, relief="raised", borderwidth=1)
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo/Title
        lbl_title = tk.Label(container, text="Intelleo", font=("Segoe UI", 24, "bold"), bg="white", fg="#1E3A8A")
        lbl_title.pack(pady=(0, 10))
        
        lbl_subtitle = tk.Label(container, text="Predict. Validate. Automate.", font=("Segoe UI", 10, "italic"), bg="white", fg="#6B7280")
        lbl_subtitle.pack(pady=(0, 20))
        
        # Username
        lbl_user = tk.Label(container, text="Username", bg="white", font=("Segoe UI", 10, "bold"), anchor="w")
        lbl_user.pack(fill="x", pady=(10, 5))
        self.entry_user = ttk.Entry(container, width=30)
        self.entry_user.pack(pady=5)
        self.entry_user.focus_set()
        
        # Password
        lbl_pass = tk.Label(container, text="Password", bg="white", font=("Segoe UI", 10, "bold"), anchor="w")
        lbl_pass.pack(fill="x", pady=(10, 5))
        self.entry_pass = ttk.Entry(container, show="*", width=30)
        self.entry_pass.pack(pady=5)
        self.entry_pass.bind("<Return>", lambda e: self.do_login())
        
        # Button
        self.btn_login = tk.Button(container, text="ACCEDI", bg="#1D4ED8", fg="white", font=("Segoe UI", 11, "bold"),
                              relief="flat", padx=20, pady=10, command=self.do_login, cursor="hand2")
        self.btn_login.pack(pady=20, fill="x")
        
        # Status Label
        self.lbl_status = tk.Label(container, text="", bg="white", fg="red")
        self.lbl_status.pack()

        # --- License Info Footer ---
        footer_frame = tk.Frame(self, bg="#F0F8FF")
        footer_frame.pack(side="bottom", fill="x", pady=10, padx=10)

        try:
            lic_data = LicenseManager.get_license_data()
            if lic_data:
                # Use correct keys from admin_license_gui.py
                client_name = lic_data.get("Cliente", "N/D")
                expiry = lic_data.get("Scadenza Licenza", "N/D")
                hwid = lic_data.get("Hardware ID", "N/D")

                info_text = f"Cliente: {client_name} | Scadenza: {expiry} | HWID: {hwid} | Versione: {app_version}"
                lbl_lic = tk.Label(footer_frame, text=info_text, bg="#F0F8FF", fg="#6B7280", font=("Segoe UI", 8))
                lbl_lic.pack(side="right")
            else:
                raise ValueError("No data")
        except Exception:
            tk.Label(footer_frame, text=f"Versione: {app_version}", bg="#F0F8FF", fg="#6B7280").pack(side="right")

    def do_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        
        if not username or not password:
            self.lbl_status.config(text="Inserisci username e password")
            return

        # Disable UI to prevent double-submit
        self.entry_user.config(state="disabled")
        self.entry_pass.config(state="disabled")
        self.btn_login.config(state="disabled", cursor="watch")
        
        self.lbl_status.config(text="Connessione in corso...", fg="blue")
        self.update_idletasks()

        # Perform login in a separate thread
        threading.Thread(target=self._login_thread, args=(username, password), daemon=True).start()

    def _login_thread(self, username, password):
        try:
            # Login call
            token_data = self.controller.api_client.login(username, password)

            # Additional info fetch
            self.controller.api_client.set_token(token_data)

            # Back to UI thread -> Success
            self.after(0, lambda: self.controller.on_login_success(token_data))

        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg:
                error_msg = "Credenziali non valide."
            elif "ConnectionError" in str(type(e).__name__):
                error_msg = "Impossibile connettersi al server."

            # Back to UI thread -> Failure (Re-enable UI)
            def on_fail():
                self.lbl_status.config(text=error_msg, fg="red")
                self.entry_user.config(state="normal")
                self.entry_pass.config(state="normal")
                self.btn_login.config(state="normal", cursor="hand2")
                self.entry_pass.delete(0, 'end')
                
            self.after(0, on_fail)
