import os
import threading

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QColor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QLabel,
    QMenu,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from app.core.config import settings
from app.services.document_locator import find_document
from desktop_app.utils import ProgressTaskRunner, open_file
from desktop_app.views.edit_certificato_dialog import EditCertificatoDialog
from desktop_app.widgets.data_table import DataTable
from desktop_app.widgets.search_bar import SearchBar


class DatabaseView(QWidget):
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

        # 1. Search Bar
        self.search_bar = SearchBar("Filtra per nome, corso...", self)
        self.search_bar.add_filter("Categoria", "categoria", ["Tutte"])
        self.search_bar.add_filter("Stato", "stato", ["Tutti", "Attivo", "In Scadenza", "Scaduto"])
        self.search_bar.add_refresh_button()

        self.search_bar.text_changed.connect(self.filter_data)
        self.search_bar.filter_changed.connect(lambda k, v: self.filter_data())
        self.search_bar.refresh_requested.connect(self.refresh_data)

        layout.addWidget(self.search_bar)

        # 2. Table
        self.table = DataTable(self)
        self.table.set_columns(
            ["ID", "Dipendente", "Documento", "Categoria", "Rilascio", "Scadenza", "Stato"]
        )
        self.table.row_double_clicked.connect(self.open_file)
        self.table.context_menu_requested.connect(self.show_context_menu)

        layout.addWidget(self.table)

        # Footer count
        self.lbl_count = QLabel("")
        layout.addWidget(self.lbl_count)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("F5"), self, self.refresh_data)
        QShortcut(QKeySequence("Del"), self, self.delete_item)
        QShortcut(QKeySequence("F2"), self, self.edit_item)

    def show_context_menu(self, pos, cert):
        menu = QMenu(self)
        menu.addAction("Apri File PDF", lambda: self.open_file(cert))
        menu.addAction("Apri Cartella", lambda: self.open_folder(cert))
        menu.addSeparator()
        menu.addAction("Modifica Dati", lambda: self.edit_item(cert))
        menu.addAction("Elimina", lambda: self.delete_item(cert))
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def refresh_data(self):
        def fetch():
            try:
                new_data = self.controller.api_client.get(
                    "certificati", params={"validated": "true"}
                )
                self.data_signal.emit(new_data)
            except Exception:
                pass

        threading.Thread(target=fetch, daemon=True).start()

    @Slot(list)
    def _update_data(self, new_data):
        self.data = new_data

        # Update categories in search bar
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

    def filter_data(self):
        query = self.search_bar.entry_search.text().lower()
        cat_filter = self.search_bar.combos["categoria"].currentText()
        status_filter = self.search_bar.combos["stato"].currentText().lower()

        filtered = []
        for item in self.data:
            stato = str(item.get("stato_certificato") or "").lower()
            if (
                cat_filter != "Tutte"
                and str(item.get("categoria") or "").upper() != cat_filter.upper()
            ):
                continue
            if status_filter != "tutti":
                if status_filter == "in scadenza" and stato != "in_scadenza":
                    continue
                if status_filter == "scaduto" and stato != "scaduto":
                    continue
                if status_filter == "attivo" and stato != "attivo":
                    continue

            txt = f"{item.get('nome', '')} {item.get('corso', '')}".lower()
            if query and query not in txt:
                continue
            filtered.append(item)

        # Load into table
        mapping = [
            "id",
            "nome",
            "corso",
            "categoria",
            "data_rilascio",
            "data_scadenza",
            "stato_certificato",
        ]
        self.table.load_data(filtered, mapping, color_callback=self._get_row_color)
        self.lbl_count.setText(f"{len(filtered)} certificati")

    def _get_row_color(self, item):
        stato = str(item.get("stato_certificato") or "").lower()
        if stato == "scaduto":
            return QColor("#FECACA")
        if stato == "in_scadenza":
            return QColor("#FED7AA")
        if stato == "attivo":
            return QColor("#BBF7D0")
        return None

    def open_file(self, cert):
        if not settings.DOCUMENTS_FOLDER:
            return
        path = find_document(settings.DOCUMENTS_FOLDER, cert)
        if path and os.path.exists(path):
            open_file(path)
        else:
            QMessageBox.warning(self, "Attenzione", "File non trovato.")

    def open_folder(self, cert):
        if not settings.DOCUMENTS_FOLDER:
            return
        path = find_document(settings.DOCUMENTS_FOLDER, cert)
        open_file(
            os.path.dirname(path) if path and os.path.exists(path) else settings.DOCUMENTS_FOLDER
        )

    def edit_item(self, cert=None):
        if not cert:
            selected = self.table.get_selected_data()
            if not selected:
                return
            cert = selected[0]

        if EditCertificatoDialog(self, self.controller, cert).exec():
            self.refresh_data()

    def delete_item(self, cert=None):
        selected = [cert] if cert else self.table.get_selected_data()
        if not selected:
            return

        if (
            QMessageBox.question(self, "Conferma", f"Eliminare {len(selected)} certificati?")
            == QMessageBox.Yes
        ):
            ids = [str(s["id"]) for s in selected]
            ProgressTaskRunner(self).run(self.controller.api_client.delete_certificato, ids)
            self.refresh_data()
