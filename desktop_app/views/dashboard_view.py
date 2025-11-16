
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QPushButton, QHBoxLayout, QComboBox, QLabel, QFileDialog, QMessageBox, QListView, QCheckBox, QStyledItemDelegate, QStyleOptionViewItem
from PyQt6.QtCore import QAbstractTableModel, Qt, QItemSelection, QItemSelectionModel, QModelIndex
from PyQt6.QtGui import QPainter, QColor, QFontMetrics, QFont
import pandas as pd
import requests
from .edit_dialog import EditCertificatoDialog
from ..api_client import API_URL

class StatusDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        status = index.data(Qt.ItemDataRole.DisplayRole)
        if status:
            painter.save()

            color_map = {
                "attivo": QColor("#ECFDF5"), "rinnovato": QColor("#ECFDF5"),
                "scaduto": QColor("#FEF2F2"), "in_scadenza": QColor("#FFFBEB")
            }
            text_color_map = {
                "attivo": QColor("#059669"), "rinnovato": QColor("#059669"),
                "scaduto": QColor("#DC2626"), "in_scadenza": QColor("#F59E0B")
            }

            background_color = color_map.get(status, QColor("transparent"))
            text_color = text_color_map.get(status, QColor("#1F2937"))

            font = QFont("Inter", 12, QFont.Weight.Medium)
            metrics = QFontMetrics(font)
            text_width = metrics.horizontalAdvance(status)

            pill_rect = option.rect.adjusted(10, 5, -10, -5)
            pill_rect.setWidth(text_width + 24)

            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(background_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(pill_rect, 12, 12)

            painter.setFont(font)
            painter.setPen(text_color)
            painter.drawText(pill_rect, Qt.AlignmentFlag.AlignCenter, status)

            painter.restore()
        else:
            super().paint(painter, option, index)

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
        self.layout.setSpacing(20)

        # Title and Description
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        title = QLabel("Database Certificati")
        title.setStyleSheet("font-size: 28px; font-weight: 700;")
        title_layout.addWidget(title)
        description = QLabel("Esplora, filtra e gestisci tutti i certificati dei dipendenti.")
        description.setStyleSheet("font-size: 16px; color: #6B7280;")
        title_layout.addWidget(description)
        self.layout.addLayout(title_layout)

        # Main Content Card
        main_card = QWidget()
        main_card.setObjectName("card")
        main_card_layout = QVBoxLayout(main_card)
        main_card_layout.setSpacing(20)

        # Control Bar
        control_bar_layout = QHBoxLayout()
        control_bar_layout.setSpacing(10)

        # Filters
        self.employee_filter = QComboBox()
        self.employee_filter.setPlaceholderText("Filtra per Dipendente")
        control_bar_layout.addWidget(self.employee_filter)

        self.category_filter = QComboBox()
        self.category_filter.setPlaceholderText("Filtra per Categoria")
        control_bar_layout.addWidget(self.category_filter)

        self.status_filter = QComboBox()
        self.status_filter.setPlaceholderText("Filtra per Stato")
        control_bar_layout.addWidget(self.status_filter)

        self.filter_button = QPushButton("Filtra")
        self.filter_button.clicked.connect(self.load_data)
        control_bar_layout.addWidget(self.filter_button)

        control_bar_layout.addStretch()

        # Action Buttons
        self.export_button = QPushButton("Esporta")
        self.export_button.setObjectName("secondary")
        self.export_button.clicked.connect(self.export_to_csv)
        control_bar_layout.addWidget(self.export_button)

        self.edit_button = QPushButton("Modifica")
        self.edit_button.setObjectName("secondary")
        self.edit_button.clicked.connect(self.edit_data)
        control_bar_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Cancella")
        self.delete_button.setObjectName("destructive")
        self.delete_button.clicked.connect(self.delete_data)
        control_bar_layout.addWidget(self.delete_button)

        main_card_layout.addLayout(control_bar_layout)

        # Table
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.table_view.setShowGrid(False)
        self.table_view.setMouseTracking(True)
        self.table_view.entered.connect(self.table_view.viewport().update)

        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_view.clicked.connect(self.on_row_clicked)

        main_card_layout.addWidget(self.table_view)
        self.layout.addWidget(main_card)

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

                employees = ["Tutti"] + sorted(list(set([item['dipendente'] for item in data])))
                categories = ["Tutti"] + sorted(list(set([item['categoria'] for item in data])))
                stati = ["Tutti", "attivo", "scaduto", "rinnovato", "in_scadenza"]

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

                if employee != "Tutti": self.df = self.df[self.df['dipendente'] == employee]
                if category != "Tutti": self.df = self.df[self.df['categoria'] == category]
                if status != "Tutti": self.df = self.df[self.df['stato_certificato'] == status]

                self.model = CheckboxTableModel(self.df)
                self.model.setParent(self)
                self.table_view.setModel(self.model)

                # Set delegate for status column
                status_column_index = self.df.columns.get_loc('stato_certificato') + 1
                self.table_view.setItemDelegateForColumn(status_column_index, StatusDelegate(self.table_view))
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
