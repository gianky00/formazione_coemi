import builtins
import contextlib
import os
import threading

import requests
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMenu,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.config import settings
from app.core.constants import CATEGORIE_STATICHE
from app.services.document_locator import find_document
from desktop_app.utils import ProgressTaskRunner, open_file
from desktop_app.widgets.data_table import DataTable
from desktop_app.widgets.search_bar import SearchBar


class ValidationView(QWidget):
    data_signal = Signal(list)

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.data = []
        self.orphan_data = []

        self.setup_ui()
        self.setup_shortcuts()
        self.data_signal.connect(self._update_data)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.sub_tabs = QTabWidget()

        # Tab 1: Da Convalidare
        self.tab_validate = QWidget()
        self._setup_validation_tab()
        self.sub_tabs.addTab(self.tab_validate, "Da Convalidare")

        # Tab 2: Orfani
        self.tab_orphans = QWidget()
        self._setup_orphans_tab()
        self.sub_tabs.addTab(self.tab_orphans, "Orfani")

        main_layout.addWidget(self.sub_tabs)

    def _setup_validation_tab(self):
        layout = QVBoxLayout(self.tab_validate)

        self.search_bar = SearchBar("Filtra...", self)
        self.search_bar.add_filter("Categoria", "categoria", ["Tutte"])
        self.search_bar.add_refresh_button()
        self.search_bar.text_changed.connect(self.filter_data)
        self.search_bar.filter_changed.connect(lambda k, v: self.filter_data())
        self.search_bar.refresh_requested.connect(self.refresh_data)
        layout.addWidget(self.search_bar)

        self.table = DataTable(self)
        self.table.set_columns(
            ["ID", "Dipendente", "Documento", "Categoria", "Rilascio", "Scadenza"]
        )
        self.table.row_double_clicked.connect(self.on_double_click)
        self.table.context_menu_requested.connect(self.show_context_menu)
        layout.addWidget(self.table)

        self.lbl_count = QLabel("")
        layout.addWidget(self.lbl_count)

    def _setup_orphans_tab(self):
        layout = QVBoxLayout(self.tab_orphans)

        toolbar = QFrame()
        toolbar.setObjectName("StatusBanner")
        t_layout = QHBoxLayout(toolbar)

        btn_assign = QPushButton("Assegna Selezionati")
        btn_assign.setProperty("class", "PrimaryButton")
        btn_assign.clicked.connect(self._assign_orphan)
        t_layout.addWidget(btn_assign)

        btn_del = QPushButton("Elimina Selezionati")
        btn_del.setProperty("class", "DangerButton")
        btn_del.clicked.connect(self._delete_orphans)
        t_layout.addWidget(btn_del)

        t_layout.addStretch()
        self.lbl_orphan_count = QLabel("")
        t_layout.addWidget(self.lbl_orphan_count)
        layout.addWidget(toolbar)

        self.table_orphans = DataTable(self)
        self.table_orphans.set_columns(
            ["ID", "Nome Rilevato", "Documento", "Categoria", "Rilascio", "Scadenza"]
        )
        self.table_orphans.row_double_clicked.connect(self._assign_orphan)
        layout.addWidget(self.table_orphans)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("F5"), self, self.refresh_data)
        QShortcut(QKeySequence("Del"), self, self.delete_selected)

    def show_context_menu(self, pos, cert):
        menu = QMenu(self)
        menu.addAction("Apri File PDF", lambda: self.open_file(cert))
        menu.addAction("Apri Cartella", lambda: self.open_folder(cert))
        menu.addSeparator()
        menu.addAction("Convalida", lambda: self.on_double_click(cert))
        menu.addAction("Elimina", lambda: self.delete_selected(cert))
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def refresh_data(self):
        def fetch():
            try:
                new_data = self.controller.api_client.get(
                    "certificati", params={"validated": "false"}
                )
                self.data_signal.emit(new_data)
            except Exception:
                pass

        threading.Thread(target=fetch, daemon=True).start()

    @Slot(list)
    def _update_data(self, new_data):
        self.data = [c for c in new_data if c.get("dipendente_id") or c.get("matricola")]
        self.orphan_data = [
            c for c in new_data if not c.get("dipendente_id") and not c.get("matricola")
        ]

        # Update category filter
        categories = sorted(
            {str(item.get("categoria", "")).upper() for item in self.data if item.get("categoria")}
        )
        combo = self.search_bar.combos["categoria"]
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("Tutte")
        combo.addItems(categories)
        combo.blockSignals(False)

        self.filter_data()
        self._refresh_orphans()

    def filter_data(self):
        query = self.search_bar.entry_search.text().lower()
        cat_filter = self.search_bar.combos["categoria"].currentText()

        filtered = []
        for item in self.data:
            if (
                cat_filter != "Tutte"
                and str(item.get("categoria") or "").upper() != cat_filter.upper()
            ):
                continue
            txt = f"{item.get('nome', '')} {item.get('corso', '')}".lower()
            if query and query not in txt:
                continue
            filtered.append(item)

        mapping = ["id", "nome", "corso", "categoria", "data_rilascio", "data_scadenza"]
        self.table.load_data(filtered, mapping)
        self.lbl_count.setText(f"{len(filtered)} da convalidare")

    def _refresh_orphans(self):
        mapping = [
            "id",
            "nome_dipendente_raw",
            "corso",
            "categoria",
            "data_rilascio",
            "data_scadenza",
        ]
        self.table_orphans.load_data(self.orphan_data, mapping)
        count = len(self.orphan_data)
        self.lbl_orphan_count.setText(f"{count} orfani")
        self.sub_tabs.setTabText(1, f" Orfani ({count})" if count > 0 else " Orfani")

    def open_file(self, cert):
        if not settings.DOCUMENTS_FOLDER:
            return
        path = find_document(settings.DOCUMENTS_FOLDER, cert)
        if path and os.path.exists(path):
            open_file(path)
        else:
            QMessageBox.warning(self, "Errore", "File non trovato.")

    def open_folder(self, cert):
        if not settings.DOCUMENTS_FOLDER:
            return
        path = find_document(settings.DOCUMENTS_FOLDER, cert)
        open_file(
            os.path.dirname(path) if path and os.path.exists(path) else settings.DOCUMENTS_FOLDER
        )

    def delete_selected(self, cert=None):
        selected = [cert] if cert else self.table.get_selected_data()
        if (
            selected
            and QMessageBox.question(self, "Conferma", f"Eliminare {len(selected)} certificati?")
            == QMessageBox.Yes
        ):
            ids = [str(s["id"]) for s in selected]
            ProgressTaskRunner(self).run(self.controller.api_client.delete_certificato, ids)
            self.refresh_data()

    def on_double_click(self, cert):
        if cert and ValidationDialog(self, self.controller, cert).exec():
            self.refresh_data()

    def _assign_orphan(self, cert=None):
        selected = [cert] if cert else self.table_orphans.get_selected_data()
        if not selected:
            return
        try:
            dipendenti = self.controller.api_client.get_dipendenti_list()
            ids = [str(s["id"]) for s in selected]
            if AssignOrphanDialog(self, self.controller, ids, dipendenti).exec():
                self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))

    def _delete_orphans(self):
        selected = self.table_orphans.get_selected_data()
        if (
            selected
            and QMessageBox.question(self, "Conferma", f"Eliminare {len(selected)} orfani?")
            == QMessageBox.Yes
        ):
            ids = [str(s["id"]) for s in selected]
            ProgressTaskRunner(self).run(self.controller.api_client.delete_certificato, ids)
            self.refresh_data()


