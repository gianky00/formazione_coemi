
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QPushButton, QHBoxLayout, QMessageBox, QStyledItemDelegate, QLineEdit, QLabel, QFrame, QProgressBar
from PyQt6.QtCore import QAbstractTableModel, Qt, pyqtSignal, QObject
import pandas as pd
import requests
from datetime import datetime
from ..api_client import APIClient
from .edit_dialog import EditCertificatoDialog

class ValidationWorker(QObject):
    finished = pyqtSignal(int, list)
    progress = pyqtSignal(int)
    status_update = pyqtSignal(str)

    def __init__(self, action_type, ids, api_client):
        super().__init__()
        self.action_type = action_type
        self.ids = ids
        self.api_client = api_client

    def run(self):
        success_count = 0
        error_messages = []
        total_ids = len(self.ids)
        start_time = datetime.now()

        for i, cert_id in enumerate(self.ids):
            elapsed_time = (datetime.now() - start_time).total_seconds()
            avg_time_per_item = elapsed_time / (i + 1)
            remaining_items = total_ids - (i + 1)
            etr_seconds = avg_time_per_item * remaining_items

            if etr_seconds > 60:
                etr_str = f"Circa {int(etr_seconds / 60)} minuti rimanenti"
            else:
                etr_str = f"Circa {int(etr_seconds)} secondi rimanenti"

            self.status_update.emit(f"Validazione record {i+1} di {total_ids} ({etr_str})")

            try:
                if self.action_type == "validate":
                    response = requests.put(f"{self.api_client.base_url}/certificati/{cert_id}/valida", headers=self.api_client._get_headers())
                else: # delete
                    response = requests.delete(f"{self.api_client.base_url}/certificati/{cert_id}", headers=self.api_client._get_headers())

                response.raise_for_status()
                success_count += 1
            except requests.exceptions.RequestException as e:
                error_messages.append(f"ID {cert_id}: {e}")

            self.progress.emit(i + 1)

        self.finished.emit(success_count, error_messages)


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

        # Progress container
        self.progress_container = QFrame()
        self.progress_container.setObjectName("card")
        progress_layout = QVBoxLayout(self.progress_container)
        self.status_label = QLabel("Pronto per la validazione.")
        progress_layout.addWidget(self.status_label)
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        self.progress_container.setVisible(False)
        self.layout.addWidget(self.progress_container)

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

    def set_read_only(self, is_read_only: bool):
        print(f"[DEBUG] ValidationView.set_read_only: {is_read_only}")
        self.is_read_only = is_read_only
        self.update_button_states()

    def update_button_states(self):
        if getattr(self, 'is_read_only', False):
            self.edit_button.setEnabled(False)
            self.validate_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.edit_button.setToolTip("Database in sola lettura")
            self.validate_button.setToolTip("Database in sola lettura")
            self.delete_button.setToolTip("Database in sola lettura")
            return
        else:
            self.edit_button.setToolTip("")
            self.validate_button.setToolTip("")
            self.delete_button.setToolTip("")

        selection_model = self.table_view.selectionModel()
        has_selection = selection_model is not None and selection_model.hasSelection()
        is_single_selection = len(selection_model.selectedRows()) == 1 if has_selection else False

        self.edit_button.setEnabled(is_single_selection)
        self.validate_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def edit_data(self):
        if getattr(self, 'is_read_only', False): return

        selected_ids = self.get_selected_ids()
        if not selected_ids or len(selected_ids) > 1:
            QMessageBox.warning(self, "Selezione Invalida", "Seleziona una singola riga da modificare.")
            return

        cert_id = selected_ids[0]
        try:
            response = requests.get(f"{self.api_client.base_url}/certificati/{cert_id}", headers=self.api_client._get_headers())
            response.raise_for_status()
            cert_data = response.json()

            all_categories = self.df['categoria'].unique().tolist() if not self.df.empty else []
            dialog = EditCertificatoDialog(cert_data, all_categories, self)
            if dialog.exec():
                updated_data = dialog.get_data()
                update_response = requests.put(f"{self.api_client.base_url}/certificati/{cert_id}", json=updated_data, headers=self.api_client._get_headers())
                update_response.raise_for_status()
                QMessageBox.information(self, "Successo", "Certificato aggiornato con successo.")
                self.load_data()
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore", f"Impossibile modificare il certificato: {e}")

    def load_data(self):
        try:
            # Fetch unvalidated certificates
            response = requests.get(f"{self.api_client.base_url}/certificati/?validated=false", headers=self.api_client._get_headers())
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
        if getattr(self, 'is_read_only', False): return

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
        if getattr(self, 'is_read_only', False): return

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
        from PyQt6.QtCore import QThread

        self.progress_bar.setMaximum(len(ids))
        self.progress_bar.setValue(0)
        self.progress_container.setVisible(True)
        self.set_controls_enabled(False)

        self.thread = QThread()
        self.worker = ValidationWorker(action_type, ids, self.api_client)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_validation_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.status_update.connect(self.status_label.setText)

        self.thread.start()

    def on_validation_finished(self, success_count, error_messages):
        self.progress_container.setVisible(False)
        self.set_controls_enabled(True)

        if error_messages:
            QMessageBox.warning(self, "Operazione Parzialmente Riuscita",
                                f"{success_count} operazioni riuscite.\n"
                                f"Errori su {len(error_messages)} elementi:\n" + "\n".join(error_messages))
        else:
            QMessageBox.information(self, "Successo", f"Operazione completata con successo su {success_count} elementi.")

        if success_count > 0:
            self.validation_completed.emit()

        self.load_data()

    def set_controls_enabled(self, enabled):
        self.edit_button.setEnabled(enabled)
        self.validate_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)
        self.table_view.setEnabled(enabled)
