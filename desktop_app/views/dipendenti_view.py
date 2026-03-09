import os
import threading
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, 
    QMenu, QMessageBox, QFrame, QDialog, QFormLayout, 
    QDialogButtonBox, QAbstractItemView, QComboBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction, QKeySequence, QShortcut

from app.core.config import settings
from app.services.document_locator import find_document
from desktop_app.utils import format_date_to_ui, open_file


class DipendentiView(QWidget):
    data_signal = Signal(list)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.data = []
        self.setStyleSheet("background-color: #F3F4F6;")

        self.setup_ui()
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
        
        btn_refresh = QPushButton("Aggiorna")
        btn_refresh.clicked.connect(self.refresh_data)
        t_layout.addWidget(btn_refresh)

        btn_new = QPushButton("Nuovo Dipendente")
        btn_new.setStyleSheet("background-color: #10B981; color: white; font-weight: bold;")
        btn_new.clicked.connect(self.add_dipendente)
        t_layout.addWidget(btn_new)

        btn_mansione = QPushButton("Assegna Mansione")
        btn_mansione.setStyleSheet("background-color: #2563EB; color: white;")
        btn_mansione.clicked.connect(self._bulk_assign_mansione)
        t_layout.addWidget(btn_mansione)

        btn_reparto = QPushButton("Assegna Reparto")
        btn_reparto.setStyleSheet("background-color: #7C3AED; color: white;")
        btn_reparto.clicked.connect(self._bulk_assign_reparto)
        t_layout.addWidget(btn_reparto)

        t_layout.addSpacing(20)
        t_layout.addWidget(QLabel("Cerca:"))
        self.entry_search = QLineEdit()
        self.entry_search.setPlaceholderText("Cerca...")
        self.entry_search.textChanged.connect(self.filter_data)
        t_layout.addWidget(self.entry_search)

        t_layout.addStretch()
        self.lbl_selection = QLabel("")
        t_layout.addWidget(self.lbl_selection)

        layout.addWidget(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Matricola", "Cognome e Nome", "Data Nascita", "Mansione", "Reparto"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.doubleClicked.connect(self.on_double_click)
        self.table.itemSelectionChanged.connect(self._on_selection_change)
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.table)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        action_storico = menu.addAction("Visualizza Storico Certificati")
        menu.addSeparator()
        action_edit = menu.addAction("Modifica Dati")
        menu.addSeparator()
        action_mansione = menu.addAction("Assegna Mansione (Selezione)")
        action_reparto = menu.addAction("Assegna Reparto (Selezione)")

        action_storico.triggered.connect(self.show_storico)
        action_edit.triggered.connect(self.on_double_click)
        action_mansione.triggered.connect(self._bulk_assign_mansione)
        action_reparto.triggered.connect(self._bulk_assign_reparto)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _on_selection_change(self):
        count = len(set(index.row() for index in self.table.selectedIndexes()))
        self.lbl_selection.setText(f"{count} selezionati" if count > 1 else "")

    def refresh_data(self):
        def fetch():
            try:
                new_data = self.controller.api_client.get_dipendenti_list()
                self.data_signal.emit(new_data)
            except: pass
        threading.Thread(target=fetch, daemon=True).start()

    @Slot(list)
    def _update_data(self, new_data):
        self.data = new_data
        self.filter_data()

    def filter_data(self):
        query = self.entry_search.text().lower()
        self.table.setRowCount(0)
        for d in self.data:
            display_name = f"{d.get('cognome','') or ''} {d.get('nome','') or ''}".strip().upper()
            matricola = str(d.get("matricola") or "").lower()
            reparto = str(d.get("categoria_reparto") or "").upper()
            
            if query in display_name.lower() or query in matricola or query in reparto.lower():
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(d.get("id"))))
                self.table.setItem(row, 1, QTableWidgetItem(d.get("matricola") or ""))
                self.table.setItem(row, 2, QTableWidgetItem(display_name))
                self.table.setItem(row, 3, QTableWidgetItem(format_date_to_ui(d.get("data_nascita"))))
                self.table.setItem(row, 4, QTableWidgetItem(d.get("mansione") or ""))
                self.table.setItem(row, 5, QTableWidgetItem(reparto))

    def add_dipendente(self):
        dialog = DipendenteDialog(self, self.controller)
        if dialog.exec(): self.refresh_data()

    def on_double_click(self):
        row = self.table.currentRow()
        if row < 0: return
        dip_id = self.table.item(row, 0).text()
        dip_obj = next((x for x in self.data if str(x["id"]) == dip_id), None)
        if dip_obj:
            dialog = DipendenteDialog(self, self.controller, dip_obj)
            if dialog.exec(): self.refresh_data()

    def show_storico(self):
        row = self.table.currentRow()
        if row < 0: return
        dip_id = self.table.item(row, 0).text()
        dip_obj = next((x for x in self.data if str(x["id"]) == dip_id), None)
        if dip_obj:
            StoricoCertificatiDialog(self, self.controller, dip_obj).exec()

    def _bulk_assign_mansione(self):
        rows = list(set(index.row() for index in self.table.selectedIndexes()))
        if not rows: return
        dip_ids = [self.table.item(r, 0).text() for r in rows]
        dialog = BulkAssignDialog(self, self.controller, dip_ids, self.data, "mansione")
        if dialog.exec(): self.refresh_data()

    def _bulk_assign_reparto(self):
        rows = list(set(index.row() for index in self.table.selectedIndexes()))
        if not rows: return
        dip_ids = [self.table.item(r, 0).text() for r in rows]
        dialog = BulkAssignDialog(self, self.controller, dip_ids, self.data, "reparto")
        if dialog.exec(): self.refresh_data()


