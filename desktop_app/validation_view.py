
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtCore import QAbstractTableModel, Qt
import pandas as pd
import requests

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

        self.validate_button = QPushButton("Convalida")
        self.validate_button.clicked.connect(self.validate_data)
        controls_layout.addWidget(self.validate_button)

        # Table
        self.table_view = QTableView()
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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

    def validate_data(self):
        selected_indexes = self.table_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "Nessuna Selezione", "Seleziona una riga da validare.")
            return

        row = selected_indexes[0].row()
        certificato_id = self.df.iloc[row]['id']

        reply = QMessageBox.question(self, 'Conferma Validazione', 'Sei sicuro di voler validare questa riga?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                response = requests.put(f"http://127.0.0.1:8000/certificati/{certificato_id}/valida")
                if response.status_code == 200:
                    QMessageBox.information(self, "Successo", "Riga validata con successo.")
                    self.load_data()
                else:
                    QMessageBox.critical(self, "Errore", f"Errore durante la validazione: {response.text}")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Errore di Connessione", f"Impossibile connettersi al server: {e}")
