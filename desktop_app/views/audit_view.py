import threading
import tkinter as tk
from tkinter import messagebox, ttk


class AuditView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F3F4F6")
        self.data = []

        self.setup_ui()

    def setup_ui(self):
        # Toolbar
        toolbar = tk.Frame(self, bg="#F3F4F6", pady=10)
        toolbar.pack(fill="x")

        tk.Button(toolbar, text="Aggiorna", command=self.refresh_data).pack(side="left", padx=10)

        tk.Label(toolbar, text="Filtra:", bg="#F3F4F6").pack(side="left", padx=5)
        self.combo_cat = ttk.Combobox(
            toolbar, values=["TUTTI", "AUTH", "DATA", "CERTIFICATE", "SECURITY"], state="readonly"
        )
        self.combo_cat.set("TUTTI")
        self.combo_cat.pack(side="left", padx=5)
        self.combo_cat.bind("<<ComboboxSelected>>", lambda e: self.filter_data())

        # Results count
        self.lbl_count = tk.Label(toolbar, text="", bg="#F3F4F6", font=("Segoe UI", 9))
        self.lbl_count.pack(side="right", padx=10)

        # Treeview
        columns = ("timestamp", "utente", "azione", "dettagli", "ip", "severita")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="extended")

        self.tree.heading("timestamp", text="Data/Ora")
        self.tree.heading("utente", text="Utente")
        self.tree.heading("azione", text="Azione")
        self.tree.heading("dettagli", text="Dettagli")
        self.tree.heading("ip", text="IP Address")
        self.tree.heading("severita", text="Severita")

        self.tree.column("timestamp", width=130, anchor="center")
        self.tree.column("utente", width=100)
        self.tree.column("azione", width=150)
        self.tree.column("dettagli", width=350)
        self.tree.column("ip", width=100)
        self.tree.column("severita", width=80, anchor="center")

        # Tags
        self.tree.tag_configure("CRITICAL", background="#FECACA")
        self.tree.tag_configure("MEDIUM", background="#FED7AA")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Keyboard shortcuts
        self.tree.bind("<F5>", lambda e: self.refresh_data())
        self.tree.bind("<Control-a>", self.select_all)

    def select_all(self, event=None):
        """Select all items in the tree."""
        self.tree.selection_set(self.tree.get_children())
        return "break"

    def refresh_data(self):
        """Refresh audit logs using background thread (no popup dialog)."""

        def fetch():
            try:
                data = self.controller.api_client.get_audit_logs(limit=500)
                if self.winfo_exists():
                    self.after(0, lambda: self._update_data(data))
            except Exception:
                if self.winfo_exists():
                    self.after(
                        0,
                        lambda: messagebox.showerror("Errore", f"Impossibile caricare i log: {e}"),
                    )

        threading.Thread(target=fetch, daemon=True).start()

    def _update_data(self, data):
        self.data = data
        self.filter_data()

    def filter_data(self):
        cat = self.combo_cat.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        count = 0
        for log in self.data:
            if cat != "TUTTI" and log.get("category") != cat:
                continue

            severity = log.get("severity", "LOW")
            values = (
                log.get("timestamp"),
                log.get("username") or "SYSTEM",
                log.get("action"),
                log.get("details"),
                log.get("ip_address"),
                severity,
            )
            tag = severity if severity in ["CRITICAL", "MEDIUM"] else ""
            self.tree.insert("", "end", values=values, tags=(tag,))
            count += 1

        self.lbl_count.config(text=f"{count} log")
