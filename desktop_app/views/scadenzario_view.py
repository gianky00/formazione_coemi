import threading
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QMessageBox, QFrame, QFileDialog
)
from PySide6.QtCore import Qt, Signal, Slot, QPoint
from PySide6.QtGui import QKeySequence, QShortcut, QColor, QBrush

from desktop_app.utils import TaskRunner, open_file
from desktop_app.widgets.data_table import DataTable
from desktop_app.widgets.search_bar import SearchBar


class ScadenzarioView(QWidget):
    data_signal = Signal(list)

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.data = []
        
        self.setup_ui()
        self.setup_shortcuts()
        self.data_signal.connect(self._update_data)
        self.refresh_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Toolbar
        self.search_bar = SearchBar("Cerca...", self)
        self.search_bar.add_filter("Categoria", "categoria", ["Tutte"])
        self.search_bar.add_filter("Stato", "stato", ["Tutti", "Valido", "In Scadenza", "Scaduto"])
        self.search_bar.add_refresh_button()
        
        btn_export = QPushButton("Esporta PDF")
        btn_export.setProperty("class", "PrimaryButton")
        btn_export.clicked.connect(self.export_pdf)
        self.search_bar.layout.addWidget(btn_export)

        btn_email = QPushButton("Invia Email")
        btn_email.setProperty("class", "PrimaryButton")
        btn_email.clicked.connect(self.send_email)
        self.search_bar.layout.addWidget(btn_email)

        self.search_bar.text_changed.connect(self.filter_data)
        self.search_bar.filter_changed.connect(lambda k, v: self.filter_data())
        self.search_bar.refresh_requested.connect(self.refresh_data)
        layout.addWidget(self.search_bar)

        # Legend
        legend = QLabel("Rosso=Scaduto | Arancio=In Scadenza | Verde=Valido")
        legend.setProperty("class", "LegendLabel")
        legend.setAlignment(Qt.AlignRight)
        layout.addWidget(legend)

        # Table
        self.table = DataTable(self)
        self.table.set_columns(["Dipendente", "Documento", "Categoria", "Scadenza", "Giorni Rimanenti"])
        layout.addWidget(self.table)

        self.lbl_count = QLabel("")
        layout.addWidget(self.lbl_count)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("F5"), self, self.refresh_data)
        QShortcut(QKeySequence("Esc"), self, self.search_bar.clear)

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
        categories = sorted(set(str(item.get("categoria", "")).upper() for item in self.data if item.get("categoria")))
        combo = self.search_bar.combos["categoria"]
        combo.blockSignals(True)
        combo.clear(); combo.addItem("Tutte"); combo.addItems(categories)
        combo.blockSignals(False)
        self.filter_data()

    def filter_data(self):
        query = self.search_bar.entry_search.text().lower()
        cat_filter = self.search_bar.combos["categoria"].currentText()
        status_filter = self.search_bar.combos["stato"].currentText().lower()

        today = datetime.now().date()
        filtered = []
        for item in self.data:
            if cat_filter != "Tutte" and str(item.get("categoria") or "").upper() != cat_filter.upper(): continue
            
            stato = item.get("stato_certificato")
            tag = "valido"
            if stato == "scaduto": tag = "scaduto"
            elif stato == "in_scadenza": tag = "in_scadenza"

            if status_filter != "tutti":
                if status_filter == "in scadenza" and tag != "in_scadenza": continue
                if status_filter == "scaduto" and tag != "scaduto": continue
                if status_filter == "valido" and tag != "valido": continue

            txt = f"{item.get('nome','')} {item.get('corso','')}".lower()
            if query and query not in txt: continue
            
            # Days remaining helper
            scad_str = item.get("data_scadenza") or ""
            item["giorni_rimanenti"] = ""
            if scad_str:
                try:
                    dt = datetime.strptime(scad_str, "%d/%m/%Y").date()
                    item["giorni_rimanenti"] = str((dt - today).days)
                except: pass
            
            filtered.append(item)

        mapping = ["nome", "corso", "categoria", "data_scadenza", "giorni_rimanenti"]
        self.table.load_data(filtered, mapping, color_callback=self._get_row_color)
        self.lbl_count.setText(f"{len(filtered)} certificati")

    def _get_row_color(self, item):
        s = item.get("stato_certificato")
        if s == "scaduto": return QColor("#FECACA")
        if s == "in_scadenza": return QColor("#FED7AA")
        if s == "attivo": return QColor("#BBF7D0")
        return None

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Esporta PDF", "report.pdf", "PDF (*.pdf)")
        if path:
            try:
                def task():
                    res = self.controller.api_client.get("notifications/export-report")
                    with open(path, "wb") as f: f.write(res.content)
                TaskRunner(self, "Esportazione").run(task)
                open_file(path)
            except Exception as e: QMessageBox.critical(self, "Errore", str(e))

    def send_email(self):
        if QMessageBox.question(self, "Conferma", "Inviare report?") == QMessageBox.Yes:
            try:
                TaskRunner(self, "Invio Email").run(lambda: self.controller.api_client.post("notifications/send-manual-alert"))
                QMessageBox.information(self, "OK", "Inviato.")
            except Exception as e: QMessageBox.critical(self, "Errore", str(e))
