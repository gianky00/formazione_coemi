import os
import threading
import tkinter as tk
from tkinter import Menu, messagebox, ttk

from app.core.config import settings
from app.services.document_locator import find_document
from desktop_app.utils import format_date_to_ui, open_file


class DipendentiView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.data = []

        self.setup_ui()

    def setup_ui(self):
        # Toolbar
        toolbar = tk.Frame(self, bg="#F3F4F6", pady=10)
        toolbar.pack(fill="x")

        tk.Button(toolbar, text="Aggiorna", command=self.refresh_data).pack(side="left", padx=10)
        tk.Button(
            toolbar, text="Nuovo Dipendente", bg="#10B981", fg="white", command=self.add_dipendente
        ).pack(side="left", padx=10)

        # Bulk action buttons
        tk.Button(
            toolbar,
            text="Assegna Mansione",
            bg="#2563EB",
            fg="white",
            command=self._bulk_assign_mansione,
        ).pack(side="left", padx=5)
        tk.Button(
            toolbar,
            text="Assegna Reparto",
            bg="#7C3AED",
            fg="white",
            command=self._bulk_assign_reparto,
        ).pack(side="left", padx=5)

        # Search
        tk.Label(toolbar, text="Cerca:", bg="#F3F4F6").pack(side="left", padx=10)
        self.entry_search = tk.Entry(toolbar, width=25)
        self.entry_search.pack(side="left")
        self.entry_search.bind("<KeyRelease>", lambda e: self.filter_data())

        # Selection count
        self.lbl_selection = tk.Label(toolbar, text="", bg="#F3F4F6", font=("Segoe UI", 9))
        self.lbl_selection.pack(side="right", padx=10)

        # Treeview with extended selection for bulk operations
        columns = ("id", "matricola", "nome", "data_nascita", "mansione", "reparto")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="extended")

        self.tree.heading("id", text="ID")
        self.tree.heading("matricola", text="Matricola")
        self.tree.heading("nome", text="Cognome e Nome")
        self.tree.heading("data_nascita", text="Data Nascita")
        self.tree.heading("mansione", text="Mansione")
        self.tree.heading("reparto", text="Reparto")

        self.tree.column("id", width=50)
        self.tree.column("matricola", width=80)
        self.tree.column("nome", width=200)
        self.tree.column("data_nascita", width=100)
        self.tree.column("mansione", width=150)
        self.tree.column("reparto", width=120)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_change)

        # Context Menu
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(
            label="Visualizza Storico Certificati", command=self.show_storico
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Modifica Dati", command=lambda: self.on_double_click(None)
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Assegna Mansione (Selezione)", command=self._bulk_assign_mansione
        )
        self.context_menu.add_command(
            label="Assegna Reparto (Selezione)", command=self._bulk_assign_reparto
        )

        self.tree.bind("<Button-3>", self.show_context_menu)

        # Keyboard shortcuts
        self.tree.bind("<Control-a>", self._select_all)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            if item not in self.tree.selection():
                self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _on_selection_change(self, event):
        """Update selection count label."""
        count = len(self.tree.selection())
        if count > 1:
            self.lbl_selection.config(text=f"{count} selezionati")
        else:
            self.lbl_selection.config(text="")

    def _select_all(self, event=None):
        """Select all items."""
        self.tree.selection_set(self.tree.get_children())
        return "break"

    def _bulk_assign_mansione(self):
        """Bulk assign mansione to selected employees."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attenzione", "Seleziona almeno un dipendente.")
            return

        BulkAssignDialog(self, self.controller, selected, self.data, "mansione")

    def _bulk_assign_reparto(self):
        """Bulk assign reparto to selected employees."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attenzione", "Seleziona almeno un dipendente.")
            return

        BulkAssignDialog(self, self.controller, selected, self.data, "reparto")

    def refresh_data(self):
        # Async fetch without blocking popup
        def fetch():
            try:
                new_data = self.controller.api_client.get_dipendenti_list()
                if self.winfo_exists():
                    self.after(0, lambda: self._update_data(new_data))
            except Exception:
                if self.winfo_exists():
                    self.after(
                        0, lambda: messagebox.showerror("Errore", f"Errore caricamento: {e}")
                    )

        threading.Thread(target=fetch, daemon=True).start()

    def _update_data(self, new_data):
        self.data = new_data
        self.filter_data()

    def filter_data(self):
        query = self.entry_search.get().lower()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for d in self.data:
            cognome = (d.get("cognome") or "").upper()
            nome = (d.get("nome") or "").upper()
            display_name = f"{cognome} {nome}".strip()
            matricola = (d.get("matricola") or "").lower()
            reparto = (d.get("categoria_reparto") or "").upper()

            dob = format_date_to_ui(d.get("data_nascita"))

            if query in display_name.lower() or query in matricola or query in reparto.lower():
                values = (
                    d.get("id"),
                    d.get("matricola") or "",
                    display_name,
                    dob,
                    d.get("mansione") or "",
                    reparto,
                )
                self.tree.insert("", "end", values=values)

    def show_storico(self):
        selected = self.tree.selection()
        if not selected:
            return

        dip_id = self.tree.item(selected[0], "values")[0]
        dip_obj = next((x for x in self.data if str(x["id"]) == str(dip_id)), None)

        if dip_obj:
            StoricoCertificatiDialog(self, self.controller, dip_obj)

    def add_dipendente(self):
        DipendenteDialog(self, self.controller)

    def on_double_click(self, event):
        item = self.tree.selection()
        if not item:
            return
        vals = self.tree.item(item, "values")
        dip_id = vals[0]
        dip_obj = next((x for x in self.data if str(x["id"]) == str(dip_id)), None)
        if dip_obj:
            DipendenteDialog(self, self.controller, dip_obj)


