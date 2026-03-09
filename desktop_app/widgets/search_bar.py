from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget


class SearchBar(QWidget):
    """
    Widget standard per la ricerca e i filtri nelle tabelle.
    """

    text_changed = Signal(str)
    filter_changed = Signal(str, str)  # key, value
    refresh_requested = Signal()

    def __init__(self, placeholder="Cerca...", parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Search Input
        self.layout.addWidget(QLabel("Cerca:"))
        self.entry_search = QLineEdit()
        self.entry_search.setPlaceholderText(placeholder)
        self.entry_search.textChanged.connect(self.text_changed.emit)
        self.layout.addWidget(self.entry_search)

        self.combos = {}  # Mantiene i filtri aggiuntivi (es. Categoria, Stato)

    def add_filter(self, label: str, key: str, options: list[str]):
        """Aggiunge un menu a tendina per filtrare una specifica chiave."""
        self.layout.addWidget(QLabel(f"{label}:"))
        combo = QComboBox()
        combo.addItems(options)
        combo.currentTextChanged.connect(lambda v: self.filter_changed.emit(key, v))
        self.layout.addWidget(combo)
        self.combos[key] = combo

    def add_refresh_button(self):
        btn = QPushButton("Aggiorna")
        btn.clicked.connect(self.refresh_requested.emit)
        self.layout.addWidget(btn)

    def clear(self):
        self.entry_search.clear()
        for combo in self.combos.values():
            combo.setCurrentIndex(0)
