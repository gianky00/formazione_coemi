import threading
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, 
    QMessageBox, QFrame, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QKeySequence, QShortcut, QColor, QBrush


class AuditView(QWidget):
    data_signal = Signal(list)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.data = []
        self.setStyleSheet("background-color: #F3F4F6;")

        self.setup_ui()
        self.setup_shortcuts()
        self.data_signal.connect(self._update_data)
        self.refresh_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        toolbar = QFrame()
        toolbar.setFixedHeight(60)
        toolbar.setStyleSheet("background-color: #F3F4F6; border: none;")
        t_layout = QHBoxLayout(toolbar)
        
        btn_refresh = QPushButton("Aggiorna")
        btn_refresh.clicked.connect(self.refresh_data)
        t_layout.addWidget(btn_refresh)

        t_layout.addWidget(QLabel("Filtra:"))
        self.combo_cat = QComboBox()
        self.combo_cat.addItems(["TUTTI", "AUTH", "DATA", "CERTIFICATE", "SECURITY"])
        self.combo_cat.currentTextChanged.connect(self.filter_data)
        t_layout.addWidget(self.combo_cat)

        t_layout.addStretch()
        self.lbl_count = QLabel("")
        t_layout.addWidget(self.lbl_count)

        layout.addWidget(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Data/Ora", "Utente", "Azione", "Dettagli", "IP Address", "Severità"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.table)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("F5"), self, self.refresh_data)
        QShortcut(QKeySequence("Ctrl+A"), self, self.table.selectAll)

    def refresh_data(self):
        def fetch():
            try:
                data = self.controller.api_client.get_audit_logs(limit=500)
                self.data_signal.emit(data)
            except: pass
        threading.Thread(target=fetch, daemon=True).start()

    @Slot(list)
    def _update_data(self, data):
        self.data = data
        self.filter_data()

    def filter_data(self):
        cat = self.combo_cat.currentText()
        self.table.setRowCount(0)
        
        count = 0
        for log in self.data:
            if cat != "TUTTI" and log.get("category") != cat:
                continue

            row = self.table.rowCount()
            self.table.insertRow(row)
            
            severity = log.get("severity", "LOW")
            bg_color = None
            if severity == "CRITICAL": bg_color = QColor("#FECACA")
            elif severity == "MEDIUM": bg_color = QColor("#FED7AA")

            cols = [
                log.get("timestamp"),
                log.get("username") or "SYSTEM",
                log.get("action"),
                log.get("details"),
                log.get("ip_address"),
                severity
            ]
            
            for i, val in enumerate(cols):
                q_item = QTableWidgetItem(str(val))
                if bg_color: q_item.setBackground(QBrush(bg_color))
                self.table.setItem(row, i, q_item)
            
            count += 1
        
        self.lbl_count.setText(f"{count} log")
