import tkinter as tk
from tkinter import ttk, messagebox
import threading

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
        btn_login = tk.Button(container, text="ACCEDI", bg="#1D4ED8", fg="white", font=("Segoe UI", 11, "bold"),
                              relief="flat", padx=20, pady=10, command=self.do_login, cursor="hand2")
        btn_login.pack(pady=20, fill="x")
        
        # Status Label
        self.lbl_status = tk.Label(container, text="", bg="white", fg="red")
        self.lbl_status.pack()

    def do_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        
        if not username or not password:
            self.lbl_status.config(text="Inserisci username e password")
            return

        self.lbl_status.config(text="Connessione in corso...", fg="blue")
        self.update_idletasks()

        # Perform login in a separate thread to avoid freezing UI (simple manual thread here)
        threading.Thread(target=self._login_thread, args=(username, password), daemon=True).start()

    def _login_thread(self, username, password):
        try:
            # Login call
            token_data = self.controller.api_client.login(username, password)

            # Additional info fetch
            self.controller.api_client.set_token(token_data)

            # Back to UI thread
            self.after(0, lambda: self.controller.on_login_success(token_data))

        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg:
                error_msg = "Credenziali non valide."
            elif "ConnectionError" in str(type(e).__name__):
                error_msg = "Impossibile connettersi al server."

            self.after(0, lambda: self.lbl_status.config(text=error_msg, fg="red"))
