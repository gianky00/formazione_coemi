import os

import requests
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from desktop_app.utils import ProgressTaskRunner


class ImportView(QWidget):
    log_signal = Signal(str)

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller

        self.setup_ui()
        self.log_signal.connect(self._safe_log)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        lbl = QLabel("Importazione e Analisi Documenti")
        lbl.setProperty("class", "SectionHeader")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

        # Controls Frame
        controls_layout = QHBoxLayout()

        self.btn_file = QPushButton("📄 Seleziona File PDF")
        self.btn_file.setCursor(Qt.PointingHandCursor)
        self.btn_file.clicked.connect(self.select_file)
        controls_layout.addWidget(self.btn_file)

        self.btn_folder = QPushButton("📂 Seleziona Cartella")
        self.btn_folder.setCursor(Qt.PointingHandCursor)
        self.btn_folder.clicked.connect(self.select_folder)
        controls_layout.addWidget(self.btn_folder)

        self.btn_csv = QPushButton("👥 Importa Dipendenti (CSV)")
        self.btn_csv.setProperty("class", "PrimaryButton")
        self.btn_csv.setCursor(Qt.PointingHandCursor)
        self.btn_csv.clicked.connect(self.import_csv)
        controls_layout.addWidget(self.btn_csv)

        layout.addLayout(controls_layout)
        layout.addSpacing(20)

        # Log Area
        lbl_log = QLabel("Log Operazioni:")
        lbl_log.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl_log)

        self.log_text = QTextEdit()
        self.log_text.setObjectName("LogArea")
        self.log_text.setReadOnly(True)
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
        color = "#D4D4D4"
        msg_upper = message.upper()
        if any(x in msg_upper for x in ("OK:", "SUCCESSO", "COMPLETAT")):
            color = "#4ADE80"
        elif any(x in msg_upper for x in ("ERRORE", "ERRORI")):
            color = "#F87171"
        elif "SKIP:" in msg_upper:
            color = "#A78BFA"
        elif "AVVISO:" in msg_upper:
            color = "#FBBF24"
        elif "---" in msg_upper:
            color = "#22D3EE"

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
        files = [path] if os.path.isfile(path) else []
        if not files:
            for root, _, filenames in os.walk(path):
                files.extend(os.path.join(root, f) for f in filenames if f.lower().endswith(".pdf"))

        if not files:
            QMessageBox.warning(self, "Attenzione", "Nessun file PDF trovato.")
            return

        runner = ProgressTaskRunner(self, "Analisi AI", f"Analisi di {len(files)} documenti...")
        try:
            result = runner.run(self._process_single_file, files)
            success = sum(1 for r in result.get("results", []) if r.get("success"))
            errors = len(result.get("errors", []))
            self.log(f"--- ANALISI TERMINATA: {success} Successi, {errors} Errori ---")
            QMessageBox.information(
                self, "Completato", f"Analisi terminata con {success} successi."
            )
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))

    def _process_single_file(self, file_path):
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

        entities = res.json().get("entities", {})
        payload = {
            k: entities.get(k)
            for k in ("nome", "corso", "categoria", "data_rilascio", "data_scadenza")
        }

        create_url = f"{self.controller.api_client.base_url}/certificati/"
        requests.post(
            create_url, json=payload, headers=self.controller.api_client._get_headers()
        ).raise_for_status()

        self.log(f"OK: {os.path.basename(file_path)} -> {entities.get('nome')}")
        return {"file": file_path, "nome": entities.get("nome")}

    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importa CSV", "", "CSV Files (*.csv)")
        if path:
            try:
                self.controller.api_client.import_dipendenti_csv(path)
                QMessageBox.information(self, "Successo", "Importazione CSV completata.")
            except Exception as e:
                QMessageBox.critical(self, "Errore", str(e))
