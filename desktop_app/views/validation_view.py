
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QPushButton, QHBoxLayout, QMessageBox, QStyledItemDelegate, QLineEdit, QCheckBox, QLabel
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
    def __init__(self, data, parent=None):
        super().__init__(parent)
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
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Title
        title = QLabel("Convalida Dati")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(title)

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
        self.table_view.setAlternatingRowColors(True)
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_view.setItemDelegate(CustomDelegate())
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
        has_selection = len(self.get_selected_ids()) > 0
        self.validate_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def load_data(self):
        try:
            response = requests.get(f"{API_URL}/certificati/?validated=false")
            if response.status_code == 200:
                data = response.json()
                self.df = pd.DataFrame(data)
                self.model = CheckboxTableModel(self.df, self)
                self.table_view.setModel(self.model)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore di Connessione", f"Impossibile connettersi al server: {e}")

    def toggle_select_all(self, state):
        check_state = Qt.CheckState(state)
        for i in range(self.model.rowCount()):
            self.model.setData(self.model.index(i, 0), check_state.value, Qt.ItemDataRole.CheckStateRole)

    def delete_selected(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            return

        reply = QMessageBox.question(self, 'Conferma Cancellazione', f'Sei sicuro di voler cancellare {len(selected_ids)} righe selezionate?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.perform_action("delete", selected_ids)

    def validate_selected(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            return

        reply = QMessageBox.question(self, 'Conferma Validazione', f'Sei sicuro di voler validare {len(selected_ids)} righe selezionate?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.perform_action("validate", selected_ids)

    def get_selected_ids(self):
        selected_ids = []
        if hasattr(self, 'model'):
            for i in range(self.model.rowCount()):
                if self.model.data(self.model.index(i, 0), Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked.value:
                    selected_ids.append(self.df.iloc[i]['id'])
        return selected_ids

    def perform_action(self, action_type, ids):
        for cert_id in ids:
            try:
                if action_type == "validate":
                    requests.put(f"{API_URL}/certificati/{cert_id}/valida")
                else:
                    requests.delete(f"{API_URL}/certificati/{cert_id}")
            except requests.exceptions.RequestException:
                pass # Optionally show an error message for each failed request
        self.load_data()
