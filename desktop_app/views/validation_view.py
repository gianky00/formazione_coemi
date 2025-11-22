
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QPushButton, QHBoxLayout, QMessageBox, QStyledItemDelegate, QLineEdit, QLabel
from PyQt6.QtCore import QAbstractTableModel, Qt, pyqtSignal
import pandas as pd
import requests
from ..api_client import APIClient
from .edit_dialog import EditCertificatoDialog


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
            val = self._data.iloc[index.row(), index.column()]
            if pd.isna(val) or val == "None" or val is None:
                return ""
            return str(val)
        return None

    def flags(self, index):
        return super().flags(index)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if not self._data.empty and section < len(self._data.columns):
                return str(self._data.columns[section]).replace("_", " ")
        return None

class ValidationView(QWidget):
    validation_completed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        description = QLabel("Verifica, modifica e approva i dati estratti prima dell'archiviazione.")
        description.setObjectName("viewDescription")
        self.layout.addWidget(description)

        main_card = QWidget()
        main_card.setObjectName("card")
        main_card_layout = QVBoxLayout(main_card)
        main_card_layout.setSpacing(15)

        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.addStretch()

        self.edit_button = QPushButton("Modifica")
        controls_layout.addWidget(self.edit_button)

        self.validate_button = QPushButton("Convalida Selezionati")
        self.validate_button.setObjectName("primary")
        self.validate_button.clicked.connect(self.validate_selected)
        controls_layout.addWidget(self.validate_button)

        self.delete_button = QPushButton("Cancella Selezionati")
        self.delete_button.setObjectName("destructive")
        self.delete_button.clicked.connect(self.delete_selected)
        controls_layout.addWidget(self.delete_button)
        main_card_layout.addLayout(controls_layout)

        self.edit_button.clicked.connect(self.edit_data)

        # Table
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.table_view.setAlternatingRowColors(True)
        # self.table_view.setItemDelegate(CustomDelegate())

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
        selection_model = self.table_view.selectionModel()
        has_selection = selection_model is not None and selection_model.hasSelection()
        is_single_selection = len(selection_model.selectedRows()) == 1 if has_selection else False

        self.edit_button.setEnabled(is_single_selection)
        self.validate_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def edit_data(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids or len(selected_ids) > 1:
            QMessageBox.warning(self, "Selezione Invalida", "Seleziona una singola riga da modificare.")
            return

        cert_id = selected_ids[0]
        try:
            response = requests.get(f"{self.api_client.base_url}/certificati/{cert_id}")
            response.raise_for_status()
            cert_data = response.json()

            all_categories = self.df['categoria'].unique().tolist() if not self.df.empty else []
            dialog = EditCertificatoDialog(cert_data, all_categories, self)
            if dialog.exec():
                updated_data = dialog.get_data()
                update_response = requests.put(f"{self.api_client.base_url}/certificati/{cert_id}", json=updated_data)
                update_response.raise_for_status()
                QMessageBox.information(self, "Successo", "Certificato aggiornato con successo.")
                self.load_data()
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore", f"Impossibile modificare il certificato: {e}")

    def load_data(self):
        try:
            # Fetch unvalidated certificates
            response = requests.get(f"{self.api_client.base_url}/certificati/?validated=false")
            response.raise_for_status()
            data = response.json()

            if not data:
                self.df = pd.DataFrame()
            else:
                self.df = pd.DataFrame(data)
                self.df.rename(columns={
                    'nome': 'DIPENDENTE',
                    'data_rilascio': 'DATA_EMISSIONE',
                    'corso': 'DOCUMENTO',
                    'assegnazione_fallita_ragione': 'CAUSA'
                }, inplace=True)

            self.model = SimpleTableModel(self.df, self)
            self.table_view.setModel(self.model)

            if not self.df.empty:
                if 'stato_certificato' in self.df.columns:
                    self.df['stato_certificato'] = self.df['stato_certificato'].apply(lambda x: str(x).replace('_', ' ') if x else x)

                if 'data_nascita' not in self.df.columns:
                    self.df['data_nascita'] = None

                column_order = ['id', 'DIPENDENTE', 'data_nascita', 'matricola', 'DOCUMENTO', 'categoria', 'DATA_EMISSIONE', 'data_scadenza', 'stato_certificato', 'CAUSA']
                existing_columns = [col for col in column_order if col in self.df.columns]
                self.df = self.df[existing_columns]

                self.model = SimpleTableModel(self.df, self)
                self.table_view.setModel(self.model)

                # Hide 'id' column
                id_col_index = self.df.columns.get_loc('id')
                self.table_view.setColumnHidden(id_col_index, True)

                # Increase row height
                self.table_view.verticalHeader().setDefaultSectionSize(50)

                # Adjust column widths
                header = self.table_view.horizontalHeader()
                header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
                if 'DIPENDENTE' in self.df.columns:
                    header.setSectionResizeMode(self.df.columns.get_loc('DIPENDENTE'), QHeaderView.ResizeMode.Stretch)
                if 'DOCUMENTO' in self.df.columns:
                    header.setSectionResizeMode(self.df.columns.get_loc('DOCUMENTO'), QHeaderView.ResizeMode.Stretch)
                if 'data_nascita' in self.df.columns:
                    header.setSectionResizeMode(self.df.columns.get_loc('data_nascita'), QHeaderView.ResizeMode.ResizeToContents)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore di Connessione", f"Impossibile caricare i dati da validare: {e}")
            self.df = pd.DataFrame()
            self.model = SimpleTableModel(self.df, self)
            self.table_view.setModel(self.model)

        # Reconnect the selection signal because setModel() clears previous selection model
        if self.table_view.selectionModel():
            self.table_view.selectionModel().selectionChanged.connect(self.update_button_states)

        # Update buttons initially
        self.update_button_states()


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

        selection_model = self.table_view.selectionModel()
        selected_rows = selection_model.selectedRows()
        first_row = min((r.row() for r in selected_rows), default=-1)

        reply = QMessageBox.question(self, 'Conferma Cancellazione', f'Sei sicuro di voler cancellare {len(selected_ids)} certificati?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.perform_action("delete", selected_ids, first_row)

    def validate_selected(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            return

        selection_model = self.table_view.selectionModel()
        selected_rows = selection_model.selectedRows()
        first_row = min((r.row() for r in selected_rows), default=-1)

        reply = QMessageBox.question(self, 'Conferma Validazione', f'Sei sicuro di voler validare {len(selected_ids)} certificati?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.perform_action("validate", selected_ids, first_row)

    def perform_action(self, action_type, ids, row_to_reselect=-1):
        success_count = 0
        error_messages = []

        for cert_id in ids:
            try:
                if action_type == "validate":
                    response = requests.put(f"{self.api_client.base_url}/certificati/{cert_id}/valida")
                else: # delete
                    response = requests.delete(f"{self.api_client.base_url}/certificati/{cert_id}")

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

        # After reloading, try to re-select a row to keep the flow
        if row_to_reselect != -1:
            new_row_count = self.model.rowCount()
            if new_row_count > 0:
                # Select the same index, or the last item if the index is now out of bounds
                final_row = min(row_to_reselect, new_row_count - 1)
                self.table_view.selectRow(final_row)
