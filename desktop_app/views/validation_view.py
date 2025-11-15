
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QPushButton, QHBoxLayout, QMessageBox, QStyledItemDelegate, QLineEdit, QCheckBox
from PyQt6.QtCore import QAbstractTableModel, Qt, QItemSelection, QItemSelectionModel
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

        if role == Qt.ItemDataRole.EditRole and index.column() > 0:
            self._data.iloc[index.row(), index.column() - 1] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        flags = super().flags(index)
        if index.column() == 0:
            flags |= Qt.ItemFlag.ItemIsUserCheckable
        else:
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if section == 0:
                return ""
            return str(self._data.columns[section - 1])
        return None

class ValidationView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.select_all_checkbox = QCheckBox("Seleziona Tutto")
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all)
        controls_layout.addWidget(self.select_all_checkbox)
        controls_layout.addStretch()

        self.validate_button = QPushButton("Convalida")
        self.validate_button.clicked.connect(self.validate_selected)
        controls_layout.addWidget(self.validate_button)

        self.delete_button = QPushButton("Cancella")
        self.delete_button.clicked.connect(self.delete_selected)
        controls_layout.addWidget(self.delete_button)
        self.layout.addLayout(controls_layout)

        # Table
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table_view.setColumnWidth(0, 40)
        self.table_view.setItemDelegate(CustomDelegate())
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
            response = requests.get(f"{API_URL}/certificati/?validated=false")
            if response.status_code == 200:
                data = response.json()
                self.df = pd.DataFrame(data)
                self.model = CheckboxTableModel(self.df)
                self.table_view.setModel(self.model)
                self.model.dataChanged.connect(self.on_data_changed)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore di Connessione", f"Impossibile connettersi al server: {e}")

    def toggle_select_all(self, state):
        check_state = Qt.CheckState(state)
        for i in range(self.model.rowCount()):
            self.model.setData(self.model.index(i, 0), check_state.value, Qt.ItemDataRole.CheckStateRole)

    def delete_selected(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            QMessageBox.warning(self, "Nessuna Selezione", "Seleziona una o più righe da cancellare.")
            return

        reply = QMessageBox.question(self, 'Conferma Cancellazione', f'Sei sicuro di voler cancellare {len(selected_ids)} righe selezionate?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.perform_action("delete", selected_ids)

    def validate_selected(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            QMessageBox.warning(self, "Nessuna Selezione", "Seleziona una o più righe da validare.")
            return

        reply = QMessageBox.question(self, 'Conferma Validazione', f'Sei sicuro di voler validare {len(selected_ids)} righe selezionate?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.perform_action("validate", selected_ids)

    def get_selected_ids(self):
        selected_ids = []
        for i in range(self.model.rowCount()):
            if self.model.data(self.model.index(i, 0), Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked.value:
                selected_ids.append(self.df.iloc[i]['id'])
        return selected_ids

    def perform_action(self, action_type, ids):
        success_count = 0
        error_count = 0
        for cert_id in ids:
            try:
                if action_type == "validate":
                    response = requests.put(f"{API_URL}/certificati/{cert_id}/valida")
                else:
                    response = requests.delete(f"{API_URL}/certificati/{cert_id}")

                if response.status_code == 200:
                    success_count += 1
                else:
                    error_count += 1
            except requests.exceptions.RequestException:
                error_count += 1

        action_str = "validate" if action_type == "validate" else "cancellate"
        QMessageBox.information(self, f"Risultato {action_type.capitalize()}", f"{success_count} righe {action_str} con successo, {error_count} errori.")
        self.load_data()
