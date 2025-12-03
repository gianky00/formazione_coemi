from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableView, QHeaderView, QHBoxLayout,
    QComboBox, QLabel, QFileDialog, QListView, QFrame,
    QMenu, QProgressBar
)
from PyQt6.QtCore import QAbstractTableModel, Qt, pyqtSignal, QTimer, QUrl
from PyQt6.QtGui import QColor, QPainter, QDesktopServices, QAction
from .edit_dialog import EditCertificatoDialog
from ..view_models.database_view_model import DatabaseViewModel
from ..api_client import APIClient
from ..components.animated_widgets import AnimatedButton, AnimatedInput, CardWidget
from ..components.cascade_delegate import CascadeDelegate
from ..components.custom_dialog import CustomMessageDialog
from app.services.document_locator import find_document
import requests
import pandas as pd
import html
import subprocess
import os


class StatusDelegate(CascadeDelegate):
    def paint(self, painter, option, index):
        painter.save()
        if not self.prepare_painter(painter, index):
            painter.restore()
            return

        # Custom Painting Logic
        status = index.data(Qt.ItemDataRole.DisplayRole)
        if status:
            color_map = {
                "ATTIVO": QColor("#ECFDF5"), "ARCHIVIATO": QColor("#ECFDF5"),
                "SCADUTO": QColor("#FEF2F2"), "IN_SCADENZA": QColor("#FFFBEB")
            }
            text_color_map = {
                "ATTIVO": QColor("#059669"), "ARCHIVIATO": QColor("#059669"),
                "SCADUTO": QColor("#DC2626"), "IN_SCADENZA": QColor("#F59E0B")
            }
            color = color_map.get(status, QColor("white"))
            text_color = text_color_map.get(status, QColor("black"))
            rect = option.rect
            rect.adjust(5, 3, -5, -3)

            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, rect.height() / 2, rect.height() / 2)
            painter.setPen(text_color)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, status.replace("_", " ").capitalize())

        painter.restore()

