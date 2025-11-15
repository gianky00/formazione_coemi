
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
            self.parent().update_button_states()
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
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Title
        title = QLabel("Database Certificati")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(title)

        # Control Bar
        control_bar_layout = QHBoxLayout()

        # Filters
        control_bar_layout.addWidget(QLabel("Dipendente:"))
        self.employee_filter = QComboBox()
        control_bar_layout.addWidget(self.employee_filter)

        control_bar_layout.addSpacing(15)

        control_bar_layout.addWidget(QLabel("Categoria:"))
        self.category_filter = QComboBox()
        control_bar_layout.addWidget(self.category_filter)

        control_bar_layout.addSpacing(15)

        control_bar_layout.addWidget(QLabel("Stato:"))
        self.status_filter = QComboBox()
        control_bar_layout.addWidget(self.status_filter)

        self.filter_button = QPushButton("Filtra")
        self.filter_button.clicked.connect(self.load_data)
        control_bar_layout.addWidget(self.filter_button)

        control_bar_layout.addStretch()

        # Action Buttons
        self.export_button = QPushButton("Esporta in CSV")
        self.export_button.clicked.connect(self.export_to_csv)
        control_bar_layout.addWidget(self.export_button)

        self.edit_button = QPushButton("Modifica")
        self.edit_button.clicked.connect(self.edit_data)
        control_bar_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Cancella")
        self.delete_button.clicked.connect(self.delete_data)
        control_bar_layout.addWidget(self.delete_button)

        self.layout.addLayout(control_bar_layout)

        # Table
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setMouseTracking(True)
        self.table_view.entered.connect(self.table_view.viewport().update)

        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_view.clicked.connect(self.on_row_clicked)

        self.layout.addWidget(self.table_view)

        self.load_data()
        self.update_button_states()

    def on_row_clicked(self, index):
        if hasattr(self, 'model'):
            check_index = self.model.index(index.row(), 0)
            check_state = self.model.data(check_index, Qt.ItemDataRole.CheckStateRole)
            new_state = Qt.CheckState.Unchecked if check_state == Qt.CheckState.Checked.value else Qt.CheckState.Checked
            self.model.setData(check_index, new_state.value, Qt.ItemDataRole.CheckStateRole)

    def update_button_states(self):
        selected_ids = self.get_selected_ids()
        self.edit_button.setEnabled(len(selected_ids) == 1)
        self.delete_button.setEnabled(len(selected_ids) > 0)

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
                self.model.setParent(self)
                self.table_view.setModel(self.model)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore di Connessione", f"Impossibile connettersi al server: {e}")

    def get_selected_ids(self):
        selected_ids = []
        if hasattr(self, 'model'):
            for i in range(self.model.rowCount()):
                if self.model.data(self.model.index(i, 0), Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked.value:
                    selected_ids.append(self.df.iloc[i]['id'])
        return selected_ids

    def edit_data(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            return

        row = [i for i, cert_id in enumerate(self.df['id']) if cert_id == selected_ids[0]][0]
        current_data = self.df.iloc[row].to_dict()

        try:
            response = requests.get(f"{API_URL}/corsi/")
            if response.status_code == 200:
                master_categories = [corso['categoria_corso'] for corso in response.json()]
            else:
                master_categories = sorted(list(set(self.df['categoria'].unique())))
        except requests.exceptions.RequestException:
            master_categories = sorted(list(set(self.df['categoria'].unique())))

        dialog = EditCertificatoDialog(current_data, master_categories, self)
        if dialog.exec():
            new_data = dialog.get_data()
            try:
                response = requests.put(f"{API_URL}/certificati/{selected_ids[0]}", json=new_data)
                if response.status_code == 200:
                    self.load_data()
                else:
                    QMessageBox.critical(self, "Errore", f"Errore durante l'aggiornamento: {response.text}")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Errore di Connessione", f"Impossibile connettersi al server: {e}")

    def delete_data(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            return

        reply = QMessageBox.question(self, 'Conferma Cancellazione', f'Sei sicuro di voler cancellare {len(selected_ids)} righe selezionate?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            for cert_id in selected_ids:
                try:
                    requests.delete(f"{API_URL}/certificati/{cert_id}")
                except requests.exceptions.RequestException:
                    pass
            self.load_data()

    def export_to_csv(self):
        if hasattr(self, 'df'):
            path, _ = QFileDialog.getSaveFileName(self, "Salva CSV", "report.csv", "CSV Files (*.csv)")
            if path:
                self.df.to_csv(path, index=False)
