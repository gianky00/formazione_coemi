import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import requests
from desktop_app.utils import TaskRunner

class ImportView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F3F4F6")
        self.log_text = None
        
        self.setup_ui()

    def setup_ui(self):
        # Header
        lbl = tk.Label(self, text="Importazione e Analisi Documenti", bg="#F3F4F6", font=("Segoe UI", 14, "bold"))
        lbl.pack(pady=20)
        
        # Controls Frame
        controls = tk.Frame(self, bg="#F3F4F6")
        controls.pack(pady=10)
        
        btn_file = tk.Button(controls, text="📄 Seleziona File PDF", bg="white", command=self.select_file, padx=10, pady=5)
        btn_file.pack(side="left", padx=10)
        
        btn_folder = tk.Button(controls, text="📂 Seleziona Cartella", bg="white", command=self.select_folder, padx=10, pady=5)
        btn_folder.pack(side="left", padx=10)
        
        btn_csv = tk.Button(controls, text="👥 Importa Dipendenti (CSV)", bg="#3B82F6", fg="white", command=self.import_csv, padx=10, pady=5)
        btn_csv.pack(side="left", padx=10)

        # Log Area
        lbl_log = tk.Label(self, text="Log Operazioni:", bg="#F3F4F6", anchor="w")
        lbl_log.pack(fill="x", padx=20, pady=(20, 0))
        
        self.log_text = tk.Text(self, height=15, state="disabled", font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Clear Log Button
        tk.Button(self, text="Pulisci Log", command=self.clear_log).pack(pady=10)

    def log(self, message):
        # Schedule update on main thread
        self.after(0, lambda: self._safe_log(message))

    def _safe_log(self, message):
        self.log_text.config(state="normal")
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
        Runs the analysis using TaskRunner (Blocking Mode).
        """
        self.log(f"Avvio analisi su: {path}")

        runner = TaskRunner(self, "Analisi in corso", "Sto analizzando i documenti con l'AI.\nNon chiudere l'applicazione.")
        try:
            result_stats = runner.run(self._process_path, path)
            self.log(f"--- ANALISI TERMINATA ---")
            self.log(f"Successi: {result_stats['success']}")
            self.log(f"Errori: {result_stats['errors']}")
            messagebox.showinfo("Completato", "Analisi terminata con successo.")

        except Exception as e:
            self.log(f"Errore critico: {e}")
            messagebox.showerror("Errore", str(e))

    def _process_path(self, path):
        stats = {"success": 0, "errors": 0}
        
        if os.path.isfile(path):
            files = [path]
        else:
            files = []
            for root, _, filenames in os.walk(path):
                for f in filenames:
                    if f.lower().endswith(".pdf"):
                        files.append(os.path.join(root, f))
        
        total = len(files)
        
        for i, file_path in enumerate(files):
            try:
                # 1. Upload & Analyze
                url = f"{self.controller.api_client.base_url}/upload-pdf/"
                with open(file_path, 'rb') as f:
                    files_dict = {'file': (os.path.basename(file_path), f, 'application/pdf')}
                    # Increased timeout for AI analysis
                    res = requests.post(url, files=files_dict, headers=self.controller.api_client._get_headers(), timeout=60)
                    res.raise_for_status()

                data = res.json()
                entities = data.get("entities", {})

                # 2. Save Certificate to DB
                # Mapping AI result to CertificatoCreazioneSchema
                # entities: {'nome': '...', 'categoria': '...', 'corso': '...', 'data_rilascio': '...', 'data_scadenza': '...'}

                payload = {
                    "nome": entities.get("nome"),
                    "corso": entities.get("corso"),
                    "categoria": entities.get("categoria"),
                    "data_rilascio": entities.get("data_rilascio"),
                    "data_scadenza": entities.get("data_scadenza")
                }

                create_url = f"{self.controller.api_client.base_url}/certificati/"
                create_res = requests.post(create_url, json=payload, headers=self.controller.api_client._get_headers())
                create_res.raise_for_status()

                self.log(f"OK: {os.path.basename(file_path)} -> {entities.get('nome')}")
                stats['success'] += 1

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 409:
                     self.log(f"SKIP: {os.path.basename(file_path)} -> Già presente.")
                else:
                     self.log(f"ERRORE HTTP: {os.path.basename(file_path)} -> {e}")
                     stats['errors'] += 1
            except Exception as e:
                self.log(f"ERRORE: {os.path.basename(file_path)} -> {e}")
                stats['errors'] += 1
        
        return stats

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            runner = TaskRunner(self, "Importazione CSV", "Caricamento dipendenti...")
            try:
                res = runner.run(self.controller.api_client.import_dipendenti_csv, path)
                self.log(f"Importazione CSV: {res.get('message', 'Ok')}")
                messagebox.showinfo("Successo", "Importazione CSV completata.")
            except Exception as e:
                self.log(f"Errore CSV: {e}")
                messagebox.showerror("Errore", str(e))
