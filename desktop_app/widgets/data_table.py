from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMenu
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QBrush, QColor

class DataTable(QTableWidget):
    """
    Widget tabella riutilizzabile con funzionalità standard di Intelleo.
    """
    row_double_clicked = Signal(dict)
    context_menu_requested = Signal(QPoint, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_defaults()
        self.raw_data = [] # Mantiene il riferimento ai dati originali per riga
        self.itemDoubleClicked.connect(self._on_double_click)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

    def _setup_defaults(self):
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)

    def set_columns(self, labels: list[str]):
        self.setColumnCount(len(labels))
        self.setHorizontalHeaderLabels(labels)

    def load_data(self, data_list: list[dict], column_mapping: list[str], color_callback=None):
        """
        Popola la tabella.
        :param data_list: Lista di dizionari con i dati.
        :param column_mapping: Lista di chiavi dei dizionari corrispondenti alle colonne.
        :param color_callback: Funzione che accetta (item_dict) e ritorna un QColor per il background.
        """
        self.setRowCount(0)
        self.raw_data = data_list
        
        for row_idx, item in enumerate(data_list):
            self.insertRow(row_idx)
            bg_color = color_callback(item) if color_callback else None
            
            for col_idx, key in enumerate(column_mapping):
                val = str(item.get(key, ""))
                if val.lower() == "none": val = ""
                
                q_item = QTableWidgetItem(val)
                if bg_color:
                    q_item.setBackground(QBrush(bg_color))
                
                self.setItem(row_idx, col_idx, q_item)

    def get_selected_data(self) -> list[dict]:
        """Ritorna la lista dei dati associati alle righe selezionate."""
        rows = sorted(set(index.row() for index in self.selectedIndexes()))
        return [self.raw_data[r] for r in rows if r < len(self.raw_data)]

    def _on_double_click(self, item):
        row = item.row()
        if row < len(self.raw_data):
            self.row_double_clicked.emit(self.raw_data[row])

    def _on_context_menu(self, pos):
        item = self.itemAt(pos)
        if item:
            row = item.row()
            if row < len(self.raw_data):
                self.context_menu_requested.emit(pos, self.raw_data[row])