class StoricoCertificatiDialog(QDialog):
    def __init__(self, parent, controller, dipendente):
        super().__init__(parent)
        self.controller = controller
        self.dipendente = dipendente
        self.setWindowTitle(f"Storico: {dipendente['cognome']} {dipendente['nome']}")
        self.resize(900, 500)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Certificati di: {self.dipendente['cognome']} {self.dipendente['nome']}"))
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Documento", "Categoria", "Emissione", "Scadenza", "Stato"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.doubleClicked.connect(self.open_pdf)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def load_data(self):
        try:
            details = self.controller.api_client.get_dipendente_detail(self.dipendente["id"])
            certs = details.get("certificati", [])
            for c in certs:
                row = self.table.rowCount()
                self.table.insertRow(row)
                scad = c.get("data_scadenza") or "NESSUNA"
                stato = (c.get("stato_certificato") or "N/D").upper()
                
                self.table.setItem(row, 0, QTableWidgetItem(c.get("corso")))
                self.table.setItem(row, 1, QTableWidgetItem(c.get("categoria")))
                self.table.setItem(row, 2, QTableWidgetItem(c.get("data_rilascio")))
                self.table.setItem(row, 3, QTableWidgetItem(scad))
                st_item = QTableWidgetItem(stato)
                
                # Colors
                s = c.get("stato_certificato")
                if s == "scaduto": st_item.setForeground(QColor("red"))
                elif s == "in_scadenza": st_item.setForeground(QColor("orange"))
                elif s == "attivo": st_item.setForeground(QColor("green"))
                
                self.table.setItem(row, 4, st_item)
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))

    def open_pdf(self):
        row = self.table.currentRow()
        if row < 0: return
        categoria = self.table.item(row, 1).text()
        scadenza = self.table.item(row, 3).text()
        if scadenza == "NESSUNA": scadenza = None

        db_path = settings.DOCUMENTS_FOLDER
        if not db_path: return

        search_data = {
            "nome": f"{self.dipendente['cognome']} {self.dipendente['nome']}",
            "matricola": self.dipendente.get("matricola"),
            "categoria": categoria,
            "data_scadenza": scadenza,
        }
        path = find_document(db_path, search_data)
        if path and os.path.exists(path): open_file(path)
        else: QMessageBox.warning(self, "Errore", "PDF non trovato.")


