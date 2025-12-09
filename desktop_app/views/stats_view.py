from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                             QGridLayout, QScrollArea, QProgressBar, QToolTip)
from PyQt6.QtCore import Qt, QTimer, QPoint, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QBrush, QLinearGradient, QCursor
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
        lbl_title.setStyleSheet("color: #6B7280; font-size: 14px; font-weight: 700; background: transparent;")
        layout.addWidget(lbl_title)

        self.lbl_value = QLabel(str(value))
        self.lbl_value.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: 800; background: transparent;")
        layout.addWidget(self.lbl_value)

    def update_value(self, value):
        self.lbl_value.setText(str(value))


class MultiColorBar(QWidget):
    """A progress bar with multiple colored segments and hover tooltips."""
    
    def __init__(self, category, active_count, expiring_count, expired_count, total, parent=None):
        super().__init__(parent)
        self.category = category
        self.active_count = active_count
        self.expiring_count = expiring_count
        self.expired_count = expired_count
        self.total = max(total, 1)  # Avoid division by zero
        
        self.active_pct = (active_count / self.total) * 100
        self.expiring_pct = (expiring_count / self.total) * 100
        self.expired_pct = (expired_count / self.total) * 100
        
        self.setMouseTracking(True)
        self.setMinimumHeight(60)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        # Header
        header = QHBoxLayout()
        lbl_cat = QLabel(self.category)
        lbl_cat.setStyleSheet("font-weight: 600; font-size: 14px;")
        header.addWidget(lbl_cat)
        header.addStretch()

        compliance_pct = int(self.active_pct)
        if compliance_pct > 80:
            val_color = '#10B981'
        elif compliance_pct > 50:
            val_color = '#F59E0B'
        else:
            val_color = '#EF4444'

        lbl_val = QLabel(f"{compliance_pct}% Attivi")
        lbl_val.setStyleSheet(f"font-weight: 700; font-size: 14px; color: {val_color};")
        header.addWidget(lbl_val)
        layout.addLayout(header)

        # Multi-segment bar container
        self.bar_container = QFrame()
        self.bar_container.setFixedHeight(12)
        self.bar_container.setStyleSheet("""
            QFrame {
                background-color: #E5E7EB;
                border-radius: 6px;
            }
        """)
        
        bar_layout = QHBoxLayout(self.bar_container)
        bar_layout.setContentsMargins(0, 0, 0, 0)
        bar_layout.setSpacing(0)
        
        # Active segment (green)
        if self.active_pct > 0:
            active_seg = QFrame()
            active_seg.setStyleSheet("""
                QFrame {
                    background-color: #10B981;
                    border-top-left-radius: 6px;
                    border-bottom-left-radius: 6px;
                }
            """)
            active_seg.setToolTip(f"Attivi: {self.active_count} ({self.active_pct:.1f}%)")
            bar_layout.addWidget(active_seg, int(self.active_pct * 10))
        
        # Expiring segment (yellow)
        if self.expiring_pct > 0:
            expiring_seg = QFrame()
            expiring_seg.setStyleSheet("QFrame { background-color: #F59E0B; }")
            expiring_seg.setToolTip(f"In Scadenza: {self.expiring_count} ({self.expiring_pct:.1f}%)")
            bar_layout.addWidget(expiring_seg, int(self.expiring_pct * 10))
        
        # Expired segment (red)
        if self.expired_pct > 0:
            expired_seg = QFrame()
            # Round right corners if it's the last segment
            if self.active_pct == 0 and self.expiring_pct == 0:
                expired_seg.setStyleSheet("""
                    QFrame {
                        background-color: #EF4444;
                        border-radius: 6px;
                    }
                """)
            else:
                expired_seg.setStyleSheet("""
                    QFrame {
                        background-color: #EF4444;
                        border-top-right-radius: 6px;
                        border-bottom-right-radius: 6px;
                    }
                """)
            expired_seg.setToolTip(f"Scaduti: {self.expired_count} ({self.expired_pct:.1f}%)")
            bar_layout.addWidget(expired_seg, int(self.expired_pct * 10))
        
        # Empty space for remaining
        remaining = 100 - self.active_pct - self.expiring_pct - self.expired_pct
        if remaining > 0:
            empty_seg = QFrame()
            empty_seg.setStyleSheet("QFrame { background-color: transparent; }")
            bar_layout.addWidget(empty_seg, int(remaining * 10))
        
        layout.addWidget(self.bar_container)

        # Detail label
        lbl_detail = QLabel(f"Totale: {self.total} documenti | Attivi: {self.active_count} | In Scadenza: {self.expiring_count} | Scaduti: {self.expired_count}")
        lbl_detail.setStyleSheet("color: #9CA3AF; font-size: 12px;")
        layout.addWidget(lbl_detail)


class StatsWorker(QThread):
    """Worker thread to fetch stats data."""
    result = pyqtSignal(dict, list)
    error = pyqtSignal(str)
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
    
    def run(self):
        try:
            summary = self.api_client.get("stats/summary") or {}
            compliance = self.api_client.get("stats/compliance") or []
            self.result.emit(summary, compliance)
        except Exception as e:
            self.error.emit(str(e))


class StatsView(QWidget):
    def __init__(self, api_client: APIClient = None, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self._worker = None
        
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
        self.kpi_expired = KPIWidget("Scaduti", "0", "#EF4444")
        self.kpi_expiring = KPIWidget("In Scadenza", "0", "#F59E0B")
        self.kpi_compliance = KPIWidget("Compliance Globale", "0%", "#10B981")

        self.kpi_layout.addWidget(self.kpi_total)
        self.kpi_layout.addWidget(self.kpi_certs)
        self.kpi_layout.addWidget(self.kpi_expired)
        self.kpi_layout.addWidget(self.kpi_expiring)
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

    def refresh_data(self):
        if not self.api_client:
            return
            
        # Stop any running worker
        if self._worker and self._worker.isRunning():
            self._worker.quit()
            self._worker.wait(1000)
        
        self._worker = StatsWorker(self.api_client)
        self._worker.result.connect(self._on_data_received)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._cleanup_worker)
        self._worker.start()
    
    def _cleanup_worker(self):
        """Cleanup worker reference to prevent QThread destruction issues."""
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
    
    def _on_error(self, error_msg):
        pass  # Silently handle errors
    
    def _on_data_received(self, summary, compliance_data):
        if summary:
            self.kpi_total.update_value(summary.get("total_dipendenti", 0))
            self.kpi_certs.update_value(summary.get("total_certificati", 0))
            self.kpi_expired.update_value(summary.get("scaduti", 0))
            self.kpi_expiring.update_value(summary.get("in_scadenza", 0))
            self.kpi_compliance.update_value(f"{summary.get('compliance_percent', 0)}%")

        # Clear layout
        for i in reversed(range(self.compliance_layout.count())):
            item = self.compliance_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        if compliance_data:
            row = 0
            col = 0
            for item in compliance_data:
                widget = MultiColorBar(
                    item['category'],
                    item.get('active', 0),
                    item.get('expiring', 0),
                    item.get('expired', 0),
                    item['total']
                )
                self.compliance_layout.addWidget(widget, row, col)
                col += 1
                if col > 1:
                    col = 0
                    row += 1

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()
    
    def cleanup(self):
        """Cleanup method called when view is destroyed."""
        if self._worker and self._worker.isRunning():
            self._worker.quit()
            self._worker.wait(2000)
            if self._worker.isRunning():
                self._worker.terminate()
