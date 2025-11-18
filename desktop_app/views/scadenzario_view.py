
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
                             QSplitter, QTreeWidget, QTreeWidgetItem, QGraphicsRectItem,
                             QGraphicsTextItem, QGraphicsLineItem, QPushButton, QHBoxLayout,
                             QScrollBar, QTreeWidgetItemIterator, QMessageBox, QFileDialog, QComboBox)
from PyQt6.QtCore import Qt, QDate
from PyQt.QtGui import QColor, QBrush, QPen, QFont, QLinearGradient, QPainterPath, QPainter, QPageLayout
from PyQt6.QtPrintSupport import QPrinter
import requests
from ..api_client import APIClient
from collections import defaultdict
from .gantt_item import GanttBarItem

class ScadenzarioView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)

        # Main Title and Description
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        title = QLabel("Scadenzario Grafico")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        title_layout.addWidget(title)
        description = QLabel("Timeline interattiva dei certificati in scadenza.")
        description.setStyleSheet("font-size: 14px; color: #6B7280;")
        title_layout.addWidget(description)
        self.layout.addLayout(title_layout)

        # Toolbar Layout
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)

        self.prev_month_button = QPushButton("<")
        self.prev_month_button.clicked.connect(self.prev_month)
        toolbar_layout.addWidget(self.prev_month_button)

        self.next_month_button = QPushButton(">")
        self.next_month_button.clicked.connect(self.next_month)
        toolbar_layout.addWidget(self.next_month_button)

        toolbar_layout.addSpacing(20)

        zoom_label = QLabel("Zoom:")
        toolbar_layout.addWidget(zoom_label)
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["3 Mesi", "6 Mesi", "1 Anno"])
        self.zoom_combo.setCurrentIndex(1) # Default to 6 months
        self.zoom_combo.currentIndexChanged.connect(self.update_zoom_from_combo)
        toolbar_layout.addWidget(self.zoom_combo)

        toolbar_layout.addStretch()

        self.generate_email_button = QPushButton("Genera Email")
        self.generate_email_button.setObjectName("primary")
        self.generate_email_button.clicked.connect(self.generate_email)
        toolbar_layout.addWidget(self.generate_email_button)

        self.export_pdf_button = QPushButton("Esporta PDF")
        self.export_pdf_button.setObjectName("secondary")
        self.export_pdf_button.clicked.connect(self.export_to_pdf)
        toolbar_layout.addWidget(self.export_pdf_button)

        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.addStretch()
        legend_items = {
            "Scaduto": "#EF4444",
            "In scadenza (< 30 gg)": "#F97316",
            "Avviso (30-90 gg)": "#FBBF24"
        }
        for text, color in legend_items.items():
            color_box = QLabel()
            color_box.setFixedSize(15, 15)
            color_box.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
            legend_layout.addWidget(color_box)
            legend_layout.addWidget(QLabel(text))
        toolbar_layout.addLayout(legend_layout)

        self.layout.addLayout(toolbar_layout)

        # Main Content Area (Tree and Gantt)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.employee_tree = QTreeWidget()
        self.employee_tree.setHeaderLabels(["Categoria / Dipendenti"])
        self.employee_tree.itemExpanded.connect(self.redraw_gantt_scene)
        self.employee_tree.itemCollapsed.connect(self.redraw_gantt_scene)
        self.employee_tree.itemClicked.connect(self._on_tree_item_selected)
        font = QFont()
        font.setPointSize(10)
        self.employee_tree.setFont(font)
        self.splitter.addWidget(self.employee_tree)

        self.gantt_view = QGraphicsView()
        self.gantt_scene = QGraphicsScene()
        self.gantt_view.setScene(self.gantt_scene)
        self.splitter.addWidget(self.gantt_view)

        self.splitter.setSizes([250, 750]) # Initial sizing
        self.layout.addWidget(self.splitter)

        # Sync Scrollbars
        self.gantt_view.verticalScrollBar().valueChanged.connect(self.employee_tree.verticalScrollBar().setValue)
        self.employee_tree.verticalScrollBar().valueChanged.connect(self.gantt_view.verticalScrollBar().setValue)

        self.api_client = APIClient()
        self.current_date = QDate.currentDate()
        self.zoom_months = 6
        self.load_data()

    def update_zoom_from_combo(self, index):
        zoom_map = {0: 3, 1: 6, 2: 12}
        self.set_zoom(zoom_map.get(index, 6))

    def set_zoom(self, months):
        self.zoom_months = months
        self.redraw_gantt_scene()

    def _on_tree_item_selected(self, item, column):
        course_data = item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(course_data, dict):
            return

        # Reset all items to their original state
        for scene_item in self.gantt_scene.items():
            if isinstance(scene_item, GanttBarItem):
                scene_item.setBrush(QBrush(scene_item.color))
                scene_item.setPen(QPen(Qt.PenStyle.NoPen))

        # Find the corresponding bar and highlight it
        for rect_item in self.gantt_scene.items():
            if isinstance(rect_item, GanttBarItem) and rect_item.data(Qt.ItemDataRole.UserRole) == course_data:
                self.gantt_view.ensureVisible(rect_item)
                rect_item.setBrush(QBrush(QColor("lightblue")))
                rect_item.setPen(QPen(QColor("blue"), 2))
                break

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.redraw_gantt_scene()

    def prev_month(self):
        self.current_date = self.current_date.addMonths(-1)
        self.redraw_gantt_scene()

    def next_month(self):
        self.current_date = self.current_date.addMonths(1)
        self.redraw_gantt_scene()

    def load_data(self):
        try:
            response = requests.get(f"{self.api_client.base_url}/certificati/?validated=true")
            all_data = response.json() if response.status_code == 200 else []

            today = QDate.currentDate()
            self.data = [
                item for item in all_data
                if 'data_scadenza' in item and item.get('data_scadenza') and today.daysTo(QDate.fromString(item['data_scadenza'], "dd/MM/yyyy")) <= 90
            ]
        except requests.exceptions.RequestException:
            self.data = []

        self.populate_tree()

    def populate_tree(self):
        self.employee_tree.clear()
        data_by_category = defaultdict(lambda: defaultdict(list))
        today = QDate.currentDate()

        for item in self.data:
            expiry_date = QDate.fromString(item['data_scadenza'], "dd/MM/yyyy")
            days_to_expiry = today.daysTo(expiry_date)

            status = "SCADUTI" if days_to_expiry < 0 else "IN SCADENZA"
            data_by_category[item['categoria']][status].append(item)

        for category, statuses in sorted(data_by_category.items()):
            if not statuses.get("IN SCADENZA") and not statuses.get("SCADUTI"):
                continue

            category_item = QTreeWidgetItem(self.employee_tree, [category])
            category_item.setData(0, Qt.ItemDataRole.UserRole, "category")

            if "IN SCADENZA" in statuses:
                in_scadenza_item = QTreeWidgetItem(category_item, ["IN SCADENZA"])
                in_scadenza_item.setData(0, Qt.ItemDataRole.UserRole, "status_folder")
                for item in sorted(statuses["IN SCADENZA"], key=lambda x: x['nome']):
                    child_item = QTreeWidgetItem(in_scadenza_item, [f"{item['nome']} ({item.get('matricola', 'N/A')})"])
                    child_item.setData(0, Qt.ItemDataRole.UserRole, item)

            if "SCADUTI" in statuses:
                scaduti_item = QTreeWidgetItem(category_item, ["SCADUTI"])
                scaduti_item.setData(0, Qt.ItemDataRole.UserRole, "status_folder")
                for item in sorted(statuses["SCADUTI"], key=lambda x: x['nome']):
                    child_item = QTreeWidgetItem(scaduti_item, [f"{item['nome']} ({item.get('matricola', 'N/A')})"])
                    child_item.setData(0, Qt.ItemDataRole.UserRole, item)

        self.employee_tree.expandAll()
        self.redraw_gantt_scene()

    def redraw_gantt_scene(self):
        self.gantt_scene.clear()

        row_height = 20
        header_height = 30
        today = QDate.currentDate()

        start_date = self.current_date.addDays(-self.current_date.day() + 1)
        end_date = start_date.addMonths(self.zoom_months)
        total_days = start_date.daysTo(end_date)

        if total_days <= 0: return

        scene_width = self.gantt_view.viewport().width()
        col_width = scene_width / total_days

        # Draw Header
        for i in range(total_days + 1):
            date = start_date.addDays(i)
            if date.day() == 1:
                month_name = date.toString("MMM yyyy")
                text = QGraphicsTextItem(month_name)
                text.setPos(i * col_width, 0)
                self.gantt_scene.addItem(text)

        # Draw Today Line
        if start_date <= today <= end_date:
            today_x = start_date.daysTo(today) * col_width
            today_line = QGraphicsLineItem(today_x, 0, today_x, self.gantt_view.viewport().height())
            today_line.setPen(QPen(QColor("#1D4ED8"), 2))
            self.gantt_scene.addItem(today_line)

        y_pos = header_height
        iterator = QTreeWidgetItemIterator(self.employee_tree)
        while iterator.value():
            item = iterator.value()
            if not item.isHidden():
                course_data = item.data(0, Qt.ItemDataRole.UserRole)
                if isinstance(course_data, dict) and 'data_scadenza' in course_data:
                    expiry_date = QDate.fromString(course_data['data_scadenza'], "dd/MM/yyyy")
                    days_to_expiry = today.daysTo(expiry_date)

                    bar_start_date = expiry_date.addDays(-30)
                    start_x = start_date.daysTo(bar_start_date) * col_width
                    end_x = start_date.daysTo(expiry_date) * col_width
                    bar_width = max(2, end_x - start_x)

                    color = QColor("#FBBF24")  # Avviso
                    if days_to_expiry < 30: color = QColor("#F97316") # In scadenza
                    if days_to_expiry < 0: color = QColor("#EF4444") # Scaduto

                    gradient = QLinearGradient(start_x, y_pos, start_x + bar_width, y_pos)
                    gradient.setColorAt(0, color.lighter(120))
                    gradient.setColorAt(1, color)

                    rect = GanttBarItem(start_x, y_pos + (row_height / 4), bar_width, row_height / 1.5, QBrush(gradient), color, course_data)
                    self.gantt_scene.addItem(rect)
                y_pos += row_height
            iterator += 1

        self.gantt_scene.setSceneRect(0, 0, scene_width, y_pos)

    def generate_email(self):
        try:
            response = requests.post(f"{self.api_client.base_url}/notifications/send-manual-alert")
            response.raise_for_status()
            QMessageBox.information(self, "Successo", "Richiesta di invio email inviata con successo.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore", f"Impossibile inviare la richiesta: {e}")

    def refresh_data(self):
        self.load_data()

    def export_to_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salva PDF", "scadenzario.pdf", "PDF Files (*.pdf)")
        if not path:
            return

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(path)

        page_layout = QPageLayout()
        page_layout.setOrientation(QPageLayout.Orientation.Landscape)
        printer.setPageLayout(page_layout)

        painter = QPainter(printer)

        # Ensure the scene has the correct dimensions for rendering
        original_size = self.gantt_view.size()
        printer_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
        self.gantt_scene.setSceneRect(0, 0, printer_rect.width(), printer_rect.height())
        self.gantt_scene.render(painter)

        # Restore original scene rect
        self.gantt_scene.setSceneRect(0, 0, original_size.width(), self.gantt_view.viewport().height())

        painter.end()
        QMessageBox.information(self, "Esportazione Riuscita", f"Gantt esportato con successo in {path}")
