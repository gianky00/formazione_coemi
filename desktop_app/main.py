import tkinter as tk
from tkinter import ttk, messagebox
import sys
import logging
from desktop_app.api_client import APIClient
from desktop_app.views.login_view import LoginView
# from desktop_app.views.dashboard_view import DashboardView (Will import later to avoid circular)

class ApplicationController:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Intelleo")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)
        
        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use('clam') # 'clam' is usually cleaner than 'default'
        
        # Configure fonts
        default_font = ("Segoe UI", 10)
        self.root.option_add("*Font", default_font)
        
        self.api_client = APIClient()
        self.current_view = None
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start(self):
        self.show_login()
        self.root.mainloop()

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
