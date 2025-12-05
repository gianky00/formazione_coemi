
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QPushButton, QHBoxLayout, QStyledItemDelegate, QLineEdit, QLabel, QMenu, QProgressBar
from PyQt6.QtCore import QAbstractTableModel, Qt, pyqtSignal, QUrl, QThreadPool
from PyQt6.QtGui import QDesktopServices, QAction
import pandas as pd
import requests
from ..api_client import APIClient
from .edit_dialog import EditCertificatoDialog
from app.services.document_locator import find_document
from ..workers.data_worker import FetchCertificatesWorker, DeleteCertificatesWorker, ValidateCertificatesWorker
from ..components.animated_widgets import LoadingOverlay
from ..components.custom_dialog import CustomMessageDialog
import subprocess
import os


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
            return str(val).upper()
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

    def __init__(self, api_client=None):
        super().__init__()
        self.api_client = api_client if api_client else APIClient()
        self.threadpool = QThreadPool()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        description = QLabel("Verifica, modifica e approva i dati estratti prima dell'archiviazione.")
        description.setObjectName("viewDescription")
        self.layout.addWidget(description)

        # Loading Bar (for indeterminate loading)
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)
        self.loading_bar.setFixedHeight(4)
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setStyleSheet("QProgressBar { border: none; background: transparent; } QProgressBar::chunk { background: #1D4ED8; border-radius: 2px; }")
        self.loading_bar.hide()
        self.layout.addWidget(self.loading_bar)

        self.main_card = QWidget()
        self.main_card.setObjectName("card")
        main_card_layout = QVBoxLayout(self.main_card)
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
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self._show_context_menu)

        main_card_layout.addWidget(self.table_view)
        self.layout.addWidget(self.main_card)

        # Loading Overlay (for determinate actions)
        self.loading_overlay = LoadingOverlay(self)

        # Initial Load
        if self.api_client.access_token:
            self.load_data()

        if hasattr(self, 'model') and self.table_view.selectionModel():
            self.table_view.selectionModel().selectionChanged.connect(self.update_button_states)
        self.update_button_states()

    def refresh_data(self):
        """Public slot to reload data from the API."""
        self.load_data()

    def set_loading(self, loading):
        if loading:
            self.loading_bar.show()
            self.main_card.setEnabled(False)
        else:
            self.loading_bar.hide()
            self.main_card.setEnabled(True)

    def set_read_only(self, is_read_only: bool):
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

    def _get_selection_info(self):
        # Bug 4 Fix: Capture selection state
        if not self.table_view.selectionModel() or not self.table_view.selectionModel().hasSelection():
            return {'mode': 'none'}

        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows: return {'mode': 'none'}

        first_row = min(r.row() for r in selected_rows)

        # Try to capture ID
        if hasattr(self, 'df') and not self.df.empty and 'id' in self.df.columns:
             try:
                 # Ensure we are accessing the correct row in dataframe
                 if first_row < len(self.df):
                     return {'mode': 'reselect_by_id', 'id': self.df.iloc[first_row]['id'], 'fallback_row': first_row}
             except:
                 pass

        return {'mode': 'reselect_by_row', 'row': first_row}

    def _restore_selection(self, selection_info):
        # Bug 4 Fix: Restore selection
        if not selection_info or selection_info.get('mode') == 'none':
            return

        if self.df.empty: return

        row_to_select = -1

        if selection_info['mode'] == 'reselect_by_id':
            target_id = selection_info.get('id')
            if 'id' in self.df.columns:
                # Find index of row with this ID
                matches = self.df.index[self.df['id'] == target_id].tolist()
                if matches:
                    row_to_select = matches[0]
                else:
                    # Fallback to similar row position
                    row_to_select = min(selection_info.get('fallback_row', 0), len(self.df) - 1)

        elif selection_info['mode'] == 'reselect_by_row':
            row_to_select = min(selection_info.get('row', 0), len(self.df) - 1)

        if row_to_select != -1 and hasattr(self, 'model') and row_to_select < self.model.rowCount():
            self.table_view.selectRow(row_to_select)

    def edit_data(self):
        if getattr(self, 'is_read_only', False): return

        selected_ids = self.get_selected_ids()
        if not selected_ids or len(selected_ids) > 1:
            CustomMessageDialog.show_warning(self, "Selezione Invalida", "Seleziona una singola riga da modificare.")
            return

        cert_id = selected_ids[0]
        try:
            response = requests.get(f"{self.api_client.base_url}/certificati/{cert_id}", headers=self.api_client._get_headers(), timeout=10)
            response.raise_for_status()
            cert_data = response.json()

            all_categories = self.df['categoria'].unique().tolist() if not self.df.empty else []
            dialog = EditCertificatoDialog(cert_data, all_categories, self)
            if dialog.exec():
                updated_data = dialog.get_data()
                update_response = requests.put(f"{self.api_client.base_url}/certificati/{cert_id}", json=updated_data, headers=self.api_client._get_headers(), timeout=10)
                update_response.raise_for_status()
                CustomMessageDialog.show_info(self, "Successo", "Certificato aggiornato con successo.")

                # Capture selection preference before reload
                self._pending_selection = self._get_selection_info()
                self.load_data()
        except requests.exceptions.RequestException as e:
            CustomMessageDialog.show_error(self, "Errore", f"Impossibile modificare il certificato: {e}")

    def load_data(self):
        self.set_loading(True)
        worker = FetchCertificatesWorker(self.api_client, validated=False)
        worker.signals.result.connect(self._on_data_loaded)
        worker.signals.error.connect(self._on_error)
        worker.signals.finished.connect(lambda: self.set_loading(False))
        self.threadpool.start(worker)

    def _on_error(self, message):
        CustomMessageDialog.show_error(self, "Errore di Connessione", f"Impossibile caricare i dati da validare: {message}")
        self._on_data_loaded([])

    def _on_data_loaded(self, data):
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

            if 'id' in self.df.columns:
                id_col_index = self.df.columns.get_loc('id')
                self.table_view.setColumnHidden(id_col_index, True)

            self.table_view.verticalHeader().setDefaultSectionSize(50)
            header = self.table_view.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            if 'DIPENDENTE' in self.df.columns:
                header.setSectionResizeMode(self.df.columns.get_loc('DIPENDENTE'), QHeaderView.ResizeMode.Stretch)
            if 'DOCUMENTO' in self.df.columns:
                header.setSectionResizeMode(self.df.columns.get_loc('DOCUMENTO'), QHeaderView.ResizeMode.Stretch)
            if 'data_nascita' in self.df.columns:
                header.setSectionResizeMode(self.df.columns.get_loc('data_nascita'), QHeaderView.ResizeMode.ResizeToContents)

        if self.table_view.selectionModel():
            self.table_view.selectionModel().selectionChanged.connect(self.update_button_states)

        self.update_button_states()

        # Restore selection if requested
        if hasattr(self, '_pending_selection'):
            self._restore_selection(self._pending_selection)
            del self._pending_selection

    def get_selected_ids(self):
        if self.df.empty:
            return []

        selection_model = self.table_view.selectionModel()
        if not selection_model: return []
        selected_rows_indices = selection_model.selectedRows()

        if 'id' not in self.df.columns: return []
        id_column_index = self.df.columns.get_loc('id')

        selected_ids = [str(self.model.index(row.row(), id_column_index).data()) for row in selected_rows_indices]
        return selected_ids

    def delete_selected(self):
        if getattr(self, 'is_read_only', False): return
        selected_ids = self.get_selected_ids()
        if not selected_ids: return

        if CustomMessageDialog.show_question(self, 'Conferma Cancellazione', f'Sei sicuro di voler cancellare {len(selected_ids)} certificati?'):
            self.perform_action("delete", selected_ids)

    def validate_selected(self):
        if getattr(self, 'is_read_only', False): return
        selected_ids = self.get_selected_ids()
        if not selected_ids: return

        if CustomMessageDialog.show_question(self, 'Conferma Validazione', f'Sei sicuro di voler validare {len(selected_ids)} certificati?'):
            self.perform_action("validate", selected_ids)

    def perform_action(self, action_type, ids):
        # Use Overlay instead of simple loading
        self.loading_overlay.show_progress(0, len(ids), "Preparazione operazione...")

        if action_type == "validate":
            worker = ValidateCertificatesWorker(self.api_client, ids)
            action_text = "Salvataggio record"
        else:
            worker = DeleteCertificatesWorker(self.api_client, ids)
            action_text = "Cancellazione record"

        worker.signals.progress.connect(lambda cur, tot: self.loading_overlay.show_progress(cur, tot, f"{action_text} {cur} di {tot}..."))
        worker.signals.result.connect(lambda res: self._on_action_completed(res, action_type))
        worker.signals.error.connect(lambda err: CustomMessageDialog.show_error(self, "Errore", f"Errore durante l'operazione: {err}"))
        worker.signals.finished.connect(self.loading_overlay.stop)

        self.threadpool.start(worker)

    def _on_action_completed(self, result, action_type):
        success = result.get("success", 0)
        errors = result.get("errors", [])

        if errors:
            CustomMessageDialog.show_warning(self, "Operazione Parzialmente Riuscita",
                                f"{success} operazioni riuscite.\n"
                                f"Errori su {len(errors)} elementi:\n" + "\n".join(errors))
        else:
            CustomMessageDialog.show_info(self, "Successo", f"Operazione completata con successo su {success} elementi.")

        if success > 0 and action_type == "validate":
            self.validation_completed.emit()

        self.load_data()

    def _show_context_menu(self, pos):
        index = self.table_view.indexAt(pos)
        if not index.isValid(): return

        menu = QMenu(self)
        open_pdf_action = QAction("Apri PDF", self)
        open_folder_action = QAction("Apri percorso file", self)
        menu.addAction(open_pdf_action)
        menu.addAction(open_folder_action)

        action = menu.exec(self.table_view.viewport().mapToGlobal(pos))
        if not action: return

        row_idx = index.row()
        if not hasattr(self, 'model') or row_idx >= self.model.rowCount(): return

        row_data = self.df.iloc[row_idx]
        cert_data = {
            'nome': row_data.get('DIPENDENTE'),
            'matricola': row_data.get('matricola'),
            'categoria': row_data.get('categoria'),
            'data_scadenza': row_data.get('data_scadenza')
        }

        if action == open_pdf_action:
            self._open_document(cert_data, open_folder=False)
        elif action == open_folder_action:
            self._open_document(cert_data, open_folder=True)

    def _open_document(self, cert_data, open_folder=False):
        try:
            paths = self.api_client.get_paths()
            db_path = paths.get('database_path')
            file_path = find_document(db_path, cert_data)

            if file_path:
                if open_folder:
                    if os.name == 'nt':
                        subprocess.run(['explorer', '/select,', file_path])
                    else:
                        QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(file_path)))
                else:
                     QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
            else:
                 CustomMessageDialog.show_warning(self, "Non Trovato", "Il file PDF non è stato trovato nel percorso previsto.")
        except Exception as e:
            CustomMessageDialog.show_error(self, "Errore", f"Impossibile eseguire l'operazione: {e}")