class ValidationDialog(QDialog):
    def __init__(self, parent, controller, cert_data):
        super().__init__(parent)
        self.controller, self.cert = controller, cert_data
        self.setWindowTitle(f"Convalida #{cert_data.get('id')}")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.edits = {
            "nome": QLineEdit(self.cert.get("nome") or ""),
            "corso": QLineEdit(self.cert.get("corso") or ""),
            "data_rilascio": QLineEdit(self.cert.get("data_rilascio") or ""),
            "data_scadenza": QLineEdit(self.cert.get("data_scadenza") or ""),
        }
        self.combo_cat = QComboBox()
        self.combo_cat.addItems(sorted(CATEGORIE_STATICHE))
        self.combo_cat.setCurrentText(self.cert.get("categoria") or "ALTRO")

        form.addRow("Dipendente:", self.edits["nome"])
        form.addRow("Corso:", self.edits["corso"])
        form.addRow("Categoria:", self.combo_cat)
        form.addRow("Rilascio:", self.edits["data_rilascio"])
        form.addRow("Scadenza:", self.edits["data_scadenza"])
        layout.addLayout(form)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.button(QDialogButtonBox.Ok).setText("CONVALIDA")
        btn_box.button(QDialogButtonBox.Ok).setProperty("class", "SuccessButton")
        btn_box.accepted.connect(self.save)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def save(self):
        data = {k: v.text() for k, v in self.edits.items()}
        data["categoria"] = self.combo_cat.currentText()
        try:
            self.controller.api_client.update_certificato(self.cert["id"], data)
            requests.put(
                f"{self.controller.api_client.base_url}/certificati/{self.cert['id']}/valida",
                headers=self.controller.api_client._get_headers(),
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))


class AssignOrphanDialog(QDialog):
    def __init__(self, parent, controller, cert_ids, dipendenti):
        super().__init__(parent)
        self.controller, self.cert_ids, self.dipendenti = controller, cert_ids, dipendenti
        self.setWindowTitle("Assegna Certificati")
        self.setFixedSize(400, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Cerca dipendente...")
        self.search.textChanged.connect(self.refresh_list)
        layout.addWidget(self.search)
        self.list = QListWidget()
        layout.addWidget(self.list)
        self.refresh_list()
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.assign)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def refresh_list(self):
        q = self.search.text().lower()
        self.list.clear()
        self.filtered = [
            d for d in self.dipendenti if q in f"{d.get('cognome', '')} {d.get('nome', '')}".lower()
        ]
        for d in self.filtered:
            self.list.addItem(f"{d.get('cognome', '')} {d.get('nome', '')}")

    def assign(self):
        idx = self.list.currentRow()
        if idx >= 0:
            dip = self.filtered[idx]
            for cid in self.cert_ids:
                with contextlib.suppress(builtins.BaseException):
                    self.controller.api_client.update_certificato(
                        cid, {"dipendente_id": dip["id"], "nome": f"{dip['cognome']} {dip['nome']}"}
                    )
            self.accept()
