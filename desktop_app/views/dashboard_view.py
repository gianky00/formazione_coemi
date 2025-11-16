
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QPushButton, QHBoxLayout, QComboBox, QLabel, QFileDialog, QMessageBox, QListView, QStyledItemDelegate
from PyQt6.QtCore import QAbstractTableModel, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter
import pandas as pd
import requests
from .edit_dialog import EditCertificatoDialog
from ..api_client import API_URL

class StatusDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        status = index.data(Qt.ItemDataRole.DisplayRole)
        if status:
            painter.save()

            color_map = {
                "attivo": QColor("#ECFDF5"),
                "rinnovato": QColor("#ECFDF5"),
                "scaduto": QColor("#FEF2F2"),
                "in_scadenza": QColor("#FFFBEB")
            }
            text_color_map = {
                "attivo": QColor("#059669"),
                "rinnovato": QColor("#059669"),
                "scaduto": QColor("#DC2626"),
                "in_scadenza": QColor("#F59E0B")
            }

            color = color_map.get(status, QColor("white"))
            text_color = text_color_map.get(status, QColor("black"))

            rect = option.rect
            rect.adjust(5, 3, -5, -3)

            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, rect.height() / 2, rect.height() / 2)

            painter.setPen(text_color)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, status.capitalize())

            painter.restore()

class CertificatoTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        return str(self._data.iloc[index.row(), index.column()])

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if not self._data.empty and section < len(self._data.columns):
                return str(self._data.columns[section])
        return None

