
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QPushButton, QHBoxLayout, QMessageBox, QStyledItemDelegate, QLineEdit
from PyQt6.QtCore import QAbstractTableModel, Qt
import pandas as pd
import requests

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
        if index.isValid() and role == Qt.ItemDataRole.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            self._data.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        flags = super().flags(index)
        if index.column() != 0:  # Allow editing for all columns except the first one (ID)
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return str(self._data.columns[section])
        return None

class ValidationView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.layout.addLayout(controls_layout)

        self.save_button = QPushButton("Salva Modifiche")
        self.save_button.clicked.connect(self.save_changes)
        controls_layout.addWidget(self.save_button)

        self.delete_button = QPushButton("Cancella Riga")
        self.delete_button.clicked.connect(self.delete_row)
        controls_layout.addWidget(self.delete_button)

        # Table
        self.table_view = QTableView()
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_view.setItemDelegate(CustomDelegate())
        self.layout.addWidget(self.table_view)

        self.load_data()

    def load_data(self):
        try:
            response = requests.get("http://127.0.0.1:8000/certificati/?validated=false")
            if response.status_code == 200:
                data = response.json()
                self.df = pd.DataFrame(data)
                self.model = PandasModel(self.df)
                self.table_view.setModel(self.model)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore di Connessione", f"Impossibile connettersi al server: {e}")

    def delete_row(self):
        selected_indexes = self.table_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "Nessuna Selezione", "Seleziona una riga da cancellare.")
            return

        row = selected_indexes[0].row()
        certificato_id = self.df.iloc[row]['id']

        reply = QMessageBox.question(self, 'Conferma Cancellazione', 'Sei sicuro di voler cancellare questa riga?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                response = requests.delete(f"http://127.0.0.1:8000/certificati/{certificato_id}")
                if response.status_code == 200:
                    QMessageBox.information(self, "Successo", "Riga cancellata con successo.")
                    self.load_data()
                else:
                    QMessageBox.critical(self, "Errore", f"Errore durante la cancellazione: {response.text}")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Errore di Connessione", f"Impossibile connettersi al server: {e}")

    def save_changes(self):
        try:
            for row in range(self.model.rowCount()):
                certificato_id = self.df.iloc[row]['id']
                nome = self.model.data(self.model.index(row, 1))
                corso = self.model.data(self.model.index(row, 2))
                data_rilascio = self.model.data(self.model.index(row, 3))
                data_scadenza = self.model.data(self.model.index(row, 4))

                # Create the payload with all fields, ensuring none are missing
                payload = {
                    "nome": nome,
                    "corso": corso,
                    "data_rilascio": data_rilascio,
                    "data_scadenza": data_scadenza
                }

                response = requests.put(f"http://127.0.0.1:8000/certificati/{certificato_id}", params=payload)

                if response.status_code != 200:
                    QMessageBox.critical(self, "Errore", f"Errore durante l'aggiornamento della riga {row}: {response.text}")
                    return

            QMessageBox.information(self, "Successo", "Modifiche salvate con successo.")
            self.load_data()

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore di Connessione", f"Impossibile connettersi al server: {e}")
