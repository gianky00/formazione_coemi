import threading
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QFrame, QFileDialog, QAbstractItemView
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QKeySequence, QShortcut, QColor, QBrush

from desktop_app.utils import TaskRunner, open_file


class ScadenzarioView(QWidget):
    data_signal = Signal(list)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.data = []
        self.setStyleSheet("background-color: #F3F4F6;")

        self.setup_ui()
        self.setup_shortcuts()
        self.data_signal.connect(self._update_data)
        self.refresh_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        toolbar = QFrame()
        toolbar.setFixedHeight(70)
        toolbar.setStyleSheet("background-color: #F3F4F6; border: none;")
        t_layout = QHBoxLayout(toolbar)
        
        btn_refresh = QPushButton("Aggiorna")
        btn_refresh.clicked.connect(self.refresh_data)
        t_layout.addWidget(btn_refresh)

        btn_export = QPushButton("Esporta PDF")
        btn_export.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold;")
        btn_export.clicked.connect(self.export_pdf)
        t_layout.addWidget(btn_export)

        btn_email = QPushButton("Invia Email Report")
        btn_email.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold;")
        btn_email.clicked.connect(self.send_email)
        t_layout.addWidget(btn_email)

        t_layout.addSpacing(20)
        t_layout.addWidget(QLabel("Cerca:"))
        self.entry_search = QLineEdit()
        self.entry_search.setPlaceholderText("Cerca...")
        self.entry_search.textChanged.connect(self.filter_data)
        t_layout.addWidget(self.entry_search)

        t_layout.addWidget(QLabel("Categoria:"))
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItem("Tutte")
        self.combo_categoria.currentTextChanged.connect(self.filter_data)
        t_layout.addWidget(self.combo_categoria)

        t_layout.addWidget(QLabel("Stato:"))
        self.combo_status = QComboBox()
        self.combo_status.addItems(["Tutti", "Valido", "In Scadenza", "Scaduto"])
        self.combo_status.currentTextChanged.connect(self.filter_data)
        t_layout.addWidget(self.combo_status)

        self.btn_reset = QPushButton("Reset Filtri")
        self.btn_reset.clicked.connect(self._reset_filters)
        t_layout.addWidget(self.btn_reset)

        t_layout.addStretch()
        self.lbl_count = QLabel("")
        t_layout.addWidget(self.lbl_count)

        layout.addWidget(toolbar)

        # Legend frame
        legend = QFrame()
        legend.setFixedHeight(30)
        l_layout = QHBoxLayout(legend)
        l_layout.setContentsMargins(15, 0, 15, 0)
        lbl_leg = QLabel("Rosso=Scaduto | Arancio=In Scadenza | Verde=Valido")
        lbl_leg.setStyleSheet("color: #6B7280; font-size: 11px;")
        l_layout.addStretch()
        l_layout.addWidget(lbl_leg)
        layout.addWidget(legend)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Dipendente", "Documento", "Categoria", "Scadenza", "Giorni Rimanenti"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.table)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("F5"), self, self.refresh_data)
        QShortcut(QKeySequence("Ctrl+F"), self, self.entry_search.setFocus)
        QShortcut(QKeySequence("Ctrl+E"), self, self.export_pdf)
        QShortcut(QKeySequence("Esc"), self, self._reset_filters)

    def refresh_data(self):
        def fetch():
            try:
                new_data = self.controller.api_client.get("certificati", params={"validated": "true"})
                self.data_signal.emit(new_data)
            except: pass
        threading.Thread(target=fetch, daemon=True).start()

    @Slot(list)
    def _update_data(self, new_data):
        self.data = new_data
        
        # Update categories
        categories = set(str(item.get("categoria", "")).upper() for item in self.data if item.get("categoria"))
        self.combo_categoria.blockSignals(True)
        self.combo_categoria.clear()
        self.combo_categoria.addItem("Tutte")
        self.combo_categoria.addItems(sorted(categories))
        self.combo_categoria.blockSignals(False)

        self.filter_data()

    def filter_data(self):
        query = self.entry_search.text().lower()
        cat_filter = self.combo_categoria.currentText()
        status_filter = self.combo_status.currentText().lower()

        self.table.setRowCount(0)
        today = datetime.now().date()
        
        count = 0
        for item in self.data:
            nome = str(item.get("nome") or "").lower()
            corso = str(item.get("corso") or "").lower()
            categoria = str(item.get("categoria") or "").lower()
            status = item.get("stato_certificato")

            if cat_filter != "Tutte" and str(item.get("categoria") or "").upper() != cat_filter.upper():
                continue
            
            tag = "valido"
            if status == "scaduto": tag = "scaduto"
            elif status == "in_scadenza": tag = "in_scadenza"

            if status_filter != "tutti":
                if status_filter == "in scadenza" and tag != "in_scadenza": continue
                if status_filter == "scaduto" and tag != "scaduto": continue
                if status_filter == "valido" and tag != "valido": continue

            if query and query not in nome and query not in corso and query not in categoria:
                continue

            # Days remaining
            scad_str = item.get("data_scadenza") or ""
            days_str = ""
            if scad_str:
                try:
                    dt = datetime.strptime(scad_str, "%d/%m/%Y").date()
                    days_str = str((dt - today).days)
                except: pass

            row = self.table.rowCount()
            self.table.insertRow(row)
            
            bg_color = None
            if tag == "scaduto": bg_color = QColor("#FECACA")
            elif tag == "in_scadenza": bg_color = QColor("#FED7AA")
            elif tag == "valido": bg_color = QColor("#BBF7D0")

            cols = [item.get("nome") or "N/D", item.get("corso") or "N/D", item.get("categoria") or "ALTRO", scad_str, days_str]
            for i, val in enumerate(cols):
                q_item = QTableWidgetItem(val)
                if bg_color: q_item.setBackground(QBrush(bg_color))
                self.table.setItem(row, i, q_item)
            
            count += 1
        
        self.lbl_count.setText(f"{count} certificati")

    def _reset_filters(self):
        self.entry_search.clear()
        self.combo_categoria.setCurrentText("Tutte")
        self.combo_status.setCurrentText("Tutti")
        self.filter_data()

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Esporta PDF", "report_scadenze.pdf", "PDF Files (*.pdf)")
        if not path: return
        
        runner = TaskRunner(self, "Esportazione", "Generazione PDF in corso...")
        try:
            def task():
                import requests
                url = f"{self.controller.api_client.base_url}/notifications/export-report"
                res = requests.get(url, headers=self.controller.api_client._get_headers())
                res.raise_for_status()
                with open(path, "wb") as f: f.write(res.content)
            runner.run(task)
            QMessageBox.information(self, "Successo", f"PDF salvato in: {path}")
            open_file(path)
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))

    def send_email(self):
        if QMessageBox.question(self, "Conferma", "Inviare il report scadenze via email?") == QMessageBox.Yes:
            runner = TaskRunner(self, "Invio Email", "Invio in corso...")
            try:
                def task():
                    import requests
                    url = f"{self.controller.api_client.base_url}/notifications/send-manual-alert"
                    res = requests.post(url, headers=self.controller.api_client._get_headers())
                    res.raise_for_status()
                runner.run(task)
                QMessageBox.information(self, "Successo", "Email inviata correttamente.")
            except Exception as e:
                QMessageBox.critical(self, "Errore", str(e))
