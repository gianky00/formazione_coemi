from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QPushButton, QHBoxLayout, QComboBox, QLabel
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

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.layout.addLayout(controls_layout)

        self.employee_filter = QComboBox()
        self.course_filter = QComboBox()
        self.load_filters_button = QPushButton("Carica Filtri")
        self.load_filters_button.clicked.connect(self.load_filters)
        self.filter_button = QPushButton("Filtra")
        self.filter_button.clicked.connect(self.load_data)
        self.export_button = QPushButton("Esporta in CSV")
        self.export_button.clicked.connect(self.export_to_csv)

        controls_layout.addWidget(QLabel("Dipendente:"))
        controls_layout.addWidget(self.employee_filter)
        controls_layout.addWidget(QLabel("Corso:"))
        controls_layout.addWidget(self.course_filter)
        controls_layout.addWidget(self.load_filters_button)
        controls_layout.addWidget(self.filter_button)
        controls_layout.addWidget(self.export_button)

        # Table
        self.table_view = QTableView()
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table_view)

    def load_filters(self):
        # In a real app, you would populate these from the database
        self.employee_filter.addItems(["Tutti", "Mario Rossi", "John Doe"])
        self.course_filter.addItems(["Tutti", "L4 GRU SU AUTOCARRO", "ANTINCENDIO"])

    def load_data(self):
        # Placeholder for API call
        data = {'Nome': ['Mario Rossi', 'John Doe'],
                'Corso': ['L4 GRU SU AUTOCARRO', 'ANTINCENDIO'],
                'Data Rilascio': ['2024-01-01', '2023-05-10'],
                'Data Scadenza': ['2029-01-01', '2026-05-10']}
        self.df = pd.DataFrame(data)
        self.model = PandasModel(self.df)
        self.table_view.setModel(self.model)


    def export_to_csv(self):
        if hasattr(self, 'df'):
            path, _ = QFileDialog.getSaveFileName(self, "Salva CSV", "report.csv", "CSV Files (*.csv)")
            if path:
                self.df.to_csv(path, index=False)
