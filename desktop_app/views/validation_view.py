import os
import threading
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMenu, QMessageBox, QTabWidget, QDialog, 
    QFormLayout, QDialogButtonBox, QListWidget, QAbstractItemView,
    QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QPoint
from PySide6.QtGui import QAction, QKeySequence, QShortcut, QColor

from app.core.config import settings
from app.core.constants import CATEGORIE_STATICHE
from app.services.document_locator import find_document
from desktop_app.utils import ProgressTaskRunner, open_file


class ValidationView(QWidget):
    data_signal = Signal(list)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.data = []
        self.orphan_data = []
        self.setStyleSheet("background-color: #F3F4F6;")

        self.setup_ui()
        self.setup_shortcuts()
        self.data_signal.connect(self._update_data)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.sub_tabs = QTabWidget()
        self.sub_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #D1D5DB; top: -1px; background: white; }
            QTabBar::tab { padding: 8px 20px; font-weight: bold; background: #E5E7EB; border: 1px solid #D1D5DB; }
            QTabBar::tab:selected { background: white; border-bottom-color: white; }
        """)

        # Tab 1: Da Convalidare
        self.tab_validate = QWidget()
        self._setup_validation_tab()
        self.sub_tabs.addTab(self.tab_validate, "Da Convalidare")

        # Tab 2: Orfani
        self.tab_orphans = QWidget()
        self._setup_orphans_tab()
        self.sub_tabs.addTab(self.tab_orphans, "Orfani (Non Associati)")

        main_layout.addWidget(self.sub_tabs)

    def _setup_validation_tab(self):
        layout = QVBoxLayout(self.tab_validate)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet("background-color: #F3F4F6; border: none;")
        t_layout = QHBoxLayout(toolbar)
        t_layout.setContentsMargins(10, 0, 10, 0)

        btn_refresh = QPushButton("Aggiorna")
        btn_refresh.clicked.connect(self.refresh_data)
        t_layout.addWidget(btn_refresh)

        t_layout.addWidget(QLabel("Cerca:"))
        self.entry_search = QLineEdit()
        self.entry_search.setPlaceholderText("Filtra...")
        self.entry_search.textChanged.connect(self.filter_data)
        t_layout.addWidget(self.entry_search)

        t_layout.addWidget(QLabel("Categoria:"))
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItem("Tutte")
        self.combo_categoria.currentTextChanged.connect(self.filter_data)
        t_layout.addWidget(self.combo_categoria)

        t_layout.addStretch()
        self.lbl_count = QLabel("")
        t_layout.addWidget(self.lbl_count)

        layout.addWidget(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Dipendente", "Documento", "Categoria", "Rilascio", "Scadenza"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.doubleClicked.connect(self.on_double_click)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)

    def _setup_orphans_tab(self):
        layout = QVBoxLayout(self.tab_orphans)
        
        toolbar = QFrame()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet("background-color: #FEF3C7; border: none;")
        t_layout = QHBoxLayout(toolbar)
        
        btn_refresh = QPushButton("Aggiorna")
        btn_refresh.clicked.connect(self.refresh_data)
        t_layout.addWidget(btn_refresh)

        lbl_warn = QLabel("⚠ Certificati non associati")
        lbl_warn.setStyleSheet("color: #92400E; font-weight: bold;")
        t_layout.addWidget(lbl_warn)

        t_layout.addStretch()

        btn_assign = QPushButton("Assegna a Dipendente")
        btn_assign.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; border-radius: 4px; padding: 5px 10px;")
        btn_assign.clicked.connect(self._assign_orphan)
        t_layout.addWidget(btn_assign)

        btn_del = QPushButton("Elimina Selezionati")
        btn_del.setStyleSheet("background-color: #DC2626; color: white; font-weight: bold; border-radius: 4px; padding: 5px 10px;")
        btn_del.clicked.connect(self._delete_orphans)
        t_layout.addWidget(btn_del)

        self.lbl_orphan_count = QLabel("")
        t_layout.addWidget(self.lbl_orphan_count)

        layout.addWidget(toolbar)

        self.table_orphans = QTableWidget()
        self.table_orphans.setColumnCount(6)
        self.table_orphans.setHorizontalHeaderLabels(["ID", "Nome Rilevato", "Documento", "Categoria", "Rilascio", "Scadenza"])
        self.table_orphans.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_orphans.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_orphans.setAlternatingRowColors(True)
        self.table_orphans.doubleClicked.connect(self._assign_orphan)
        
        layout.addWidget(self.table_orphans)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("F5"), self, self.refresh_data)
        QShortcut(QKeySequence("Del"), self, self.delete_selected)
        QShortcut(QKeySequence("Ctrl+A"), self, self.table.selectAll)
        QShortcut(QKeySequence("Ctrl+F"), self, self.entry_search.setFocus)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        action_open_pdf = menu.addAction("Apri File PDF")
        action_open_folder = menu.addAction("Apri Cartella")
        menu.addSeparator()
        action_validate = menu.addAction("Convalida")
        menu.addSeparator()
        action_delete = menu.addAction("Elimina")

        action_open_pdf.triggered.connect(self.open_file)
        action_open_folder.triggered.connect(self.open_folder)
        action_validate.triggered.connect(self.on_double_click)
        action_delete.triggered.connect(self.delete_selected)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def refresh_data(self):
        def fetch():
            try:
                new_data = self.controller.api_client.get("certificati", params={"validated": "false"})
                self.data_signal.emit(new_data)
            except Exception as e:
                # Need thread-safe way to show error
                pass 
        threading.Thread(target=fetch, daemon=True).start()

    @Slot(list)
    def _update_data(self, new_data):
        self.data = [c for c in new_data if c.get("dipendente_id") or c.get("matricola")]
        self.orphan_data = [c for c in new_data if not c.get("dipendente_id") and not c.get("matricola")]
        
        # Update category filter
        categories = set(str(item.get("categoria", "")).upper() for item in self.data if item.get("categoria"))
        self.combo_categoria.blockSignals(True)
        current = self.combo_categoria.currentText()
        self.combo_categoria.clear()
        self.combo_categoria.addItem("Tutte")
        self.combo_categoria.addItems(sorted(categories))
        self.combo_categoria.setCurrentText(current if current in categories or current == "Tutte" else "Tutte")
        self.combo_categoria.blockSignals(False)

        self.filter_data()
        self._filter_orphans()

    def filter_data(self):
        query = self.entry_search.text().lower()
        cat_filter = self.combo_categoria.currentText()
        
        self.table.setRowCount(0)
        count = 0
        for item in self.data:
            nome = str(item.get("nome") or "").lower()
            corso = str(item.get("corso") or "").lower()
            categoria = str(item.get("categoria") or "").lower()

            if cat_filter != "Tutte" and str(item.get("categoria") or "").upper() != cat_filter.upper():
                continue
            if query and query not in nome and query not in corso and query not in categoria:
                continue

            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(item.get("id"))))
            self.table.setItem(row, 1, QTableWidgetItem(item.get("nome") or "N/D"))
            self.table.setItem(row, 2, QTableWidgetItem(item.get("corso") or "N/D"))
            self.table.setItem(row, 3, QTableWidgetItem(item.get("categoria") or "ALTRO"))
            self.table.setItem(row, 4, QTableWidgetItem(item.get("data_rilascio") or ""))
            self.table.setItem(row, 5, QTableWidgetItem(item.get("data_scadenza") or "NESSUNA"))
            count += 1
        
        self.lbl_count.setText(f"{count} da convalidare")

    def _filter_orphans(self):
        self.table_orphans.setRowCount(0)
        for item in self.orphan_data:
            row = self.table_orphans.rowCount()
            self.table_orphans.insertRow(row)
            self.table_orphans.setItem(row, 0, QTableWidgetItem(str(item.get("id"))))
            self.table_orphans.setItem(row, 1, QTableWidgetItem(item.get("nome_dipendente_raw") or item.get("nome") or "Non ident."))
            self.table_orphans.setItem(row, 2, QTableWidgetItem(item.get("corso") or ""))
            self.table_orphans.setItem(row, 3, QTableWidgetItem(item.get("categoria") or "ALTRO"))
            self.table_orphans.setItem(row, 4, QTableWidgetItem(item.get("data_rilascio") or ""))
            self.table_orphans.setItem(row, 5, QTableWidgetItem(item.get("data_scadenza") or ""))
        
        count = len(self.orphan_data)
        self.lbl_orphan_count.setText(f"{count} orfani")
        self.sub_tabs.setTabText(1, f" Orfani ({count})" if count > 0 else " Orfani (Non Associati)")

    def open_file(self):
        row = self.table.currentRow()
        if row < 0: return
        cert_id = self.table.item(row, 0).text()
        cert = next((x for x in self.data if str(x.get("id")) == cert_id), None)
        if not cert: return

        db_path = settings.DOCUMENTS_FOLDER
        if not db_path:
            QMessageBox.critical(self, "Errore", "Percorso Database non configurato.")
            return

        search_data = {
            "nome": cert.get("nome") or cert.get("nome_dipendente_raw"),
            "matricola": cert.get("matricola"),
            "categoria": cert.get("categoria"),
            "data_scadenza": cert.get("data_scadenza"),
        }
        path = find_document(db_path, search_data)
        if path and os.path.exists(path):
            open_file(path)
        else:
            QMessageBox.warning(self, "Attenzione", f"File PDF non trovato per {search_data['nome']}")

    def open_folder(self):
        row = self.table.currentRow()
        if row < 0: return
        cert_id = self.table.item(row, 0).text()
        cert = next((x for x in self.data if str(x.get("id")) == cert_id), None)
        if not cert: return

        db_path = settings.DOCUMENTS_FOLDER
        if not db_path: return

        search_data = {"nome": cert.get("nome"), "matricola": cert.get("matricola"), "categoria": cert.get("categoria"), "data_scadenza": cert.get("data_scadenza")}
        path = find_document(db_path, search_data)
        if path and os.path.exists(path):
            open_file(os.path.dirname(path))
        else:
            open_file(db_path)

    def delete_selected(self):
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

    def on_double_click(self, _):
        rows = sorted(set(index.row() for index in self.table.selectedIndexes()))
        if not rows: return
        
        if len(rows) > 1:
            self.batch_validate(rows)
        else:
            cert_id = self.table.item(rows[0], 0).text()
            cert = next((x for x in self.data if str(x.get("id")) == cert_id), None)
            if cert:
                dialog = ValidationDialog(self, self.controller, cert)
                if dialog.exec():
                    self.refresh_data()

    def batch_validate(self, rows):
        if QMessageBox.question(self, "Conferma", f"Convalidare {len(rows)} certificati?") != QMessageBox.Yes:
            return
        cert_ids = [self.table.item(r, 0).text() for r in rows]
        runner = ProgressTaskRunner(self, "Convalida", "Convalida in corso...")
        try:
            runner.run(self._validate_single_cert, cert_ids)
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))

    def _validate_single_cert(self, cert_id):
        url = f"{self.controller.api_client.base_url}/certificati/{cert_id}/valida"
        res = requests.put(url, headers=self.controller.api_client._get_headers())
        res.raise_for_status()
        return cert_id

    def _assign_orphan(self):
        rows = sorted(set(index.row() for index in self.table_orphans.selectedIndexes()))
        if not rows: return
        
        try:
            dipendenti = self.controller.api_client.get_dipendenti_list()
            selected_ids = [self.table_orphans.item(r, 0).text() for r in rows]
            dialog = AssignOrphanDialog(self, self.controller, selected_ids, dipendenti)
            if dialog.exec():
                self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))

    def _delete_orphans(self):
        rows = sorted(set(index.row() for index in self.table_orphans.selectedIndexes()), reverse=True)
        if not rows: return
        if QMessageBox.question(self, "Conferma", f"Eliminare {len(rows)} certificati orfani?") != QMessageBox.Yes:
            return
        cert_ids = [self.table_orphans.item(r, 0).text() for r in rows]
        runner = ProgressTaskRunner(self, "Eliminazione", "Eliminazione in corso...")
        try:
            runner.run(self.controller.api_client.delete_certificato, cert_ids)
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))


class ValidationDialog(QDialog):
    def __init__(self, parent, controller, cert_data):
        super().__init__(parent)
        self.controller = controller
        self.cert = cert_data
        self.setWindowTitle(f"Convalida Certificato #{cert_data.get('id')}")
        self.setFixedSize(500, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.edit_dip = QLineEdit(self.cert.get("nome") or "")
        self.edit_corso = QLineEdit(self.cert.get("corso") or "")
        self.combo_cat = QComboBox()
        self.combo_cat.addItems(sorted(CATEGORIE_STATICHE))
        current_cat = self.cert.get("categoria") or "ALTRO"
        self.combo_cat.setCurrentText(current_cat if current_cat in CATEGORIE_STATICHE else "ALTRO")
        
        self.edit_ril = QLineEdit(self.cert.get("data_rilascio") or "")
        self.edit_scad = QLineEdit(self.cert.get("data_scadenza") or "")
        
        form.addRow("Dipendente:", self.edit_dip)
        form.addRow("Corso:", self.edit_corso)
        form.addRow("Categoria:", self.combo_cat)
        form.addRow("Rilascio (DD/MM/YYYY):", self.edit_ril)
        form.addRow("Scadenza (DD/MM/YYYY):", self.edit_scad)
        
        layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        btn_del = QPushButton("ELIMINA")
        btn_del.setStyleSheet("background-color: #DC2626; color: white; font-weight: bold;")
        btn_del.clicked.connect(self.delete_cert)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.button(QDialogButtonBox.Ok).setText("CONVALIDA")
        btn_box.button(QDialogButtonBox.Ok).setStyleSheet("background-color: #10B981; color: white; font-weight: bold;")
        btn_box.accepted.connect(self.validate_cert)
        btn_box.rejected.connect(self.reject)
        
        btn_layout.addWidget(btn_del)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_box)
        layout.addLayout(btn_layout)

    def validate_cert(self):
        data = {
            "nome": self.edit_dip.text(),
            "corso": self.edit_corso.text(),
            "categoria": self.combo_cat.currentText(),
            "data_rilascio": self.edit_ril.text(),
            "data_scadenza": self.edit_scad.text(),
        }
        try:
            self.controller.api_client.update_certificato(self.cert["id"], data)
            url = f"{self.controller.api_client.base_url}/certificati/{self.cert['id']}/valida"
            requests.put(url, headers=self.controller.api_client._get_headers())
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))

    def delete_cert(self):
        if QMessageBox.question(self, "Conferma", "Eliminare definitivamente?") == QMessageBox.Yes:
            try:
                self.controller.api_client.delete_certificato(self.cert["id"])
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Errore", str(e))


class AssignOrphanDialog(QDialog):
    def __init__(self, parent, controller, cert_ids, dipendenti):
        super().__init__(parent)
        self.controller = controller
        self.cert_ids = cert_ids
        self.dipendenti = dipendenti
        self.setWindowTitle(f"Assegna {len(cert_ids)} Certificati")
        self.setFixedSize(500, 450)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Assegna {len(self.cert_ids)} certificati a un dipendente:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Cerca dipendente...")
        self.search_edit.textChanged.connect(self.filter_dipendenti)
        layout.addWidget(self.search_edit)
        
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        self.filter_dipendenti()
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.assign)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def filter_dipendenti(self):
        query = self.search_edit.text().lower()
        self.list_widget.clear()
        self.filtered_list = []
        for dip in self.dipendenti:
            display = f"{dip.get('cognome', '')} {dip.get('nome', '')} ({dip.get('matricola', '')})"
            if query in display.lower():
                self.list_widget.addItem(display)
                self.filtered_list.append(dip)

    def assign(self):
        idx = self.list_widget.currentRow()
        if idx < 0: return
        dip = self.filtered_list[idx]
        dip_id = dip.get("id")
        dip_name = f"{dip.get('cognome', '')} {dip.get('nome', '')}".strip()
        
        if QMessageBox.question(self, "Conferma", f"Assegnare a {dip_name}?") != QMessageBox.Yes:
            return
            
        success = 0
        for cid in self.cert_ids:
            try:
                self.controller.api_client.update_certificato(cid, {"dipendente_id": dip_id, "nome": dip_name})
                success += 1
            except: pass
        
        QMessageBox.information(self, "Fine", f"Assegnati {success}/{len(self.cert_ids)} certificati.")
        self.accept()