class StoricoCertificatiDialog(tk.Toplevel):
    def __init__(self, parent, controller, dipendente):
        super().__init__(parent)
        self.controller = controller
        self.dipendente = dipendente
        self.title(f"Storico Certificati: {dipendente['cognome']} {dipendente['nome']}")
        self.geometry("900x500")
        self.transient(parent)
        self.grab_set()

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        frame = tk.Frame(self, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        lbl_info = tk.Label(
            frame,
            text=f"Certificati legati a: {self.dipendente['cognome']} {self.dipendente['nome']} (Matricola: {self.dipendente.get('matricola', 'N/D')})",
            font=("Segoe UI", 11, "bold"),
            pady=10,
        )
        lbl_info.pack(fill="x")

        columns = ("corso", "categoria", "rilascio", "scadenza", "stato")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree.heading("corso", text="Documento / Corso")
        self.tree.heading("categoria", text="Categoria")
        self.tree.heading("rilascio", text="Emissione")
        self.tree.heading("scadenza", text="Scadenza")
        self.tree.heading("stato", text="Stato")

        self.tree.column("corso", width=250)
        self.tree.column("categoria", width=150)
        self.tree.column("rilascio", width=100)
        self.tree.column("scadenza", width=100)
        self.tree.column("stato", width=100)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Double-1>", self.open_pdf)

    def load_data(self):
        try:
            # Fetch detailed dipendente info which includes certificates
            details = self.controller.api_client.get_dipendente_detail(self.dipendente["id"])
            certs = details.get("certificati", [])

            for c in certs:
                scad = c.get("data_scadenza") or "NESSUNA"
                stato = c.get("stato_certificato") or "N/D"
                values = (
                    c.get("corso"),
                    c.get("categoria"),
                    c.get("data_rilascio"),
                    scad,
                    stato.upper(),
                )
                self.tree.insert("", "end", values=values, tags=(c.get("stato_certificato"),))

            self.tree.tag_configure("scaduto", foreground="red")
            self.tree.tag_configure("in_scadenza", foreground="orange")
            self.tree.tag_configure("attivo", foreground="green")

        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def open_pdf(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        vals = self.tree.item(selected[0], "values")
        corso = vals[0]
        categoria = vals[1]
        scadenza = vals[3]
        if scadenza == "NESSUNA":
            scadenza = None

        try:
            db_path = settings.DATABASE_PATH
            if not db_path:
                messagebox.showerror("Errore", "Percorso documenti non configurato.")
                return

            search_data = {
                "nome": f"{self.dipendente['cognome']} {self.dipendente['nome']}",
                "matricola": self.dipendente.get("matricola"),
                "categoria": categoria,
                "data_scadenza": scadenza,
            }

            path = find_document(db_path, search_data)
            if path and os.path.exists(path):
                open_file(path)
            else:
                messagebox.showwarning(
                    "File non trovato",
                    f"Non è stato possibile localizzare il PDF.\nDati: {search_data}",
                )
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile aprire il file: {e}")


class DipendenteDialog(tk.Toplevel):
    def __init__(self, parent, controller, dip_data=None):
        super().__init__(parent)
        self.controller = controller
        self.dip_data = dip_data
        self.parent_view = parent

        self.title("Modifica Dipendente" if dip_data else "Nuovo Dipendente")
        self.geometry("450x480")
        self.minsize(400, 450)

        self.setup_ui()

        # Center
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (225)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (240)
        self.geometry(f"+{x}+{y}")

    def setup_ui(self):
        # Main frame with scrollable content
        main_frame = tk.Frame(self, padx=20, pady=15)
        main_frame.pack(fill="both", expand=True)

        # Convert date to DD/MM/YYYY format for display
        data_nascita = ""
        if self.dip_data and self.dip_data.get("data_nascita"):
            raw_date = self.dip_data.get("data_nascita")
            data_nascita = format_date_to_ui(raw_date)

        self.entry_cognome = self._add_field(
            main_frame, "Cognome:", self.dip_data.get("cognome") if self.dip_data else ""
        )
        self.entry_nome = self._add_field(
            main_frame, "Nome:", self.dip_data.get("nome") if self.dip_data else ""
        )
        self.entry_matricola = self._add_field(
            main_frame, "Matricola:", self.dip_data.get("matricola") if self.dip_data else ""
        )
        self.entry_nascita = self._add_field(main_frame, "Data Nascita (GG/MM/AAAA):", data_nascita)
        self.entry_mansione = self._add_field(
            main_frame, "Mansione:", self.dip_data.get("mansione") if self.dip_data else ""
        )
        self.entry_reparto = self._add_field(
            main_frame, "Reparto:", self.dip_data.get("categoria_reparto") if self.dip_data else ""
        )

        # Spacer
        tk.Frame(main_frame, height=20).pack()

        # Buttons frame - always visible at bottom
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)

        if self.dip_data:
            tk.Button(
                btn_frame,
                text="ELIMINA",
                bg="#DC2626",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                command=self.delete,
                width=12,
            ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="SALVA",
            bg="#1D4ED8",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.save,
            width=12,
        ).pack(side="right", padx=5)

        tk.Button(
            btn_frame, text="ANNULLA", font=("Segoe UI", 10), command=self.destroy, width=12
        ).pack(side="right", padx=5)

    def _add_field(self, parent, label, value):
        tk.Label(parent, text=label, anchor="w").pack(fill="x", pady=(10, 0))
        e = tk.Entry(parent)
        if value:
            e.insert(0, str(value))
        e.pack(fill="x", pady=(0, 5))
        return e

    def save(self):
        # Convert date from DD/MM/YYYY to YYYY-MM-DD for backend
        data_nascita_raw = self.entry_nascita.get().strip()
        data_nascita_formatted = None
        if data_nascita_raw:
            try:
                from datetime import datetime

                # Try DD/MM/YYYY format
                if "/" in data_nascita_raw:
                    dt = datetime.strptime(data_nascita_raw, "%d/%m/%Y")
                    data_nascita_formatted = dt.strftime("%Y-%m-%d")
                elif "-" in data_nascita_raw and len(data_nascita_raw) == 10:
                    # Already in YYYY-MM-DD format
                    data_nascita_formatted = data_nascita_raw
                else:
                    data_nascita_formatted = data_nascita_raw
            except ValueError:
                messagebox.showerror("Errore", "Formato data nascita non valido. Usare GG/MM/AAAA")
                return

        data = {
            "cognome": self.entry_cognome.get(),
            "nome": self.entry_nome.get(),
            "matricola": self.entry_matricola.get(),
            "data_nascita": data_nascita_formatted,
            "mansione": self.entry_mansione.get(),
            "categoria_reparto": self.entry_reparto.get(),
        }

        if not data["nome"] or not data["cognome"]:
            messagebox.showerror("Errore", "Nome e Cognome sono obbligatori.")
            return

        try:
            if self.dip_data:
                self.controller.api_client.update_dipendente(self.dip_data["id"], data)
            else:
                self.controller.api_client.create_dipendente(data)

            self.parent_view.refresh_data()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare: {e}")

    def delete(self):
        if messagebox.askyesno("Conferma", "Eliminare definitivamente questo dipendente?"):
            try:
                self.controller.api_client.delete_dipendente(self.dip_data["id"])
                self.parent_view.refresh_data()
                self.destroy()
            except Exception as e:
                messagebox.showerror("Errore", str(e))


class BulkAssignDialog(tk.Toplevel):
    """Dialog for bulk assigning mansione or reparto to multiple employees."""

    def __init__(self, parent, controller, selected_items, data, field_type):
        super().__init__(parent)
        self.controller = controller
        self.parent_view = parent
        self.selected_items = selected_items
        self.data = data
        self.field_type = field_type  # "mansione" or "reparto"

        field_label = "Mansione" if field_type == "mansione" else "Reparto"
        self.title(f"Assegna {field_label} a {len(selected_items)} Dipendenti")
        self.geometry("450x350")
        self.resizable(False, True)
        self.transient(parent)
        self.grab_set()

        self.setup_ui()

        # Center
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (225)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (175)
        self.geometry(f"+{x}+{y}")

    def setup_ui(self):
        frame = tk.Frame(self, padx=20, pady=15)
        frame.pack(fill="both", expand=True)

        field_label = "Mansione" if self.field_type == "mansione" else "Reparto"
        api_field = "mansione" if self.field_type == "mansione" else "categoria_reparto"

        # Info
        tk.Label(
            frame,
            text=f"Dipendenti selezionati: {len(self.selected_items)}",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        # Show list of selected employees
        list_frame = tk.Frame(frame, bg="#E5E7EB", relief="solid", bd=1)
        list_frame.pack(fill="x", pady=5)

        for i, sel in enumerate(self.selected_items[:8]):  # Show max 8
            vals = self.parent_view.tree.item(sel, "values")
            tk.Label(
                list_frame,
                text=f"  \u2022 {vals[2]}",
                bg="#E5E7EB",
                font=("Segoe UI", 9),
                anchor="w",
            ).pack(fill="x")

        if len(self.selected_items) > 8:
            tk.Label(
                list_frame,
                text=f"  ... e altri {len(self.selected_items) - 8}",
                bg="#E5E7EB",
                font=("Segoe UI", 9, "italic"),
                anchor="w",
            ).pack(fill="x")

        # Separator
        tk.Frame(frame, height=10).pack()

        # Get existing values from data
        existing_values = set()
        for dip in self.data:
            val = dip.get(api_field)
            if val:
                existing_values.add(val)

        # Input section
        tk.Label(
            frame, text=f"Nuovo valore per {field_label}:", font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(10, 5))

        # Entry with autocomplete from existing values
        self.entry_value = ttk.Combobox(frame, values=sorted(existing_values), width=35)
        self.entry_value.pack(fill="x", pady=5)
        self.entry_value.focus_set()

        # Hint
        if existing_values:
            tk.Label(
                frame,
                text=f"Valori esistenti: {', '.join(sorted(existing_values)[:5])}{'...' if len(existing_values) > 5 else ''}",
                font=("Segoe UI", 8),
                fg="#6B7280",
            ).pack(anchor="w")

        # Buttons
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill="x", pady=20)

        tk.Button(
            btn_frame, text="Annulla", command=self.destroy, font=("Segoe UI", 10), width=12
        ).pack(side="left")

        tk.Button(
            btn_frame,
            text="Applica a Tutti",
            bg="#10B981",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            width=15,
            command=self._apply,
        ).pack(side="right")

    def _apply(self):
        """Apply the value to all selected employees."""
        new_value = self.entry_value.get().strip()
        if not new_value:
            messagebox.showwarning("Attenzione", "Inserisci un valore.")
            return

        api_field = "mansione" if self.field_type == "mansione" else "categoria_reparto"
        field_label = "Mansione" if self.field_type == "mansione" else "Reparto"

        # Get dipendente IDs
        dip_ids = []
        for sel in self.selected_items:
            vals = self.parent_view.tree.item(sel, "values")
            dip_ids.append(vals[0])

        count = len(dip_ids)
        if not messagebox.askyesno(
            "Conferma", f"Assegnare {field_label} = '{new_value}' a {count} dipendenti?"
        ):
            return

        success = 0
        errors = []

        for dip_id in dip_ids:
            try:
                update_data = {api_field: new_value}
                self.controller.api_client.update_dipendente(dip_id, update_data)
                success += 1
            except Exception as e:
                errors.append(str(e))

        # Show result
        if success == count:
            messagebox.showinfo("Completato", f"{field_label} assegnata a {success} dipendenti.")
        else:
            messagebox.showwarning(
                "Parziale", f"Aggiornati {success}/{count}.\nErrori: {len(errors)}"
            )

        self.parent_view.refresh_data()
        self.destroy()
