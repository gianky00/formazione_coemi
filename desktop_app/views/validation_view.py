
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QPushButton, QHBoxLayout, QMessageBox, QStyledItemDelegate, QLineEdit
from PyQt6.QtCore import QAbstractTableModel, Qt
import pandas as pd
import requests
from ..api_client import API_URL

class CustomDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        return editor

    def setEditorData(self, editor, index):
        super().setEditorData(editor, index)
        if isinstance(editor, QLineEdit):
            editor.selectAll()

class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not self._data.empty and index.isValid() and role == Qt.ItemDataRole.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not self._data.empty and role == Qt.ItemDataRole.EditRole:
            self._data.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        flags = super().flags(index)
        if not self._data.empty and index.column() != 0:  # Allow editing for all columns except the first one (ID)
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if not self._data.empty and role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return str(self._data.columns[section])
        return None

class ValidationView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.layout.addLayout(controls_layout)

        self.validate_button = QPushButton("Convalida Selezionato")
        self.validate_button.clicked.connect(self.validate_selected)
        controls_layout.addWidget(self.validate_button)

        self.validate_all_button = QPushButton("Convalida Tutto")
        self.validate_all_button.clicked.connect(self.validate_all)
        controls_layout.addWidget(self.validate_all_button)

        self.delete_button = QPushButton("Cancella Selezionato")
        self.delete_button.clicked.connect(self.delete_selected)
        controls_layout.addWidget(self.delete_button)

        # Table
        self.table_view = QTableView()
        self.table_view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_view.setItemDelegate(CustomDelegate())
        self.layout.addWidget(self.table_view)

        self.load_data()

    def load_data(self):
        try:
            response = requests.get(f"{API_URL}/certificati/?validated=false")
            if response.status_code == 200:
                data = response.json()
                self.df = pd.DataFrame(data)
                self.model = PandasModel(self.df)
                self.table_view.setModel(self.model)
                self.table_view.resizeColumnsToContents()
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore di Connessione", f"Impossibile connettersi al server: {e}")

    def validate_all(self):
        if not hasattr(self, 'df') or self.df.empty:
            QMessageBox.information(self, "Nessuna Azione", "Non ci sono certificati da validare.")
            return

        reply = QMessageBox.question(self, 'Conferma Validazione Multipla',
                                     f"Sei sicuro di voler validare tutti i {len(self.df)} certificati visualizzati?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.No:
            return

        error_count = 0
        success_count = 0

        certificato_ids = self.df['id'].tolist()

        for cert_id in certificato_ids:
            try:
                response = requests.put(f"{API_URL}/certificati/{cert_id}/valida")
                if response.status_code == 200:
                    success_count += 1
                else:
                    error_count += 1
            except requests.exceptions.RequestException:
                error_count += 1

        summary_message = f"Validazione completata.\n\n" \
                          f"Certificati validati con successo: {success_count}\n" \
                          f"Errori riscontrati: {error_count}"

        QMessageBox.information(self, "Risultato Validazione", summary_message)
        self.load_data()

    def delete_selected(self):
        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Nessuna Selezione", "Seleziona una o più righe da cancellare.")
            return

        reply = QMessageBox.question(self, 'Conferma Cancellazione', f'Sei sicuro di voler cancellare {len(selected_rows)} righe selezionate?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            ids_to_delete = [self.df.iloc[index.row()]['id'] for index in selected_rows]
            success_count = 0
            error_count = 0
            for cert_id in ids_to_delete:
                try:
                    response = requests.delete(f"{API_URL}/certificati/{cert_id}")
                    if response.status_code == 200:
                        success_count += 1
                    else:
                        error_count += 1
                except requests.exceptions.RequestException:
                    error_count += 1

            QMessageBox.information(self, "Risultato Cancellazione", f"{success_count} righe cancellate con successo, {error_count} errori.")
            self.load_data()

    def validate_selected(self):
        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Nessuna Selezione", "Seleziona una o più righe da validare.")
            return

        reply = QMessageBox.question(self, 'Conferma Validazione', f'Sei sicuro di voler validare {len(selected_rows)} righe selezionate?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            ids_to_validate = [self.df.iloc[index.row()]['id'] for index in selected_rows]
            success_count = 0
            error_count = 0
            for cert_id in ids_to_validate:
                try:
                    response = requests.put(f"{API_URL}/certificati/{cert_id}/valida")
                    if response.status_code == 200:
                        success_count += 1
                    else:
                        error_count += 1
                except requests.exceptions.RequestException:
                    error_count += 1

            QMessageBox.information(self, "Risultato Validazione", f"{success_count} righe validate con successo, {error_count} errori.")
            self.load_data()
