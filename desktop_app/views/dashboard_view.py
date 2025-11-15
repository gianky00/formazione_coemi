from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QPushButton, QHBoxLayout, QComboBox, QLabel, QFileDialog, QMessageBox, QLineEdit
from PyQt6.QtCore import QAbstractTableModel, Qt
import pandas as pd
import requests
from .edit_dialog import EditCertificatoDialog

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

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if not self._data.empty and role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
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
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tutti", "attivo", "scaduto"])
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Cerca...")
        self.filter_button = QPushButton("Filtra")
        self.filter_button.clicked.connect(self.apply_filters)
        self.employee_filter.currentTextChanged.connect(self.apply_filters)
        self.course_filter.currentTextChanged.connect(self.apply_filters)
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        self.search_bar.textChanged.connect(self.apply_filters)
        self.export_button = QPushButton("Esporta in CSV")
        self.export_button.clicked.connect(self.export_to_csv)

        controls_layout.addWidget(QLabel("Dipendente:"))
        controls_layout.addWidget(self.employee_filter)
        controls_layout.addWidget(QLabel("Corso:"))
        controls_layout.addWidget(self.course_filter)
        controls_layout.addWidget(QLabel("Stato:"))
        controls_layout.addWidget(self.status_filter)
        controls_layout.addWidget(self.search_bar)
        controls_layout.addWidget(self.filter_button)
        controls_layout.addWidget(self.export_button)

        self.edit_button = QPushButton("Modifica")
        self.edit_button.clicked.connect(self.edit_data)
        self.delete_button = QPushButton("Cancella")
        self.delete_button.clicked.connect(self.delete_data)
        controls_layout.addWidget(self.edit_button)
        controls_layout.addWidget(self.delete_button)

        # Table
        self.table_view = QTableView()
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.layout.addWidget(self.table_view)
        self.load_data()

    def load_data(self):
        try:
            response = requests.get("http://127.0.0.1:8000/certificati/?validated=true")
            if response.status_code == 200:
                data = response.json()
                self.full_df = pd.DataFrame(data)  # Store the full dataset

                # Populate filters if they are empty
                if self.employee_filter.count() == 0:
                    employees = ["Tutti"] + sorted(list(set([item['dipendente'] for item in data])))
                    self.employee_filter.addItems(employees)
                if self.course_filter.count() == 0:
                    courses = ["Tutti"] + sorted(list(set([item['corso'] for item in data])))
                    self.course_filter.addItems(courses)

                self.apply_filters() # Apply filters to the full dataset
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore di Connessione", f"Impossibile connettersi al server: {e}")

    def apply_filters(self):
        filtered_df = self.full_df.copy()

        # Apply dropdown filters
        employee = self.employee_filter.currentText()
        if employee != "Tutti":
            filtered_df = filtered_df[filtered_df['dipendente'] == employee]

        course = self.course_filter.currentText()
        if course != "Tutti":
            filtered_df = filtered_df[filtered_df['corso'] == course]

        status = self.status_filter.currentText()
        if status != "Tutti":
            filtered_df = filtered_df[filtered_df['stato_certificato'] == status]

        # Apply search bar filter (case-insensitive)
        search_text = self.search_bar.text().lower()
        if search_text:
            filtered_df = filtered_df[filtered_df.apply(
                lambda row: any(search_text in str(cell).lower() for cell in row),
                axis=1
            )]

        self.df = filtered_df
        self.model = PandasModel(self.df)
        self.table_view.setModel(self.model)
        self.table_view.resizeColumnsToContents()

    def edit_data(self):
        selected_indexes = self.table_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "Nessuna Selezione", "Seleziona una riga da modificare.")
            return

        row = selected_indexes[0].row()
        certificato_id = self.df.iloc[row]['id']
        current_data = self.df.iloc[row].to_dict()

        dialog = EditCertificatoDialog(current_data, self)
        if dialog.exec():
            new_data = dialog.get_data()
            try:
                response = requests.put(
                    f"http://127.0.0.1:8000/certificati/{certificato_id}",
                    json=new_data
                )
                if response.status_code == 200:
                    QMessageBox.information(self, "Successo", "Dati aggiornati con successo.")
                    self.load_data()
                else:
                    QMessageBox.critical(self, "Errore", f"Errore durante l'aggiornamento: {response.json().get('detail', response.text)}")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Errore di Connessione", f"Impossibile connettersi al server: {e}")

    def delete_data(self):
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

    def export_to_csv(self):
        if hasattr(self, 'df'):
            path, _ = QFileDialog.getSaveFileName(self, "Salva CSV", "report.csv", "CSV Files (*.csv)")
            if path:
                self.df.to_csv(path, index=False)