class DashboardView(QWidget):
    database_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        title = QLabel("Database Certificati")
        title.setObjectName("viewTitle")
        title_layout.addWidget(title)
        description = QLabel("Visualizza, gestisci ed esporta tutti i certificati dei dipendenti.")
        description.setObjectName("viewDescription")
        title_layout.addWidget(description)
        self.layout.addLayout(title_layout)

        main_card = QWidget()
        main_card.setObjectName("card")
        main_card_layout = QVBoxLayout(main_card)
        main_card_layout.setSpacing(15)

        # Filters and Controls
        control_bar_layout = QHBoxLayout()
        control_bar_layout.setSpacing(10)

        self.dipendente_filter = QComboBox()
        self.dipendente_filter.setMinimumWidth(200)
        self.dipendente_filter.setView(QListView())
        self.dipendente_filter.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        control_bar_layout.addWidget(QLabel("Dipendente:"))
        control_bar_layout.addWidget(self.dipendente_filter)

        self.categoria_filter = QComboBox()
        self.categoria_filter.setMinimumWidth(200)
        self.categoria_filter.setView(QListView())
        self.categoria_filter.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        control_bar_layout.addWidget(QLabel("Categoria:"))
        control_bar_layout.addWidget(self.categoria_filter)

        self.status_filter = QComboBox()
        self.status_filter.setMinimumWidth(150)
        self.status_filter.setView(QListView())
        self.status_filter.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        control_bar_layout.addWidget(QLabel("Stato:"))
        control_bar_layout.addWidget(self.status_filter)

        control_bar_layout.addStretch()

        self.export_button = QPushButton("Esporta")
        self.export_button.setObjectName("secondary")
        self.export_button.clicked.connect(self.export_to_csv)
        control_bar_layout.addWidget(self.export_button)

        self.edit_button = QPushButton("Modifica")
        self.edit_button.clicked.connect(self.edit_data)
        control_bar_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Cancella")
        self.delete_button.setObjectName("destructive")
        self.delete_button.clicked.connect(self.delete_data)
        control_bar_layout.addWidget(self.delete_button)

        main_card_layout.addLayout(control_bar_layout)

        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.table_view.setShowGrid(False)
        self.table_view.setAlternatingRowColors(True)

        main_card_layout.addWidget(self.table_view)
        self.layout.addWidget(main_card)

        # Connect signals once
        self.dipendente_filter.currentIndexChanged.connect(self.filter_data)
        self.categoria_filter.currentIndexChanged.connect(self.filter_data)
        self.status_filter.currentIndexChanged.connect(self.filter_data)

        self._initial_load = True
        self.df_original = pd.DataFrame()
        self.load_data()

        if self.table_view.selectionModel():
            self.table_view.selectionModel().selectionChanged.connect(self.update_button_states)
        self.update_button_states()

    def update_button_states(self):
        selection_model = self.table_view.selectionModel()
        has_selection = selection_model is not None and selection_model.hasSelection()
        is_single_selection = len(selection_model.selectedRows()) == 1 if has_selection else False

        self.edit_button.setEnabled(is_single_selection)
        self.delete_button.setEnabled(has_selection)
        self.export_button.setEnabled(hasattr(self, 'model') and self.model.rowCount() > 0)

    def setup_filters(self):
        # Block signals to prevent premature filtering while populating
        self.dipendente_filter.blockSignals(True)
        self.categoria_filter.blockSignals(True)
        self.status_filter.blockSignals(True)

        self.dipendente_filter.clear()
        dipendenti = sorted(self.df_original['nome'].unique()) if not self.df_original.empty else []
        self.dipendente_filter.addItems(["Tutti"] + dipendenti)

        self.categoria_filter.clear()
        categorie = sorted(self.df_original['categoria'].unique()) if not self.df_original.empty else []
        self.categoria_filter.addItems(["Tutti"] + categorie)

        self.status_filter.clear()
        stati = sorted(self.df_original['stato_certificato'].unique()) if not self.df_original.empty else []
        self.status_filter.addItems(["Tutti"] + stati)

        # Unblock signals
        self.dipendente_filter.blockSignals(False)
        self.categoria_filter.blockSignals(False)
        self.status_filter.blockSignals(False)

    def load_data(self):
        try:
            response = requests.get(f"{API_URL}/certificati/")
            response.raise_for_status()
            data = response.json()

            self.df_original = pd.DataFrame(data) if data else pd.DataFrame()

            if self._initial_load:
                self.setup_filters()
                self._initial_load = False

            self.filter_data()
            self.update_button_states()

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore di Connessione", f"Impossibile caricare i dati: {e}")
            self.df_original = pd.DataFrame()
            self.filter_data()

    def filter_data(self):
        if self.df_original.empty:
            self.model = CertificatoTableModel(pd.DataFrame())
            self.table_view.setModel(self.model)
            self.update_button_states()
            return

        df_filtered = self.df_original.copy()

        dipendente = self.dipendente_filter.currentText()
        if dipendente != "Tutti":
            df_filtered = df_filtered[df_filtered['nome'] == dipendente]

        categoria = self.categoria_filter.currentText()
        if categoria != "Tutti":
            df_filtered = df_filtered[df_filtered['categoria'] == categoria]

        stato = self.status_filter.currentText()
        if stato != "Tutti":
            df_filtered = df_filtered[df_filtered['stato_certificato'] == stato]

        self.model = CertificatoTableModel(df_filtered)
        self.table_view.setModel(self.model)

        if not df_filtered.empty:
            id_col_index = df_filtered.columns.get_loc('id')
            self.table_view.setColumnHidden(id_col_index, True)

            status_col_index = df_filtered.columns.get_loc('stato_certificato')
            self.table_view.setItemDelegateForColumn(status_col_index, StatusDelegate())

            header = self.table_view.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            if 'nome' in df_filtered.columns:
                header.setSectionResizeMode(df_filtered.columns.get_loc('nome'), QHeaderView.ResizeMode.Stretch)
            if 'corso' in df_filtered.columns:
                header.setSectionResizeMode(df_filtered.columns.get_loc('corso'), QHeaderView.ResizeMode.Stretch)

        self.update_button_states()

    def get_selected_ids(self):
        if not hasattr(self, 'model') or self.model.rowCount() == 0:
            return []

        selection_model = self.table_view.selectionModel()
        selected_rows_indices = selection_model.selectedRows()

        df_for_columns = self.model._data
        if df_for_columns.empty:
            return []

        id_column_index = df_for_columns.columns.get_loc('id')
        selected_ids = [str(self.model.index(row.row(), id_column_index).data()) for row in selected_rows_indices]
        return selected_ids

    def edit_data(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids or len(selected_ids) > 1:
            QMessageBox.warning(self, "Selezione Invalida", "Seleziona una singola riga da modificare.")
            return

        cert_id = selected_ids[0]
        try:
            response = requests.get(f"{API_URL}/certificati/{cert_id}")
            response.raise_for_status()
            cert_data = response.json()

            dialog = EditCertificatoDialog(cert_data)
            if dialog.exec():
                updated_data = dialog.get_data()
                update_response = requests.put(f"{API_URL}/certificati/{cert_id}", json=updated_data)
                update_response.raise_for_status()
                QMessageBox.information(self, "Successo", "Certificato aggiornato con successo.")
                self.load_data()
                self.database_changed.emit()
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore", f"Impossibile modificare il certificato: {e}")

    def delete_data(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            return

        reply = QMessageBox.question(self, 'Conferma Cancellazione', f'Sei sicuro di voler cancellare {len(selected_ids)} certificati?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            success_count = 0
            for cert_id in selected_ids:
                try:
                    response = requests.delete(f"{API_URL}/certificati/{cert_id}")
                    response.raise_for_status()
                    success_count += 1
                except requests.exceptions.RequestException:
                    pass
            QMessageBox.information(self, "Operazione Completata", f"{success_count} certificati cancellati con successo.")
            self.load_data()
            if success_count > 0:
                self.database_changed.emit()

    def export_to_csv(self):
        if not hasattr(self, 'model') or self.model.rowCount() == 0:
            QMessageBox.warning(self, "Nessun Dato", "Non ci sono dati da esportare.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Salva CSV", "certificati.csv", "CSV Files (*.csv)")
        if path:
            try:
                self.model._data.to_csv(path, index=False)
                QMessageBox.information(self, "Esportazione Riuscita", f"Dati esportati con successo in {path}")
            except Exception as e:
                QMessageBox.critical(self, "Errore di Esportazione", f"Impossibile salvare il file: {e}")
