from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QPushButton, QHBoxLayout, QComboBox, QLabel, QFileDialog, QMessageBox
from PyQt6.QtCore import QAbstractTableModel, Qt
import pandas as pd
import requests
from .edit_dialog import EditCertificatoDialog
from ..api_client import API_URL

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
        self.category_filter = QComboBox()
        self.status_filter = QComboBox()
        self.filter_button = QPushButton("Filtra")
        self.filter_button.clicked.connect(self.load_data)
        self.export_button = QPushButton("Esporta in CSV")
        self.export_button.clicked.connect(self.export_to_csv)

        filter_group = QHBoxLayout()
        filter_group.addWidget(QLabel("Dipendente:"))
        filter_group.addWidget(self.employee_filter)
        filter_group.addWidget(QLabel("Categoria:"))
        filter_group.addWidget(self.category_filter)
        filter_group.addWidget(QLabel("Stato:"))
        filter_group.addWidget(self.status_filter)
        filter_group.addStretch()
        controls_layout.addLayout(filter_group)

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
        self.table_view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table_view)
        self.load_data()

    def load_data(self):
        try:
            response = requests.get(f"{API_URL}/certificati/?validated=true")
            if response.status_code == 200:
                data = response.json()
                self.df = pd.DataFrame(data)

                # Populate filters
                employees = ["Tutti"] + sorted(list(set([item['nome'] for item in data])))
                categories = ["Tutti"] + sorted(list(set([item['categoria'] for item in data])))
                stati = ["Tutti", "attivo", "scaduto", "rinnovato"]

                # Save current filter selection
                current_employee = self.employee_filter.currentText()
                current_category = self.category_filter.currentText()
                current_status = self.status_filter.currentText()

                self.employee_filter.clear()
                self.employee_filter.addItems(employees)
                self.category_filter.clear()
                self.category_filter.addItems(categories)
                self.status_filter.clear()
                self.status_filter.addItems(stati)

                # Restore filter selection
                if current_employee in employees:
                    self.employee_filter.setCurrentText(current_employee)
                if current_category in categories:
                    self.category_filter.setCurrentText(current_category)
                if current_status in stati:
                    self.status_filter.setCurrentText(current_status)

                employee = self.employee_filter.currentText()
                category = self.category_filter.currentText()
                status = self.status_filter.currentText()

                if employee != "Tutti":
                    self.df = self.df[self.df['nome'] == employee]
                if category != "Tutti":
                    self.df = self.df[self.df['categoria'] == category]
                if status != "Tutti":
                    self.df = self.df[self.df['stato_certificato'] == status]

                self.model = PandasModel(self.df)
                self.table_view.setModel(self.model)
                self.table_view.resizeColumnsToContents()
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore di Connessione", f"Impossibile connettersi al server: {e}")

    def edit_data(self):
        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Nessuna Selezione", "Seleziona una riga da modificare.")
            return
        if len(selected_rows) > 1:
            QMessageBox.warning(self, "Selezione Multipla", "La modifica è consentita solo per una riga alla volta.")
            return

        row = selected_rows[0].row()
        certificato_id = self.df.iloc[row]['id']
        current_data = self.df.iloc[row].to_dict()

        dialog = EditCertificatoDialog(current_data, self)
        if dialog.exec():
            new_data = dialog.get_data()
            try:
                response = requests.put(
                    f"{API_URL}/certificati/{certificato_id}",
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

    def export_to_csv(self):
        if hasattr(self, 'df'):
            path, _ = QFileDialog.getSaveFileName(self, "Salva CSV", "report.csv", "CSV Files (*.csv)")
            if path:
                self.df.to_csv(path, index=False)
