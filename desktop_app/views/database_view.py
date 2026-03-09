import os
import threading
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMenu, QMessageBox, QFrame, QAbstractItemView
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QAction, QKeySequence, QShortcut, QColor, QBrush

from app.core.config import settings
from app.services.document_locator import find_document
from desktop_app.utils import ProgressTaskRunner, open_file
from desktop_app.views.edit_certificato_dialog import EditCertificatoDialog


class DatabaseView(QWidget):
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
        toolbar.setFixedHeight(60)
        toolbar.setStyleSheet("background-color: #F3F4F6; border: none;")
        t_layout = QHBoxLayout(toolbar)
        
        t_layout.addWidget(QLabel("Cerca:"))
        self.entry_search = QLineEdit()
        self.entry_search.setPlaceholderText("Filtra per nome, corso...")
        self.entry_search.textChanged.connect(self.filter_data)
        t_layout.addWidget(self.entry_search)

        t_layout.addWidget(QLabel("Categoria:"))
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItem("Tutte")
        self.combo_categoria.currentTextChanged.connect(self.filter_data)
        t_layout.addWidget(self.combo_categoria)

        t_layout.addWidget(QLabel("Stato:"))
        self.combo_status = QComboBox()
        self.combo_status.addItems(["Tutti", "Attivo", "In Scadenza", "Scaduto"])
        self.combo_status.currentTextChanged.connect(self.filter_data)
        t_layout.addWidget(self.combo_status)

        btn_refresh = QPushButton("Aggiorna")
        btn_refresh.clicked.connect(self.refresh_data)
        t_layout.addWidget(btn_refresh)

        t_layout.addStretch()
        self.lbl_count = QLabel("")
        t_layout.addWidget(self.lbl_count)

        layout.addWidget(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Dipendente", "Documento", "Categoria", "Rilascio", "Scadenza", "Stato"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.doubleClicked.connect(self.open_file)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.table)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("F5"), self, self.refresh_data)
        QShortcut(QKeySequence("Del"), self, self.delete_item)
        QShortcut(QKeySequence("F2"), self, self.edit_item)
        QShortcut(QKeySequence("Ctrl+A"), self, self.table.selectAll)
        QShortcut(QKeySequence("Ctrl+F"), self, self.entry_search.setFocus)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        action_open_pdf = menu.addAction("Apri File PDF")
        action_open_folder = menu.addAction("Apri Cartella")
        menu.addSeparator()
        action_edit = menu.addAction("Modifica Dati")
        action_delete = menu.addAction("Elimina")

        action_open_pdf.triggered.connect(self.open_file)
        action_open_folder.triggered.connect(self.open_folder)
        action_edit.triggered.connect(self.edit_item)
        action_delete.triggered.connect(self.delete_item)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def refresh_data(self):
        def fetch():
            try:
                new_data = self.controller.api_client.get("certificati", params={"validated": "true"})
                self.data_signal.emit(new_data)
            except Exception: pass
        threading.Thread(target=fetch, daemon=True).start()

    @Slot(list)
    def _update_data(self, new_data):
        self.data = new_data
        
        # Update categories
        categories = set(str(item.get("categoria", "")).upper() for item in self.data if item.get("categoria"))
        self.combo_categoria.blockSignals(True)
        current = self.combo_categoria.currentText()
        self.combo_categoria.clear()
        self.combo_categoria.addItem("Tutte")
        self.combo_categoria.addItems(sorted(categories))
        self.combo_categoria.setCurrentText(current if current in categories or current == "Tutte" else "Tutte")
        self.combo_categoria.blockSignals(False)

        self.filter_data()

    def filter_data(self):
        query = self.entry_search.text().lower()
        status_filter = self.combo_status.currentText().lower()
        cat_filter = self.combo_categoria.currentText()

        self.table.setRowCount(0)
        count = 0
        for item in self.data:
            nome = str(item.get("nome") or "").lower()
            corso = str(item.get("corso") or "").lower()
            categoria = str(item.get("categoria") or "").lower()
            stato = str(item.get("stato_certificato") or "").lower()

            if cat_filter != "Tutte" and str(item.get("categoria") or "").upper() != cat_filter.upper():
                continue
            if status_filter != "tutti":
                if status_filter == "in scadenza" and stato != "in_scadenza": continue
                if status_filter == "scaduto" and stato != "scaduto": continue
                if status_filter == "attivo" and stato != "attivo": continue
            if query and query not in nome and query not in corso and query not in categoria:
                continue

            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Colors
            bg_color = None
            if stato == "scaduto": bg_color = QColor("#FECACA")
            elif stato == "in_scadenza": bg_color = QColor("#FED7AA")
            elif stato == "attivo": bg_color = QColor("#BBF7D0")

            cols = [
                str(item.get("id")),
                item.get("nome") or "N/D",
                item.get("corso") or "N/D",
                item.get("categoria") or "ALTRO",
                item.get("data_rilascio") or "",
                item.get("data_scadenza") or "NESSUNA",
                stato.replace("_", " ").upper()
            ]
            
            for i, val in enumerate(cols):
                q_item = QTableWidgetItem(val)
                if bg_color: q_item.setBackground(QBrush(bg_color))
                self.table.setItem(row, i, q_item)
            
            count += 1
        
        self.lbl_count.setText(f"{count} certificati")

    def open_file(self):
        row = self.table.currentRow()
        if row < 0: return
        cert_id = self.table.item(row, 0).text()
        cert = next((x for x in self.data if str(x["id"]) == cert_id), None)
        if not cert: return

        db_path = settings.DOCUMENTS_FOLDER
        if not db_path:
            QMessageBox.critical(self, "Errore", "Percorso Database non configurato.")
            return

        search_data = {"nome": cert.get("nome"), "matricola": cert.get("matricola"), "categoria": cert.get("categoria"), "data_scadenza": cert.get("data_scadenza")}
        path = find_document(db_path, search_data)
        if path and os.path.exists(path):
            open_file(path)
        else:
            QMessageBox.warning(self, "Attenzione", f"File PDF non trovato per {search_data['nome']}")

    def open_folder(self):
        row = self.table.currentRow()
        if row < 0: return
        cert_id = self.table.item(row, 0).text()
        cert = next((x for x in self.data if str(x["id"]) == cert_id), None)
        if not cert: return

        db_path = settings.DOCUMENTS_FOLDER
        if not db_path: return

        search_data = {"nome": cert.get("nome"), "matricola": cert.get("matricola"), "categoria": cert.get("categoria"), "data_scadenza": cert.get("data_scadenza")}
        path = find_document(db_path, search_data)
        if path and os.path.exists(path):
            open_file(os.path.dirname(path))
        else:
            open_file(db_path)

    def edit_item(self):
        row = self.table.currentRow()
        if row < 0: return
        cert_id = self.table.item(row, 0).text()
        cert = next((x for x in self.data if str(x["id"]) == cert_id), None)
        if not cert: return
        
        dialog = EditCertificatoDialog(self, self.controller, cert)
        if dialog.exec():
            self.refresh_data()

    def delete_item(self):
        rows = sorted(set(index.row() for index in self.table.selectedIndexes()), reverse=True)
        if not rows: return
        if QMessageBox.question(self, "Conferma", f"Eliminare {len(rows)} certificati?") != QMessageBox.Yes:
            return

        cert_ids = [self.table.item(r, 0).text() for r in rows]
        runner = ProgressTaskRunner(self, "Eliminazione", "Eliminazione in corso...")
        try:
            runner.run(self.controller.api_client.delete_certificato, cert_ids)
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))