class CertificatoTableModel(QAbstractTableModel):
    def __init__(self, data, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._data = data

    def flags(self, index):
        return super().flags(index)

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        val = self._data.iloc[index.row(), index.column()]
        if pd.isna(val) or val == "None" or val is None:
            return ""
        # Return uppercase string without HTML escaping to display correct characters like '
        return str(val).upper()

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if not self._data.empty and section < len(self._data.columns):
                return str(self._data.columns[section]).replace("_", " ")
        return None

class DatabaseView(QWidget):
    database_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.model = None
        self.view_model = DatabaseViewModel()
        self.api_client = APIClient()

        self._init_ui()
        self._connect_signals()
        self.view_model.load_data()

    def _init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Header / Description
        header_layout = QHBoxLayout()
        description = QLabel("Visualizza, gestisci ed esporta tutti i certificati dei dipendenti.")
        description.setStyleSheet("color: #6B7280; font-size: 14px;")
        header_layout.addWidget(description)
        header_layout.addStretch()
        self.layout.addLayout(header_layout)

        # Loading Bar
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0) # Indeterminate
        self.loading_bar.setFixedHeight(4)
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setStyleSheet("QProgressBar { border: none; background: transparent; } QProgressBar::chunk { background: #1D4ED8; border-radius: 2px; }")
        self.loading_bar.hide()
        self.layout.addWidget(self.loading_bar)

        # --- FILTER CARD ---
        self.filter_card = CardWidget()
        filter_layout = QHBoxLayout(self.filter_card)
        filter_layout.setSpacing(15)
        filter_layout.setContentsMargins(20, 20, 20, 20)

        self.dipendente_filter = QComboBox()
        self.dipendente_filter.setMinimumWidth(200)
        self.dipendente_filter.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        filter_layout.addWidget(QLabel("Dipendente:"))
        filter_layout.addWidget(self.dipendente_filter)

        self.categoria_filter = QComboBox()
        self.categoria_filter.setMinimumWidth(200)
        self.categoria_filter.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        filter_layout.addWidget(QLabel("Categoria:"))
        filter_layout.addWidget(self.categoria_filter)

        self.status_filter = QComboBox()
        self.status_filter.setMinimumWidth(150)
        self.status_filter.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        filter_layout.addWidget(QLabel("Stato:"))
        filter_layout.addWidget(self.status_filter)

        self.search_input = AnimatedInput()
        self.search_input.setPlaceholderText("Cerca...")
        self.search_input.setMinimumWidth(200)
        filter_layout.addWidget(QLabel("Cerca:"))
        filter_layout.addWidget(self.search_input)

        filter_layout.addStretch()

        # Actions in Filter Card
        self.export_button = AnimatedButton("Esporta")
        self.export_button.set_colors("#FFFFFF", "#F9FAFB", "#F3F4F6", text="#1F2937") # Secondary style
        self.export_button.setStyleSheet("border: 1px solid #D1D5DB; border-radius: 8px;")
        filter_layout.addWidget(self.export_button)

        self.edit_button = AnimatedButton("Modifica")
        filter_layout.addWidget(self.edit_button)

        self.delete_button = AnimatedButton("Cancella")
        self.delete_button.set_colors("#DC2626", "#B91C1C", "#991B1B")
        filter_layout.addWidget(self.delete_button)

        self.layout.addWidget(self.filter_card)

        # --- DATA CARD ---
        self.data_card = CardWidget()
        data_layout = QVBoxLayout(self.data_card)
        data_layout.setContentsMargins(0, 0, 0, 0) # Table flush with card? No, padding looks better.
        data_layout.setContentsMargins(20, 20, 20, 20)

        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self._show_context_menu)
        self.table_view.setShowGrid(False)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setStyleSheet("""
            QTableView { border: none; background-color: #FFFFFF; }
            QTableView::item:selected { background-color: #EFF6FF; color: #1E40AF; }
        """)

        data_layout.addWidget(self.table_view)
        self.layout.addWidget(self.data_card)

        # Animate Cards In
        self.filter_card.animate_in(delay=100)
        self.data_card.animate_in(delay=300)

    def _connect_signals(self):
        self.view_model.data_changed.connect(self.on_data_changed)
        self.view_model.error_occurred.connect(self._show_error_message)
        self.view_model.operation_completed.connect(self._show_success_message)
        self.view_model.loading_changed.connect(self._on_loading_changed)

        self.dipendente_filter.currentIndexChanged.connect(self._trigger_filter)
        self.categoria_filter.currentIndexChanged.connect(self._trigger_filter)
        self.status_filter.currentIndexChanged.connect(self._trigger_filter)
        self.search_input.textChanged.connect(self._trigger_filter)

        self.export_button.clicked.connect(self.export_to_csv)
        self.edit_button.clicked.connect(self.edit_data)
        self.delete_button.clicked.connect(self.delete_data)

    def load_data(self):
        self._current_selection = self._get_selection_info()
        self.view_model.load_data()

    def _on_loading_changed(self, is_loading):
        if is_loading:
            self.loading_bar.show()
            self.filter_card.setEnabled(False)
            self.data_card.setEnabled(False)
        else:
            self.loading_bar.hide()
            self.filter_card.setEnabled(True)
            self.data_card.setEnabled(True)

    def on_data_changed(self):
        self._update_table_view()
        self._update_filters()
        self._restore_selection()
        self._update_button_states()

    def _update_table_view(self):
        df = self.view_model.filtered_data

        if self.table_view.model() and self.table_view.selectionModel():
            try: self.table_view.selectionModel().selectionChanged.disconnect(self._update_button_states)
            except: pass

        if not df.empty:
            if 'matricola' not in df.columns: df['matricola'] = None
            if 'data_nascita' not in df.columns: df['data_nascita'] = None

            column_order = ['id', 'Dipendente', 'data_nascita', 'matricola', 'DOCUMENTO', 'categoria', 'DATA_EMISSIONE', 'data_scadenza', 'stato_certificato']
            df = df[[col for col in column_order if col in df.columns]]

            self.model = CertificatoTableModel(df)
            self.table_view.setModel(self.model)

            self.table_view.setColumnHidden(df.columns.get_loc('id'), True)

            # Set Delegates
            self.status_delegate = StatusDelegate(self.table_view)
            self.default_delegate = CascadeDelegate(self.table_view)

            status_col_index = df.columns.get_loc('stato_certificato')

            for col in range(df.shape[1]):
                if col == status_col_index:
                    self.table_view.setItemDelegateForColumn(col, self.status_delegate)
                else:
                    self.table_view.setItemDelegateForColumn(col, self.default_delegate)

            self.table_view.verticalHeader().setDefaultSectionSize(50)
            header = self.table_view.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(df.columns.get_loc('Dipendente'), QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(df.columns.get_loc('DOCUMENTO'), QHeaderView.ResizeMode.Stretch)
        else:
            self.model = CertificatoTableModel(df)
            self.table_view.setModel(self.model)

        if self.table_view.selectionModel():
            self.table_view.selectionModel().selectionChanged.connect(self._update_button_states)

        self._update_button_states()

    def _update_filters(self):
        self.dipendente_filter.blockSignals(True)
        self.categoria_filter.blockSignals(True)
        self.status_filter.blockSignals(True)

        current_dipendente = self.dipendente_filter.currentText()
        current_categoria = self.categoria_filter.currentText()
        current_status = self.status_filter.currentText()

        options = self.view_model.get_filter_options()
        self.dipendente_filter.clear(); self.dipendente_filter.addItems(["Tutti"] + options["dipendenti"])
        self.categoria_filter.clear(); self.categoria_filter.addItems(["Tutti"] + options["categorie"])
        self.status_filter.clear(); self.status_filter.addItems(["Tutti"] + options["stati"])

        self.dipendente_filter.setCurrentText(current_dipendente)
        self.categoria_filter.setCurrentText(current_categoria)
        self.status_filter.setCurrentText(current_status)

        self.dipendente_filter.blockSignals(False)
        self.categoria_filter.blockSignals(False)
        self.status_filter.blockSignals(False)

    def _trigger_filter(self):
        self.view_model.filter_data(
            self.dipendente_filter.currentText(),
            self.categoria_filter.currentText(),
            self.status_filter.currentText(),
            self.search_input.text()
        )

    def set_read_only(self, is_read_only: bool):
        print(f"[DEBUG] DashboardView.set_read_only: {is_read_only}")
        self.is_read_only = is_read_only
        self._update_button_states()

    def _update_button_states(self):
        if getattr(self, 'is_read_only', False):
            self.edit_button.setEnabled(False)
            self.edit_button.setToolTip("Database in sola lettura")
            self.delete_button.setEnabled(False)
            self.delete_button.setToolTip("Database in sola lettura")
        else:
            self.edit_button.setEnabled(True)
            self.edit_button.setToolTip("")
            self.delete_button.setEnabled(True)
            self.delete_button.setToolTip("")

        self.export_button.setEnabled(self.model is not None and self.model.rowCount() > 0)

    def _get_selection_info(self):
        if not self.table_view.selectionModel() or not self.table_view.selectionModel().hasSelection():
            return {'mode': 'none'}

        selected_rows = self.table_view.selectionModel().selectedRows()
        first_row = min(r.row() for r in selected_rows)

        if self.model and 0 <= first_row < self.model.rowCount():
             id_index = self.model.index(first_row, self.model._data.columns.get_loc('id'))
             return {'mode': 'reselect_by_id', 'id': self.model.data(id_index), 'fallback_row': first_row}

        return {'mode': 'reselect_by_row', 'row': first_row}

    def _restore_selection(self):
        if not hasattr(self, '_current_selection') or not self.model:
            return

        selection_mode = self._current_selection.get('mode', 'none')
        if selection_mode == 'none' or self.model.rowCount() == 0:
            return

        row_to_select = -1
        if selection_mode == 'reselect_by_id':
            target_id = self._current_selection.get('id')
            matches = self.model._data.index[self.model._data['id'] == target_id].tolist()
            if matches:
                row_to_select = matches[0]
            else: # Fallback
                row_to_select = min(self._current_selection.get('fallback_row', 0), self.model.rowCount() - 1)

        elif selection_mode == 'reselect_by_row':
            row_to_select = min(self._current_selection.get('row', 0), self.model.rowCount() - 1)

        if row_to_select != -1:
            self.table_view.selectRow(row_to_select)

    def _show_error_message(self, message):
        CustomMessageDialog.show_error(self, "Errore", message)

    def _show_success_message(self, message):
        CustomMessageDialog.show_info(self, "Successo", message)

    def edit_data(self):
        if getattr(self, 'is_read_only', False):
            return

        selection_info = self._get_selection_info()
        if selection_info['mode'] == 'none' or len(self.table_view.selectionModel().selectedRows()) > 1:
            CustomMessageDialog.show_warning(self, "Selezione Invalida", "Seleziona una singola riga da modificare.")
            return

        cert_id_to_edit = selection_info.get('id')
        if not cert_id_to_edit: return

        try:
            response = requests.get(f"{self.api_client.base_url}/certificati/{cert_id_to_edit}", headers=self.api_client._get_headers(), timeout=10)
            response.raise_for_status()
            cert_data = response.json()

            all_categories = self.view_model.get_filter_options()['categorie']
            dialog = EditCertificatoDialog(cert_data, all_categories)
            if dialog.exec():
                updated_data = dialog.get_data()
                self._current_selection = self._get_selection_info()
                if self.view_model.update_certificate(cert_id_to_edit, updated_data):
                     self.database_changed.emit()

        except requests.exceptions.RequestException as e:
            self._show_error_message(f"Impossibile recuperare i dati del certificato: {e}")

    def delete_data(self):
        if getattr(self, 'is_read_only', False):
            return

        if not self.table_view.selectionModel() or not self.table_view.selectionModel().hasSelection():
            return

        selected_ids = [self.model.index(r.row(), self.model._data.columns.get_loc('id')).data() for r in self.table_view.selectionModel().selectedRows()]

        if CustomMessageDialog.show_question(self, 'Conferma Cancellazione', f'Sei sicuro di voler cancellare {len(selected_ids)} certificati?'):
            self._current_selection = self._get_selection_info()
            self.view_model.delete_certificates(selected_ids)
            self.database_changed.emit()

    def export_to_csv(self):
        if self.model is None or self.model.rowCount() == 0:
            CustomMessageDialog.show_warning(self, "Nessun Dato", "Non ci sono dati da esportare.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Salva CSV", "certificati.csv", "CSV Files (*.csv)")
        if path:
            try:
                self.model._data.to_csv(path, index=False)
                CustomMessageDialog.show_info(self, "Esportazione Riuscita", f"Dati esportati con successo in {path}")
            except Exception as e:
                self._show_error_message(f"Impossibile salvare il file: {e}")

    def _show_context_menu(self, pos):
        index = self.table_view.indexAt(pos)
        if not index.isValid():
            return

        menu = QMenu(self)

        # Define Actions
        open_pdf_action = QAction("Apri PDF", self)
        open_folder_action = QAction("Apri percorso file", self)

        menu.addAction(open_pdf_action)
        menu.addAction(open_folder_action)

        # Execute Menu
        action = menu.exec(self.table_view.viewport().mapToGlobal(pos))

        if not action:
            return

        # Prepare Data
        row_idx = index.row()
        if not self.model or row_idx >= len(self.model._data):
            return

        row_data = self.model._data.iloc[row_idx]
        cert_data = {
            'nome': row_data.get('Dipendente'),
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
                    # Windows specific selection
                    if os.name == 'nt':
                        subprocess.run(['explorer', '/select,', file_path])
                    else:
                        # Fallback for Linux/Mac: just open the folder
                        QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(file_path)))
                else:
                     QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
            else:
                 CustomMessageDialog.show_warning(self, "Non Trovato", "Il file PDF non è stato trovato nel percorso previsto.\n\nPotrebbe essere stato spostato, rinominato manualmente o non ancora archiviato.")

        except Exception as e:
            CustomMessageDialog.show_error(self, "Errore", f"Impossibile eseguire l'operazione: {e}")
