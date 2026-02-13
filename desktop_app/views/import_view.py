import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

import requests

from app.core.config import settings
from app.services.document_locator import construct_certificate_path
from app.services.sync_service import get_unique_filename
from desktop_app.utils import ProgressTaskRunner, TaskRunner


class ImportView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F3F4F6")
        self.log_text = None

        self.setup_ui()

    def setup_ui(self):
        # Header
        lbl = tk.Label(
            self,
            text="Importazione e Analisi Documenti",
            bg="#F3F4F6",
            font=("Segoe UI", 14, "bold"),
        )
        lbl.pack(pady=20)

        # Controls Frame
        controls = tk.Frame(self, bg="#F3F4F6")
        controls.pack(pady=10)

        btn_file = tk.Button(
            controls,
            text="📄 Seleziona File PDF",
            bg="white",
            command=self.select_file,
            padx=10,
            pady=5,
        )
        btn_file.pack(side="left", padx=10)

        btn_folder = tk.Button(
            controls,
            text="📂 Seleziona Cartella",
            bg="white",
            command=self.select_folder,
            padx=10,
            pady=5,
        )
        btn_folder.pack(side="left", padx=10)

        btn_csv = tk.Button(
            controls,
            text="👥 Importa Dipendenti (CSV)",
            bg="#3B82F6",
            fg="white",
            command=self.import_csv,
            padx=10,
            pady=5,
        )
        btn_csv.pack(side="left", padx=10)

        # Log Area
        lbl_log = tk.Label(self, text="Log Operazioni:", bg="#F3F4F6", anchor="w")
        lbl_log.pack(fill="x", padx=20, pady=(20, 0))

        self.log_text = tk.Text(
            self, height=15, state="disabled", font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4"
        )
        self.log_text.pack(fill="both", expand=True, padx=20, pady=5)

        # Configure log tags for colors
        self.log_text.tag_configure(
            "success", foreground="#4ade80", font=("Consolas", 9, "bold")
        )  # Green
        self.log_text.tag_configure(
            "error", foreground="#f87171", font=("Consolas", 9, "bold")
        )  # Red
        self.log_text.tag_configure(
            "warning", foreground="#fbbf24", font=("Consolas", 9, "bold")
        )  # Yellow/Orange
        self.log_text.tag_configure("info", foreground="#60a5fa")  # Blue
        self.log_text.tag_configure("skip", foreground="#a78bfa")  # Purple
        self.log_text.tag_configure(
            "header", foreground="#22d3ee", font=("Consolas", 10, "bold")
        )  # Cyan

        # Clear Log Button
        tk.Button(self, text="Pulisci Log", command=self.clear_log).pack(pady=10)

    def log(self, message):
        # Schedule update on main thread
        self.after(0, lambda: self._safe_log(message))

    def _safe_log(self, message):
        self.log_text.config(state="normal")

        # Determine tag based on message content
        tag = None
        msg_upper = message.upper()
        if msg_upper.startswith("OK:") or "SUCCESSO" in msg_upper or "COMPLETAT" in msg_upper:
            tag = "success"
        elif msg_upper.startswith("ERRORE") or "ERRORE" in msg_upper or "ERRORI" in msg_upper:
            tag = "error"
        elif msg_upper.startswith("SKIP:") or "SALTATI" in msg_upper:
            tag = "skip"
        elif msg_upper.startswith("AVVISO:") or "AVVISO" in msg_upper:
            tag = "warning"
        elif msg_upper.startswith("---") or "TERMINATA" in msg_upper:
            tag = "header"
        elif msg_upper.startswith("AVVIO") or "TROVATI" in msg_upper:
            tag = "info"

        if tag:
            self.log_text.insert("end", message + "\n", tag)
        else:
            self.log_text.insert("end", message + "\n")

        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.run_analysis(path)

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.run_analysis(path)

    def run_analysis(self, path):
        """
        Runs the analysis using ProgressTaskRunner with ETA.
        """
        self.log(f"Avvio analisi su: {path}")

        # Collect files first
        if os.path.isfile(path):
            files = [path]
        else:
            files = []
            for root, _, filenames in os.walk(path):
                for f in filenames:
                    if f.lower().endswith(".pdf"):
                        files.append(os.path.join(root, f))

        if not files:
            messagebox.showwarning("Attenzione", "Nessun file PDF trovato.")
            return

        self.log(f"Trovati {len(files)} file PDF da analizzare")

        runner = ProgressTaskRunner(
            self, "Analisi AI in corso", f"Analisi di {len(files)} documenti..."
        )

        try:
            result = runner.run(self._process_single_file, files)

            # Count results
            success = sum(1 for r in result.get("results", []) if r.get("success"))
            errors = len(result.get("errors", []))
            skipped = sum(
                1
                for r in result.get("results", [])
                if not r.get("success") and "409" in str(r.get("error", ""))
            )

            self.log("--- ANALISI TERMINATA ---")
            self.log(f"Successi: {success}")
            self.log(f"Saltati (già presenti): {skipped}")
            self.log(f"Errori: {errors - skipped}")

            messagebox.showinfo(
                "Completato",
                f"Analisi terminata.\n\nSuccessi: {success}\nSaltati: {skipped}\nErrori: {errors - skipped}",
            )

        except Exception as e:
            self.log(f"Errore critico: {e}")
            messagebox.showerror("Errore", str(e))

    def _process_single_file(self, file_path):
        """Process a single PDF file."""
        try:
            # 1. Upload & Analyze
            url = f"{self.controller.api_client.base_url}/upload-pdf/"
            with open(file_path, "rb") as f:
                files_dict = {"file": (os.path.basename(file_path), f, "application/pdf")}
                res = requests.post(
                    url,
                    files=files_dict,
                    headers=self.controller.api_client._get_headers(),
                    timeout=120,
                )
                res.raise_for_status()

            data = res.json()
            entities = data.get("entities", {})

            # 2. Save Certificate to DB
            payload = {
                "nome": entities.get("nome"),
                "corso": entities.get("corso"),
                "categoria": entities.get("categoria"),
                "data_rilascio": entities.get("data_rilascio"),
                "data_scadenza": entities.get("data_scadenza"),
            }

            create_url = f"{self.controller.api_client.base_url}/certificati/"
            create_res = requests.post(
                create_url, json=payload, headers=self.controller.api_client._get_headers()
            )
            create_res.raise_for_status()

            # Copy file to database structure
            self._organize_pdf_file(file_path, entities)

            self.log(f"OK: {os.path.basename(file_path)} -> {entities.get('nome')}")
            return {"file": file_path, "nome": entities.get("nome")}

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:
                self.log(f"SKIP: {os.path.basename(file_path)} -> Già presente.")
                raise Exception("409: Già presente")
            else:
                self.log(f"ERRORE HTTP: {os.path.basename(file_path)} -> {e}")
                raise
        except Exception as e:
            self.log(f"ERRORE: {os.path.basename(file_path)} -> {e}")
            raise

    def _organize_pdf_file(self, source_path, entities):
        """
        Copies the PDF file to the organized database structure.
        Structure: DOCUMENTS_FOLDER/DOCUMENTI DIPENDENTI/{NOME} ({MATRICOLA})/{CATEGORIA}/{STATUS}/{file}.pdf
        """
        database_path = settings.DOCUMENTS_FOLDER
        if not database_path:
            return  # No database path configured

        try:
            from datetime import datetime

            nome = entities.get("nome") or "SCONOSCIUTO"
            categoria = entities.get("categoria") or "ALTRO"
            data_scadenza = entities.get("data_scadenza")

            # Try to find the employee in DB to get matricola
            matricola = None
            try:
                dipendenti = self.controller.api_client.get_dipendenti_list()
                for dip in dipendenti:
                    dip_nome = f"{dip.get('cognome', '')} {dip.get('nome', '')}".strip().upper()
                    if nome.upper() == dip_nome:
                        matricola = dip.get("matricola")
                        break
            except Exception:
                pass  # If we can't fetch, use None

            # Determine correct status based on expiry date
            status = "ATTIVO"
            if data_scadenza:
                try:
                    # Try different date formats
                    for fmt in ["%d/%m/%Y", "%Y-%m-%d"]:
                        try:
                            scad_date = datetime.strptime(data_scadenza, fmt).date()
                            today = datetime.now().date()
                            days_remaining = (scad_date - today).days
                            if days_remaining < 0:
                                status = "SCADUTO"
                            elif days_remaining <= 60:  # Threshold for "in scadenza"
                                status = "IN SCADENZA"
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass

            # Build cert_data for path construction
            cert_data = {
                "nome": nome,
                "matricola": matricola,
                "categoria": categoria,
                "data_scadenza": data_scadenza,
            }

            # Construct destination path with correct status
            dest_path = construct_certificate_path(database_path, cert_data, status=status)
            dest_dir = os.path.dirname(dest_path)

            # Create directory structure
            os.makedirs(dest_dir, exist_ok=True)

            # Get unique filename to avoid overwrites
            filename = os.path.basename(dest_path)
            unique_filename = get_unique_filename(dest_dir, filename)
            final_path = os.path.join(dest_dir, unique_filename)

            # Copy file (don't move, keep original)
            shutil.copy2(source_path, final_path)

        except Exception as e:
            self.log(f"Avviso: impossibile organizzare file - {e}")

    def _run_sync_with_notification(self):
        """Run sync in background and notify when complete."""
        import threading

        def sync_task():
            try:
                sync_url = f"{self.controller.api_client.base_url}/system/maintenance/background"
                sync_res = requests.post(
                    sync_url, headers=self.controller.api_client._get_headers(), timeout=300
                )

                # Schedule UI update on main thread
                if sync_res.ok:
                    result = sync_res.json() if sync_res.text else {}
                    message = result.get("message", "File sincronizzati correttamente")
                    self.after(0, lambda: self._on_sync_complete(True, message))
                else:
                    self.after(0, lambda: self._on_sync_complete(False, sync_res.text))
            except Exception:
                self.after(0, lambda: self._on_sync_complete(False, str(e)))

        thread = threading.Thread(target=sync_task, daemon=True)
        thread.start()

    def _on_sync_complete(self, success, message):
        """Handle sync completion with toast notification."""
        if success:
            self.log(f"OK: Sincronizzazione completata - {message}")
            if hasattr(self.controller, "show_toast"):
                self.controller.show_toast(
                    "Sincronizzazione Completata",
                    message or "I file sono stati sincronizzati correttamente.",
                    "success",
                    5000,
                )
        else:
            self.log(f"ERRORE: Sincronizzazione fallita - {message}")
            if hasattr(self.controller, "show_toast"):
                self.controller.show_toast(
                    "Sincronizzazione Fallita",
                    message or "Si è verificato un errore durante la sincronizzazione.",
                    "error",
                    8000,
                )

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            runner = TaskRunner(self, "Importazione CSV", "Caricamento dipendenti...")
            try:
                res = runner.run(self.controller.api_client.import_dipendenti_csv, path)
                self.log(f"Importazione CSV: {res.get('message', 'Ok')}")

                # Trigger maintenance to sync orphaned certificates and PDF files
                self.log("Sincronizzazione file PDF in corso...")
                self._run_sync_with_notification()

                messagebox.showinfo(
                    "Successo",
                    "Importazione CSV completata.\nI file PDF verranno sincronizzati automaticamente.",
                )
            except Exception as e:
                self.log(f"Errore CSV: {e}")
                messagebox.showerror("Errore", str(e))
