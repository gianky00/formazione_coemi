from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QPushButton, QHBoxLayout, QComboBox, QLabel, QFileDialog, QMessageBox, QListView, QCheckBox
from PyQt6.QtCore import QAbstractTableModel, Qt, QItemSelection, QItemSelectionModel
import pandas as pd
import requests
from .edit_dialog import EditCertificatoDialog
from ..api_client import API_URL

class CheckboxTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.check_states = [Qt.CheckState.Unchecked] * self._data.shape[0]

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1] + 1

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            return self.check_states[index.row()].value

        if role == Qt.ItemDataRole.DisplayRole and index.column() > 0:
            return str(self._data.iloc[index.row(), index.column() - 1])

        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            self.check_states[index.row()] = Qt.CheckState(value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        flags = super().flags(index)
        if index.column() == 0:
            flags |= Qt.ItemFlag.ItemIsUserCheckable
        return flags

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if section == 0:
                return ""
            return str(self._data.columns[section - 1])
        return None

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.select_all_checkbox = QCheckBox("Seleziona Tutto")
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all)
        controls_layout.addWidget(self.select_all_checkbox)
        controls_layout.addStretch()

        self.employee_filter = QComboBox()
        self.employee_filter.setView(QListView())
        self.employee_filter.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.category_filter = QComboBox()
        self.category_filter.setView(QListView())
        self.category_filter.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.status_filter = QComboBox()
        self.status_filter.setView(QListView())
        self.status_filter.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.filter_button = QPushButton("Filtra")
        self.filter_button.clicked.connect(self.load_data)
        self.export_button = QPushButton("Esporta in CSV")
        self.export_button.clicked.connect(self.export_to_csv)
        self.edit_button = QPushButton("Modifica")
        self.edit_button.clicked.connect(self.edit_data)
        self.delete_button = QPushButton("Cancella")
        self.delete_button.clicked.connect(self.delete_data)

        # Top layout for filters
        filters_layout = QHBoxLayout()
        filters_layout.addWidget(QLabel("Dipendente:"))
        filters_layout.addWidget(self.employee_filter)
        filters_layout.addSpacing(15)
        filters_layout.addWidget(QLabel("Categoria:"))
        filters_layout.addWidget(self.category_filter)
        filters_layout.addSpacing(15)
        filters_layout.addWidget(QLabel("Stato:"))
        filters_layout.addWidget(self.status_filter)
        filters_layout.addSpacing(15)
        filters_layout.addWidget(self.filter_button)
        filters_layout.addStretch()
        self.layout.addLayout(filters_layout)

        # Bottom layout for controls
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.select_all_checkbox)
        controls_layout.addStretch()
        controls_layout.addWidget(self.export_button)
        controls_layout.addWidget(self.edit_button)
        controls_layout.addWidget(self.delete_button)
        self.layout.addLayout(controls_layout)

        # Table
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table_view.setColumnWidth(0, 40)
        self.layout.addWidget(self.table_view)
        self.load_data()

    def on_data_changed(self, top_left, bottom_right):
        if top_left.column() == 0:
            selection_model = self.table_view.selectionModel()
            for row in range(top_left.row(), bottom_right.row() + 1):
                is_checked = self.model.data(self.model.index(row, 0), Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked.value
                selection = QItemSelection(self.model.index(row, 0), self.model.index(row, self.model.columnCount() - 1))
                if is_checked:
                    selection_model.select(selection, QItemSelectionModel.SelectionFlag.Select)
                else:
                    selection_model.select(selection, QItemSelectionModel.SelectionFlag.Deselect)

    def load_data(self):
        try:
            response = requests.get(f"{API_URL}/certificati/?validated=true")
            if response.status_code == 200:
                data = response.json()
                self.df = pd.DataFrame(data)

                employees = ["Tutti"] + sorted(list(set([item['nome'] for item in data])))
                categories = ["Tutti"] + sorted(list(set([item['categoria'] for item in data])))
                stati = ["Tutti", "attivo", "scaduto", "rinnovato"]

                current_employee = self.employee_filter.currentText()
                current_category = self.category_filter.currentText()
                current_status = self.status_filter.currentText()

                self.employee_filter.clear()
                self.employee_filter.addItems(employees)
                self.category_filter.clear()
                self.category_filter.addItems(categories)
                self.status_filter.clear()
                self.status_filter.addItems(stati)

                if current_employee in employees: self.employee_filter.setCurrentText(current_employee)
                if current_category in categories: self.category_filter.setCurrentText(current_category)
                if current_status in stati: self.status_filter.setCurrentText(current_status)

                employee = self.employee_filter.currentText()
                category = self.category_filter.currentText()
                status = self.status_filter.currentText()

                if employee != "Tutti": self.df = self.df[self.df['nome'] == employee]
                if category != "Tutti": self.df = self.df[self.df['categoria'] == category]
                if status != "Tutti": self.df = self.df[self.df['stato_certificato'] == status]

                self.model = CheckboxTableModel(self.df)
                self.table_view.setModel(self.model)
                self.model.dataChanged.connect(self.on_data_changed)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore di Connessione", f"Impossibile connettersi al server: {e}")

    def toggle_select_all(self, state):
        check_state = Qt.CheckState(state)
        for i in range(self.model.rowCount()):
            self.model.setData(self.model.index(i, 0), check_state.value, Qt.ItemDataRole.CheckStateRole)

    def get_selected_ids(self):
        selected_ids = []
        for i in range(self.model.rowCount()):
            if self.model.data(self.model.index(i, 0), Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked.value:
                selected_ids.append(self.df.iloc[i]['id'])
        return selected_ids

    def edit_data(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            QMessageBox.warning(self, "Nessuna Selezione", "Seleziona una riga da modificare.")
            return
        if len(selected_ids) > 1:
            QMessageBox.warning(self, "Selezione Multipla", "La modifica è consentita solo per una riga alla volta.")
            return

        row = [i for i, cert_id in enumerate(self.df['id']) if cert_id == selected_ids[0]][0]
        current_data = self.df.iloc[row].to_dict()

        # Fetch all master categories for the dropdown
        try:
            response = requests.get(f"{API_URL}/corsi/")
            if response.status_code == 200:
                master_categories = [corso['categoria'] for corso in response.json()]
            else:
                QMessageBox.warning(self, "Errore API", "Impossibile caricare l'elenco completo delle categorie.")
                master_categories = sorted(list(set(self.df['categoria'].unique()))) # Fallback to current categories
        except requests.exceptions.RequestException:
            QMessageBox.critical(self, "Errore di Connessione", "Impossibile recuperare le categorie dal server.")
            return

        dialog = EditCertificatoDialog(current_data, master_categories, self)
        if dialog.exec():
            new_data = dialog.get_data()
            try:
                response = requests.put(f"{API_URL}/certificati/{selected_ids[0]}", json=new_data)
                if response.status_code == 200:
                    QMessageBox.information(self, "Successo", "Dati aggiornati con successo.")
                    self.load_data()
                else:
                    QMessageBox.critical(self, "Errore", f"Errore durante l'aggiornamento: {response.json().get('detail', response.text)}")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Errore di Connessione", f"Impossibile connettersi al server: {e}")

    def delete_data(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            QMessageBox.warning(self, "Nessuna Selezione", "Seleziona una o più righe da cancellare.")
            return

        reply = QMessageBox.question(self, 'Conferma Cancellazione', f'Sei sicuro di voler cancellare {len(selected_ids)} righe selezionate?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            success_count = 0
            error_count = 0
            for cert_id in selected_ids:
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
