from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                             QGridLayout, QScrollArea, QProgressBar)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QBrush
from desktop_app.api_client import APIClient

class KPIWidget(QFrame):
    def __init__(self, title, value, color="#1E3A8A", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(f"""
            QFrame#card {{
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
                border-left: 5px solid {color};
            }}
        """)
        layout = QVBoxLayout(self)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #6B7280; font-size: 14px; font-weight: 500;")
        layout.addWidget(lbl_title)

        self.lbl_value = QLabel(str(value))
        self.lbl_value.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: 700;")
        layout.addWidget(self.lbl_value)

    def update_value(self, value):
        self.lbl_value.setText(str(value))

class ComplianceBar(QWidget):
    def __init__(self, category, total, compliance_pct, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        header = QHBoxLayout()
        lbl_cat = QLabel(category)
        lbl_cat.setStyleSheet("font-weight: 600; font-size: 14px;")
        header.addWidget(lbl_cat)
        header.addStretch()
        lbl_val = QLabel(f"{compliance_pct}%")
        lbl_val.setStyleSheet(f"font-weight: 700; font-size: 14px; color: {'#10B981' if compliance_pct > 80 else '#F59E0B' if compliance_pct > 50 else '#EF4444'};")
        header.addWidget(lbl_val)
        layout.addLayout(header)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(compliance_pct)
        bar.setTextVisible(False)
        bar.setFixedHeight(8)

        # Color logic via stylesheet
        color = "#10B981" # Green
        if compliance_pct < 50: color = "#EF4444" # Red
        elif compliance_pct < 80: color = "#F59E0B" # Orange

        bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #E5E7EB;
                border-radius: 4px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(bar)

        lbl_detail = QLabel(f"Totale: {total} documenti")
        lbl_detail.setStyleSheet("color: #9CA3AF; font-size: 12px;")
        layout.addWidget(lbl_detail)

class StatsView(QWidget):
    def __init__(self, api_client: APIClient, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Header
        header_lbl = QLabel("Statistiche & KPI")
        header_lbl.setStyleSheet("font-size: 24px; font-weight: 700; color: #1F2937;")
        self.layout.addWidget(header_lbl)

        # KPIs Row
        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.setSpacing(15)

        self.kpi_total = KPIWidget("Dipendenti Totali", "0", "#3B82F6")
        self.kpi_certs = KPIWidget("Certificati Gestiti", "0", "#8B5CF6")
        self.kpi_expired = KPIWidget("Scaduti / In Scadenza", "0", "#EF4444")
        self.kpi_compliance = KPIWidget("Compliance Globale", "0%", "#10B981")

        self.kpi_layout.addWidget(self.kpi_total)
        self.kpi_layout.addWidget(self.kpi_certs)
        self.kpi_layout.addWidget(self.kpi_expired)
        self.kpi_layout.addWidget(self.kpi_compliance)

        self.layout.addLayout(self.kpi_layout)

        # Section Title
        lbl_compliance = QLabel("Compliance per Categoria")
        lbl_compliance.setStyleSheet("font-size: 18px; font-weight: 600; margin-top: 20px;")
        self.layout.addWidget(lbl_compliance)

        # Compliance Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        self.compliance_container = QWidget()
        self.compliance_layout = QGridLayout(self.compliance_container)
        self.compliance_layout.setSpacing(20)
        self.compliance_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self.compliance_container)
        self.layout.addWidget(scroll)

        # Auto-refresh logic (optional, on show is better)

    def refresh_data(self):
        try:
            summary = self.api_client.get("stats/summary")
            if summary:
                self.kpi_total.update_value(summary.get("total_dipendenti", 0))
                self.kpi_certs.update_value(summary.get("total_certificati", 0))
                scad = summary.get("scaduti", 0) + summary.get("in_scadenza", 0)
                self.kpi_expired.update_value(scad)
                self.kpi_compliance.update_value(f"{summary.get('compliance_percent', 0)}%")

            compliance_data = self.api_client.get("stats/compliance")

            # Clear layout
            for i in reversed(range(self.compliance_layout.count())):
                item = self.compliance_layout.itemAt(i)
                if item.widget():
                    item.widget().setParent(None)

            if compliance_data:
                # 2 Columns grid
                row = 0
                col = 0
                for item in compliance_data:
                    widget = ComplianceBar(item['category'], item['total'], item['compliance'])
                    self.compliance_layout.addWidget(widget, row, col)
                    col += 1
                    if col > 1:
                        col = 0
                        row += 1

        except Exception as e:
            print(f"Error fetching stats: {e}")

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()