class DipendenteDialog(QDialog):
    def __init__(self, parent, controller, dip_data=None):
        super().__init__(parent)
        self.controller = controller
        self.dip_data = dip_data
        self.setWindowTitle("Modifica Dipendente" if dip_data else "Nuovo Dipendente")
        self.setFixedWidth(450)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.edit_cognome = QLineEdit(self.dip_data.get("cognome") if self.dip_data else "")
        self.edit_nome = QLineEdit(self.dip_data.get("nome") if self.dip_data else "")
        self.edit_matr = QLineEdit(self.dip_data.get("matricola") if self.dip_data else "")
        self.edit_nasc = QLineEdit(format_date_to_ui(self.dip_data.get("data_nascita")) if self.dip_data else "")
        self.edit_mans = QLineEdit(self.dip_data.get("mansione") if self.dip_data else "")
        self.edit_rep = QLineEdit(self.dip_data.get("categoria_reparto") if self.dip_data else "")
        
        form.addRow("Cognome:", self.edit_cognome)
        form.addRow("Nome:", self.edit_nome)
        form.addRow("Matricola:", self.edit_matr)
        form.addRow("Data Nascita (GG/MM/AAAA):", self.edit_nasc)
        form.addRow("Mansione:", self.edit_mans)
        form.addRow("Reparto:", self.edit_rep)
        
        layout.addLayout(form)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        if self.dip_data:
            btn_del = QPushButton("ELIMINA")
            btn_del.setStyleSheet("background-color: #DC2626; color: white;")
            btn_del.clicked.connect(self.delete_dip)
            layout.addWidget(btn_del)
            
        btn_box.accepted.connect(self.save)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def save(self):
        # Date conversion logic
        raw_date = self.edit_nasc.text().strip()
        formatted_date = raw_date
        if "/" in raw_date:
            try:
                from datetime import datetime
                formatted_date = datetime.strptime(raw_date, "%d/%m/%Y").strftime("%Y-%m-%d")
            except: pass

        data = {
            "cognome": self.edit_cognome.text(),
            "nome": self.edit_nome.text(),
            "matricola": self.edit_matr.text(),
            "data_nascita": formatted_date,
            "mansione": self.edit_mans.text(),
            "categoria_reparto": self.edit_rep.text(),
        }
        
        try:
            if self.dip_data: self.controller.api_client.update_dipendente(self.dip_data["id"], data)
            else: self.controller.api_client.create_dipendente(data)
            self.accept()
        except Exception as e: QMessageBox.critical(self, "Errore", str(e))

    def delete_dip(self):
        if QMessageBox.question(self, "Conferma", "Eliminare definitivamente?") == QMessageBox.Yes:
            try:
                self.controller.api_client.delete_dipendente(self.dip_data["id"])
                self.accept()
            except Exception as e: QMessageBox.critical(self, "Errore", str(e))


class BulkAssignDialog(QDialog):
    def __init__(self, parent, controller, dip_ids, all_data, field_type):
        super().__init__(parent)
        self.controller = controller
        self.dip_ids = dip_ids
        self.field_type = field_type
        self.setWindowTitle(f"Assegna {field_type.title()} a {len(dip_ids)} dipendenti")
        self.setFixedWidth(400)
        self.setup_ui(all_data)

    def setup_ui(self, all_data):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Assegnazione massiva {self.field_type}:"))
        
        # Suggestions
        api_field = "mansione" if self.field_type == "mansione" else "categoria_reparto"
        existing = sorted(set(d.get(api_field) for d in all_data if d.get(api_field)))
        
        self.combo = QComboBox()
        self.combo.setEditable(True)
        self.combo.addItems(existing)
        layout.addWidget(self.combo)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.apply)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def apply(self):
        val = self.combo.currentText().strip()
        if not val: return
        
        api_field = "mansione" if self.field_type == "mansione" else "categoria_reparto"
        success = 0
        for did in self.dip_ids:
            try:
                self.controller.api_client.update_dipendente(did, {api_field: val})
                success += 1
            except: pass
        QMessageBox.information(self, "Fine", f"Aggiornati {success}/{len(self.dip_ids)} dipendenti.")
        self.accept()
