import os
import shutil
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QFileDialog, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QFont, QTextCursor

from app.core.config import settings
from app.services.document_locator import construct_certificate_path
from app.services.sync_service import get_unique_filename
from desktop_app.utils import ProgressTaskRunner, TaskRunner


class ImportView(QWidget):
    log_signal = Signal(str)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setStyleSheet("background-color: #F3F4F6;")
        
        self.setup_ui()
        self.log_signal.connect(self._safe_log)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        lbl = QLabel("Importazione e Analisi Documenti")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #1F2937; border: none;")
        layout.addWidget(lbl)

        # Controls Frame
        controls_layout = QHBoxLayout()
        
        self.btn_file = QPushButton("📄 Seleziona File PDF")
        self.btn_file.setCursor(Qt.PointingHandCursor)
        self.btn_file.setStyleSheet("padding: 10px; background-color: white; border: 1px solid #D1D5DB; border-radius: 4px;")
        self.btn_file.clicked.connect(self.select_file)
        controls_layout.addWidget(self.btn_file)

        self.btn_folder = QPushButton("📂 Seleziona Cartella")
        self.btn_folder.setCursor(Qt.PointingHandCursor)
        self.btn_folder.setStyleSheet("padding: 10px; background-color: white; border: 1px solid #D1D5DB; border-radius: 4px;")
        self.btn_folder.clicked.connect(self.select_folder)
        controls_layout.addWidget(self.btn_folder)

        self.btn_csv = QPushButton("👥 Importa Dipendenti (CSV)")
        self.btn_csv.setCursor(Qt.PointingHandCursor)
        self.btn_csv.setStyleSheet("padding: 10px; background-color: #3B82F6; color: white; font-weight: bold; border-radius: 4px; border: none;")
        self.btn_csv.clicked.connect(self.import_csv)
        controls_layout.addWidget(self.btn_csv)

        layout.addLayout(controls_layout)
        layout.addSpacing(20)

        # Log Area
        lbl_log = QLabel("Log Operazioni:")
        lbl_log.setStyleSheet("font-weight: bold; color: #374151; border: none;")
        layout.addWidget(lbl_log)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        self.log_text.setStyleSheet("background-color: #1E1E1E; color: #D4D4D4; border-radius: 4px;")
        layout.addWidget(self.log_text)

        # Clear Log Button
        self.btn_clear = QPushButton("Pulisci Log")
        self.btn_clear.clicked.connect(self.clear_log)
        self.btn_clear.setFixedWidth(120)
        layout.addWidget(self.btn_clear, 0, Qt.AlignCenter)

    def log(self, message):
        self.log_signal.emit(message)

    @Slot(str)
    def _safe_log(self, message):
        # Determine color based on content
        color = "#D4D4D4" # Default
        msg_upper = message.upper()
        if msg_upper.startswith("OK:") or "SUCCESSO" in msg_upper or "COMPLETAT" in msg_upper:
            color = "#4ADE80"
        elif msg_upper.startswith("ERRORE") or "ERRORE" in msg_upper or "ERRORI" in msg_upper:
            color = "#F87171"
        elif msg_upper.startswith("SKIP:") or "SALTATI" in msg_upper:
            color = "#A78BFA"
        elif msg_upper.startswith("AVVISO:") or "AVVISO" in msg_upper:
            color = "#FBBF24"
        elif msg_upper.startswith("---") or "TERMINATA" in msg_upper:
            color = "#22D3EE"
        elif msg_upper.startswith("AVVIO") or "TROVATI" in msg_upper:
            color = "#60A5FA"

        html_msg = f'<span style="color: {color};">{message}</span><br>'
        self.log_text.append(html_msg)
        self.log_text.moveCursor(QTextCursor.End)

    def clear_log(self):
        self.log_text.clear()

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleziona File PDF", "", "PDF Files (*.pdf)")
        if path:
            self.run_analysis(path)

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Seleziona Cartella")
        if path:
            self.run_analysis(path)

    def run_analysis(self, path):
        self.log(f"Avvio analisi su: {path}")
        if os.path.isfile(path):
            files = [path]
        else:
            files = []
            for root, _, filenames in os.walk(path):
                for f in filenames:
                    if f.lower().endswith(".pdf"):
                        files.append(os.path.join(root, f))

        if not files:
            QMessageBox.warning(self, "Attenzione", "Nessun file PDF trovato.")
            return

        self.log(f"Trovati {len(files)} file PDF da analizzare")

        runner = ProgressTaskRunner(self, "Analisi AI in corso", f"Analisi di {len(files)} documenti...")
        try:
            result = runner.run(self._process_single_file, files)
            success = sum(1 for r in result.get("results", []) if r.get("success"))
            errors = len(result.get("errors", []))
            skipped = sum(1 for r in result.get("results", []) if not r.get("success") and "409" in str(r.get("error", "")))

            self.log("--- ANALISI TERMINATA ---")
            self.log(f"Successi: {success}")
            self.log(f"Saltati (già presenti): {skipped}")
            self.log(f"Errori: {errors - skipped}")

            QMessageBox.information(
                self, "Completato",
                f"Analisi terminata.\n\nSuccessi: {success}\nSaltati: {skipped}\nErrori: {errors - skipped}"
            )
        except Exception as e:
            self.log(f"Errore critico: {e}")
            QMessageBox.critical(self, "Errore", str(e))

    def _process_single_file(self, file_path):
        try:
            url = f"{self.controller.api_client.base_url}/upload-pdf/"
            with open(file_path, "rb") as f:
                files_dict = {"file": (os.path.basename(file_path), f, "application/pdf")}
                res = requests.post(
                    url, files=files_dict,
                    headers=self.controller.api_client._get_headers(),
                    timeout=120
                )
                res.raise_for_status()

            data = res.json()
            entities = data.get("entities", {})

            payload = {
                "nome": entities.get("nome"),
                "corso": entities.get("corso"),
                "categoria": entities.get("categoria"),
                "data_rilascio": entities.get("data_rilascio"),
                "data_scadenza": entities.get("data_scadenza"),
            }

            create_url = f"{self.controller.api_client.base_url}/certificati/"
            create_res = requests.post(create_url, json=payload, headers=self.controller.api_client._get_headers())
            create_res.raise_for_status()

            self._organize_pdf_file(file_path, entities)
            self.log(f"OK: {os.path.basename(file_path)} -> {entities.get('nome')}")
            return {"file": file_path, "nome": entities.get("nome")}

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:
                self.log(f"SKIP: {os.path.basename(file_path)} -> Già presente.")
                raise Exception("409: Già presente") from e
            raise
        except Exception as e:
            self.log(f"ERRORE: {os.path.basename(file_path)} -> {e}")
            raise

    def _organize_pdf_file(self, source_path, entities):
        database_path = settings.DOCUMENTS_FOLDER
        if not database_path: return

        try:
            from datetime import datetime
            nome = entities.get("nome") or "SCONOSCIUTO"
            categoria = entities.get("categoria") or "ALTRO"
            data_scadenza = entities.get("data_scadenza")

            matricola = None
            try:
                dipendenti = self.controller.api_client.get_dipendenti_list()
                for dip in dipendenti:
                    dip_nome = f"{dip.get('cognome', '')} {dip.get('nome', '')}".strip().upper()
                    if nome.upper() == dip_nome:
                        matricola = dip.get("matricola")
                        break
            except Exception: pass

            status = "ATTIVO"
            if data_scadenza:
                try:
                    for fmt in ["%d/%m/%Y", "%Y-%m-%d"]:
                        try:
                            scad_date = datetime.strptime(data_scadenza, fmt).date()
                            days_remaining = (scad_date - datetime.now().date()).days
                            if days_remaining < 0: status = "SCADUTO"
                            elif days_remaining <= 60: status = "IN SCADENZA"
                            break
                        except ValueError: continue
                except Exception: pass

            cert_data = {"nome": nome, "matricola": matricola, "categoria": categoria, "data_scadenza": data_scadenza}
            dest_path = construct_certificate_path(database_path, cert_data, status=status)
            dest_dir = os.path.dirname(dest_path)
            os.makedirs(dest_dir, exist_ok=True)
            unique_filename = get_unique_filename(dest_dir, os.path.basename(dest_path))
            final_path = os.path.join(dest_dir, unique_filename)
            shutil.copy2(source_path, final_path)
        except Exception as e:
            self.log(f"Avviso: impossibile organizzare file - {e}")

    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importa Dipendenti (CSV)", "", "CSV Files (*.csv)")
        if path:
            runner = TaskRunner(self, "Importazione CSV", "Caricamento dipendenti...")
            try:
                res = runner.run(self.controller.api_client.import_dipendenti_csv, path)
                self.log(f"Importazione CSV: {res.get('message', 'Ok')}")
                self.log("Sincronizzazione file PDF in corso...")
                self._run_sync_with_notification()
                QMessageBox.information(self, "Successo", "Importazione CSV completata.\nI file PDF verranno sincronizzati automaticamente.")
            except Exception as e:
                self.log(f"Errore CSV: {e}")
                QMessageBox.critical(self, "Errore", str(e))

    def _run_sync_with_notification(self):
        import threading
        def sync_task():
            try:
                sync_url = f"{self.controller.api_client.base_url}/system/maintenance/background"
                sync_res = requests.post(sync_url, headers=self.controller.api_client._get_headers(), timeout=300)
                msg = sync_res.json().get("message", "File sincronizzati") if sync_res.ok else sync_res.text
                QTimer.singleShot(0, lambda: self._on_sync_complete(sync_res.ok, msg))
            except Exception as e:
                QTimer.singleShot(0, lambda: self._on_sync_complete(False, str(e)))
        threading.Thread(target=sync_task, daemon=True).start()

    def _on_sync_complete(self, success, message):
        if success:
            self.log(f"OK: Sincronizzazione completata - {message}")
            if hasattr(self.controller, "show_toast"):
                self.controller.show_toast("Sincronizzazione Completata", message, "success")
        else:
            self.log(f"ERRORE: Sincronizzazione fallita - {message}")
            if hasattr(self.controller, "show_toast"):
                self.controller.show_toast("Sincronizzazione Fallita", message, "error")
