import builtins
import contextlib
import threading

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from desktop_app.utils import format_date_to_ui
from desktop_app.widgets.data_table import DataTable
from desktop_app.widgets.search_bar import SearchBar


class DipendentiView(QWidget):
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
        self.search_bar = SearchBar("Cerca dipendenti...", self)
        self.search_bar.add_refresh_button()

        btn_new = QPushButton("Nuovo")
        btn_new.setProperty("class", "SuccessButton")
        btn_new.clicked.connect(self.add_dipendente)
        self.search_bar.layout.addWidget(btn_new)

        btn_bulk = QPushButton("Assegna Mansione")
        btn_bulk.setProperty("class", "PrimaryButton")
        btn_bulk.clicked.connect(self._bulk_assign_mansione)
        self.search_bar.layout.addWidget(btn_bulk)

        self.search_bar.text_changed.connect(self.filter_data)
        self.search_bar.refresh_requested.connect(self.refresh_data)
        layout.addWidget(self.search_bar)

        # Table
        self.table = DataTable(self)
        self.table.set_columns(
            ["ID", "Matricola", "Cognome e Nome", "Data Nascita", "Mansione", "Reparto"]
        )
        self.table.row_double_clicked.connect(self.on_double_click)
        self.table.context_menu_requested.connect(self.show_context_menu)
        self.table.itemSelectionChanged.connect(self._on_selection_change)
        layout.addWidget(self.table)

        self.lbl_selection = QLabel("")
        layout.addWidget(self.lbl_selection)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("F5"), self, self.refresh_data)

    def show_context_menu(self, pos, dip):
        menu = QMenu(self)
        menu.addAction("Visualizza Storico", lambda: self.show_storico(dip))
        menu.addSeparator()
        menu.addAction("Modifica", lambda: self.on_double_click(dip))
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _on_selection_change(self):
        count = len(self.table.get_selected_data())
        self.lbl_selection.setText(f"{count} selezionati" if count > 1 else "")

    def refresh_data(self):
        def fetch():
            try:
                new_data = self.controller.api_client.get_dipendenti_list()
                self.data_signal.emit(new_data)
            except Exception:
                pass

        threading.Thread(target=fetch, daemon=True).start()

    @Slot(list)
    def _update_data(self, new_data):
        self.data = new_data
        self.filter_data()

    def filter_data(self):
        query = self.search_bar.entry_search.text().lower()
        filtered = []
        for d in self.data:
            display_name = f"{d.get('cognome', '')} {d.get('nome', '')}".strip().upper()
            txt = (
                f"{display_name} {d.get('matricola', '')} {d.get('categoria_reparto', '')}".lower()
            )
            if query and query not in txt:
                continue

            d["display_name"] = display_name
            d["formatted_nascita"] = format_date_to_ui(d.get("data_nascita"))
            filtered.append(d)

        mapping = [
            "id",
            "matricola",
            "display_name",
            "formatted_nascita",
            "mansione",
            "categoria_reparto",
        ]
        self.table.load_data(filtered, mapping)

    def add_dipendente(self):
        if DipendenteDialog(self, self.controller).exec():
            self.refresh_data()

    def on_double_click(self, dip):
        if dip and DipendenteDialog(self, self.controller, dip).exec():
            self.refresh_data()

    def show_storico(self, dip):
        if dip:
            StoricoCertificatiDialog(self, self.controller, dip).exec()

    def _bulk_assign_mansione(self):
        selected = self.table.get_selected_data()
        if selected:
            ids = [str(s["id"]) for s in selected]
            if BulkAssignDialog(self, self.controller, ids, self.data).exec():
                self.refresh_data()


class DipendenteDialog(QDialog):
    def __init__(self, parent, controller, dip_data=None):
        super().__init__(parent)
        self.controller, self.dip_data = controller, dip_data
        self.setWindowTitle("Scheda Dipendente")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        fields = ["cognome", "nome", "matricola", "data_nascita", "mansione", "categoria_reparto"]
        self.edits = {
            k: QLineEdit(str(self.dip_data.get(k) or "")) if self.dip_data else QLineEdit()
            for k in fields
        }
        for k, v in self.edits.items():
            form.addRow(f"{k.replace('_', ' ').title()}:", v)
        layout.addLayout(form)
        btn_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.save)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def save(self):
        data = {k: v.text() for k, v in self.edits.items()}
        try:
            if self.dip_data:
                self.controller.api_client.update_dipendente(self.dip_data["id"], data)
            else:
                self.controller.api_client.create_dipendente(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))


class BulkAssignDialog(QDialog):
    def __init__(self, parent, controller, dip_ids, all_data):
        super().__init__(parent)
        self.controller, self.dip_ids = controller, dip_ids
        self.setWindowTitle("Assegnazione Massiva")
        layout = QVBoxLayout(self)
        self.combo = QComboBox()
        self.combo.setEditable(True)
        self.combo.addItems(sorted({d.get("mansione") for d in all_data if d.get("mansione")}))
        layout.addWidget(QLabel("Nuova Mansione:"))
        layout.addWidget(self.combo)
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.apply)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def apply(self):
        val = self.combo.currentText()
        for did in self.dip_ids:
            with contextlib.suppress(builtins.BaseException):
                self.controller.api_client.update_dipendente(did, {"mansione": val})
        self.accept()


class StoricoCertificatiDialog(QDialog):
    def __init__(self, parent, controller, dip):
        super().__init__(parent)
        self.controller, self.dip = controller, dip
        self.setWindowTitle(f"Storico: {dip.get('display_name')}")
        self.resize(800, 400)
        layout = QVBoxLayout(self)
        self.table = DataTable(self)
        self.table.set_columns(["Documento", "Categoria", "Emissione", "Scadenza", "Stato"])
        layout.addWidget(self.table)
        self.load_data()

    def load_data(self):
        try:
            res = self.controller.api_client.get_dipendente_detail(self.dip["id"])
            certs = res.get("certificati", [])
            mapping = ["corso", "categoria", "data_rilascio", "data_scadenza", "stato_certificato"]
            self.table.load_data(certs, mapping)
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))
