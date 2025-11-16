
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QPushButton, QHBoxLayout, QMessageBox, QStyledItemDelegate, QLineEdit, QLabel
from PyQt6.QtCore import QAbstractTableModel, Qt, pyqtSignal
import pandas as pd
import requests
from ..api_client import API_URL

class CustomDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            editor.selectAll()
        return editor

    def setEditorData(self, editor, index):
        super().setEditorData(editor, index)

class SimpleTableModel(QAbstractTableModel):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole and index.isValid():
            try:
                # Update DataFrame
                self._data.iloc[index.row(), index.column()] = value

                # Get certificate ID and column name
                cert_id = self._data.iloc[index.row()]['id']
                column_name = self._data.columns[index.column()]

                # Prepare payload for API
                payload = {column_name: value}

                # API call to update data
                response = requests.put(f"{API_URL}/certificati/{cert_id}", json=payload)
                response.raise_for_status()

                self.dataChanged.emit(index, index, [role])
                return True
            except requests.exceptions.RequestException as e:
                QMessageBox.warning(self.parent(), "Errore di Aggiornamento", f"Impossibile salvare le modifiche: {e}")
                # Revert data in model if API call fails (optional)
                # self.load_data() # Or more sophisticated revert logic
                return False
            except Exception as e:
                QMessageBox.warning(self.parent(), "Errore", f"Si è verificato un errore: {e}")
                return False
        return False

    def flags(self, index):
        # Make all columns editable except 'id' and 'stato_certificato'
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        column_name = self._data.columns[index.column()]
        if column_name in ['id', 'stato_certificato']:
            return super().flags(index)

        return super().flags(index) | Qt.ItemFlag.ItemIsEditable

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if not self._data.empty and section < len(self._data.columns):
                return str(self._data.columns[section])
        return None

class ValidationView(QWidget):
    validation_completed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Title
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        title = QLabel("Convalida Dati")
        title.setObjectName("viewTitle") # Using object name for styling
        title_layout.addWidget(title)
        description = QLabel("Verifica, modifica e approva i dati estratti prima dell'archiviazione.")
        description.setObjectName("viewDescription")
        title_layout.addWidget(description)
        self.layout.addLayout(title_layout)

        main_card = QWidget()
        main_card.setObjectName("card")
        main_card_layout = QVBoxLayout(main_card)
        main_card_layout.setSpacing(15)

        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.addStretch()

        self.validate_button = QPushButton("Convalida Selezionati")
        self.validate_button.setObjectName("primary")
        self.validate_button.clicked.connect(self.validate_selected)
        controls_layout.addWidget(self.validate_button)

        self.delete_button = QPushButton("Cancella Selezionati")
        self.delete_button.setObjectName("destructive")
        self.delete_button.clicked.connect(self.delete_selected)
        controls_layout.addWidget(self.delete_button)
        main_card_layout.addLayout(controls_layout)

        # Table
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setItemDelegate(CustomDelegate())

        main_card_layout.addWidget(self.table_view)
        self.layout.addWidget(main_card)

        self.load_data()

        if hasattr(self, 'model') and self.table_view.selectionModel():
            self.table_view.selectionModel().selectionChanged.connect(self.update_button_states)
        self.update_button_states()

    def refresh_data(self):
        """Public slot to reload data from the API."""
        self.load_data()

    def update_button_states(self):
        has_selection = self.table_view.selectionModel().hasSelection()
        self.validate_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def load_data(self):
        try:
            # Fetch unvalidated certificates
            response = requests.get(f"{API_URL}/certificati/?validated=false")
            response.raise_for_status()
            data = response.json()

            if not data:
                self.df = pd.DataFrame()
            else:
                self.df = pd.DataFrame(data)

            self.model = SimpleTableModel(self.df, self)
            self.table_view.setModel(self.model)

            if not self.df.empty:
                # Hide 'id' column
                id_col_index = self.df.columns.get_loc('id')
                self.table_view.setColumnHidden(id_col_index, True)

                # Adjust column widths
                header = self.table_view.horizontalHeader()
                header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
                if 'nome' in self.df.columns:
                    header.setSectionResizeMode(self.df.columns.get_loc('nome'), QHeaderView.ResizeMode.Stretch)
                if 'corso' in self.df.columns:
                    header.setSectionResizeMode(self.df.columns.get_loc('corso'), QHeaderView.ResizeMode.Stretch)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore di Connessione", f"Impossibile caricare i dati da validare: {e}")
            self.df = pd.DataFrame()
            self.model = SimpleTableModel(self.df, self)
            self.table_view.setModel(self.model)


    def get_selected_ids(self):
        if self.df.empty:
            return []

        selection_model = self.table_view.selectionModel()
        selected_rows_indices = selection_model.selectedRows()

        id_column_index = self.df.columns.get_loc('id')

        selected_ids = [str(self.model.index(row.row(), id_column_index).data()) for row in selected_rows_indices]
        return selected_ids

    def delete_selected(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            return

        reply = QMessageBox.question(self, 'Conferma Cancellazione', f'Sei sicuro di voler cancellare {len(selected_ids)} certificati?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.perform_action("delete", selected_ids)

    def validate_selected(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            return

        reply = QMessageBox.question(self, 'Conferma Validazione', f'Sei sicuro di voler validare {len(selected_ids)} certificati?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.perform_action("validate", selected_ids)

    def perform_action(self, action_type, ids):
        success_count = 0
        error_messages = []

        for cert_id in ids:
            try:
                if action_type == "validate":
                    response = requests.put(f"{API_URL}/certificati/{cert_id}/valida")
                else: # delete
                    response = requests.delete(f"{API_URL}/certificati/{cert_id}")

                response.raise_for_status()
                success_count += 1
            except requests.exceptions.RequestException as e:
                error_messages.append(f"ID {cert_id}: {e}")

        if error_messages:
            QMessageBox.warning(self, "Operazione Parzialmente Riuscita",
                                f"{success_count} operazioni riuscite.\n"
                                f"Errori su {len(error_messages)} elementi:\n" + "\n".join(error_messages))
        else:
            QMessageBox.information(self, "Successo", f"Operazione completata con successo su {success_count} elementi.")

        if success_count > 0 and action_type == "validate":
            self.validation_completed.emit()

        self.load_data()
        self.update_button_states()
