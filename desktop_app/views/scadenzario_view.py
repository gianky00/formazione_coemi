
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
                             QSplitter, QTreeWidget, QTreeWidgetItem, QGraphicsRectItem,
                             QGraphicsTextItem, QGraphicsLineItem, QPushButton, QHBoxLayout,
                             QScrollBar, QTreeWidgetItemIterator, QMessageBox, QFileDialog, QComboBox)
from PyQt6.QtCore import Qt, QDate, QRectF
from PyQt6.QtGui import QColor, QBrush, QPen, QFont, QLinearGradient, QPainterPath, QPainter, QPageLayout, QPageSize
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
        self.zoom_combo.setCurrentIndex(1)
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
        self.legend_items = {
            "Scaduto": "#EF4444",
            "In scadenza (< 30 gg)": "#F97316",
            "Avviso (30-90 gg)": "#FBBF24"
        }
        for text, color in self.legend_items.items():
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
        self.employee_tree.itemClicked.connect(self._on_tree_item_selected)
        font = QFont()
        font.setPointSize(10)
        self.employee_tree.setFont(font)
        self.splitter.addWidget(self.employee_tree)

        self.gantt_view = QGraphicsView()
        self.gantt_scene = QGraphicsScene()
        self.gantt_view.setScene(self.gantt_scene)
        self.splitter.addWidget(self.gantt_view)

        self.splitter.setSizes([300, 700])
        self.layout.addWidget(self.splitter)

        self.api_client = APIClient()
        self.current_date = QDate.currentDate()
        self.zoom_months = 6
        self.certificates = []
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

        for scene_item in self.gantt_scene.items():
            if isinstance(scene_item, GanttBarItem):
                scene_item.setBrush(QBrush(scene_item.color))
                scene_item.setPen(QPen(Qt.PenStyle.NoPen))

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
            self.certificates = sorted([
                item for item in all_data
                if 'data_scadenza' in item and item.get('data_scadenza') and today.daysTo(QDate.fromString(item['data_scadenza'], "dd/MM/yyyy")) <= 90
            ], key=lambda x: QDate.fromString(x['data_scadenza'], "dd/MM/yyyy"))
        except requests.exceptions.RequestException:
            self.certificates = []
        self.populate_tree()
        self.redraw_gantt_scene()

    def populate_tree(self):
        self.employee_tree.clear()
        data_by_category = defaultdict(lambda: defaultdict(list))
        for item in self.certificates:
            status = "SCADUTI" if QDate.currentDate() > QDate.fromString(item['data_scadenza'], "dd/MM/yyyy") else "IN SCADENZA"
            data_by_category[item['categoria']][status].append(item)

        for category, statuses in sorted(data_by_category.items()):
            category_item = QTreeWidgetItem(self.employee_tree, [category])
            category_item.setData(0, Qt.ItemDataRole.UserRole, "category")
            for status in ["IN SCADENZA", "SCADUTI"]:
                if status in statuses:
                    status_item = QTreeWidgetItem(category_item, [status])
                    status_item.setData(0, Qt.ItemDataRole.UserRole, "status_folder")
                    for cert in sorted(statuses[status], key=lambda x: x['nome']):
                        child_item = QTreeWidgetItem(status_item, [f"{cert['nome']} ({cert.get('matricola', 'N/A')})"])
                        child_item.setData(0, Qt.ItemDataRole.UserRole, cert)

    def redraw_gantt_scene(self):
        self.gantt_scene.clear()

        bar_height = 18
        bar_spacing = 4
        row_height = bar_height + bar_spacing
        header_height = 30

        today = QDate.currentDate()
        start_date = self.current_date.addDays(-self.current_date.day() + 1)
        end_date = start_date.addMonths(self.zoom_months)
        total_days = start_date.daysTo(end_date)
        if total_days <= 0: return

        scene_width = self.gantt_view.viewport().width()
        col_width = scene_width / total_days

        for i in range(total_days + 1):
            date = start_date.addDays(i)
            if date.day() == 1:
                month_name = date.toString("MMM yyyy")
                text = QGraphicsTextItem(month_name)
                text.setPos(i * col_width, 0)
                self.gantt_scene.addItem(text)

        if start_date <= today <= end_date:
            today_x = start_date.daysTo(today) * col_width
            today_line = QGraphicsLineItem(today_x, 0, today_x, 2000)
            today_line.setPen(QPen(QColor("#1D4ED8"), 2))
            self.gantt_scene.addItem(today_line)

        y_pos = header_height
        for cert_data in self.certificates:
            expiry_date = QDate.fromString(cert_data['data_scadenza'], "dd/MM/yyyy")
            days_to_expiry = today.daysTo(expiry_date)
            bar_start_date = expiry_date.addDays(-30)

            start_x = start_date.daysTo(bar_start_date) * col_width
            end_x = start_date.daysTo(expiry_date) * col_width
            bar_width = max(2, end_x - start_x)

            color = QColor(self.legend_items["Avviso (30-90 gg)"])
            if days_to_expiry < 30: color = QColor(self.legend_items["In scadenza (< 30 gg)"])
            if days_to_expiry < 0: color = QColor(self.legend_items["Scaduto"])

            gradient = QLinearGradient(start_x, y_pos, start_x + bar_width, y_pos)
            gradient.setColorAt(0, color.lighter(120))
            gradient.setColorAt(1, color)

            rect = GanttBarItem(start_x, y_pos, bar_width, bar_height, QBrush(gradient), color, cert_data)
            self.gantt_scene.addItem(rect)

            y_pos += row_height

        total_height = y_pos
        self.gantt_scene.setSceneRect(0, 0, scene_width, total_height)
        if 'today_line' in locals():
            today_line.setLine(today_line.line().x1(), 0, today_line.line().x2(), total_height)

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
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A3))
        printer.setPageOrientation(QPageLayout.Orientation.Landscape)

        painter = QPainter(printer)
        page_rect = printer.pageRect(QPrinter.Unit.Point)

        margin = 30
        content_rect = QRectF(page_rect.left() + margin, page_rect.top() + margin,
                              page_rect.width() - 2 * margin, page_rect.height() - 2 * margin)

        font_h1 = QFont("Arial", 16, QFont.Weight.Bold)
        font_h2 = QFont("Arial", 11)
        font_body = QFont("Arial", 9)
        font_small = QFont("Arial", 8, QFont.Weight.Bold)
        pen_default = QPen(Qt.GlobalColor.black)

        header_height = 80
        row_height = 20

        certs_to_print = self.certificates
        items_per_page = int((content_rect.height() - header_height) / row_height)
        total_pages = max(1, (len(certs_to_print) + items_per_page - 1) // items_per_page)

        for page_num in range(total_pages):
            if page_num > 0:
                printer.newPage()

            painter.setFont(font_h1)
            painter.drawText(QRectF(content_rect.left(), content_rect.top(), content_rect.width(), 40), Qt.AlignmentFlag.AlignCenter, "Report Scadenzario Certificati")

            painter.setFont(font_h2)
            start_date_str = self.current_date.toString("dd/MM/yyyy")
            end_date_str = self.current_date.addMonths(self.zoom_months).toString("dd/MM/yyyy")
            painter.drawText(QRectF(content_rect.left(), content_rect.top() + 30, content_rect.width(), 20), Qt.AlignmentFlag.AlignCenter, f"Periodo: {start_date_str} - {end_date_str}")

            legend_y = content_rect.top() + 55
            legend_x = content_rect.left()
            for text, color in self.legend_items.items():
                painter.setBrush(QBrush(QColor(color)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(QRectF(legend_x, legend_y, 15, 10), 3, 3)
                painter.setPen(pen_default)
                painter.setFont(font_body)
                text_width = painter.fontMetrics().horizontalAdvance(text)
                painter.drawText(QRectF(legend_x + 20, legend_y-2, text_width, 15), Qt.AlignmentFlag.AlignLeft, text)
                legend_x += (text_width + 40)

            content_y_start = content_rect.top() + header_height

            gantt_start_x = content_rect.left() + (content_rect.width() * 0.4)
            gantt_width = content_rect.width() * 0.6

            start_date = self.current_date.addDays(-self.current_date.day() + 1)
            end_date = start_date.addMonths(self.zoom_months)
            total_days = start_date.daysTo(end_date)
            col_width = gantt_width / total_days if total_days > 0 else 0

            for i in range(total_days + 1):
                date = start_date.addDays(i)
                if date.day() == 1:
                    month_name = date.toString("MMM yy")
                    painter.setFont(font_small)
                    painter.setPen(QPen(Qt.GlobalColor.lightGray))
                    painter.drawLine(int(gantt_start_x + i * col_width), int(content_y_start - 15), int(gantt_start_x + i * col_width), int(content_rect.bottom()))
                    painter.setPen(pen_default)
                    painter.drawText(int(gantt_start_x + i * col_width + 3), int(content_y_start - 15), month_name)

            start_item_index = page_num * items_per_page
            end_item_index = min(start_item_index + items_per_page, len(certs_to_print))

            current_y = content_y_start
            for i in range(start_item_index, end_item_index):
                cert_data = certs_to_print[i]

                # Draw Text Label on the left
                painter.setFont(font_body)
                painter.setPen(pen_default)
                label = f"{cert_data['categoria']} - {cert_data['nome']} ({cert_data['matricola']}) - Scad: {cert_data['data_scadenza']}"
                painter.drawText(QRectF(content_rect.left(), current_y, content_rect.width() * 0.4 - 10, row_height), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, label)

                # Draw Gantt Bar
                today = QDate.currentDate()
                expiry_date = QDate.fromString(cert_data['data_scadenza'], "dd/MM/yyyy")
                days_to_expiry = today.daysTo(expiry_date)
                bar_start_date = expiry_date.addDays(-30)

                start_x_offset = start_date.daysTo(bar_start_date) * col_width
                end_x_offset = start_date.daysTo(expiry_date) * col_width
                bar_width = max(1, end_x_offset - start_x_offset)

                color = QColor(self.legend_items["Avviso (30-90 gg)"])
                if days_to_expiry < 30: color = QColor(self.legend_items["In scadenza (< 30 gg)"])
                if days_to_expiry < 0: color = QColor(self.legend_items["Scaduto"])

                painter.setBrush(QBrush(color))
                painter.setPen(Qt.PenStyle.NoPen)
                bar_rect = QRectF(gantt_start_x + start_x_offset, current_y + 2, bar_width, row_height - 6)
                painter.drawRoundedRect(bar_rect, 3, 3)

                current_y += row_height

        painter.end()
        QMessageBox.information(self, "Esportazione Riuscita", f"Gantt esportato con successo in {path}")
