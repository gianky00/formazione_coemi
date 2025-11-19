
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
                             QSplitter, QTreeWidget, QTreeWidgetItem, QGraphicsRectItem,
                             QGraphicsTextItem, QGraphicsLineItem, QPushButton, QHBoxLayout,
                             QScrollBar, QTreeWidgetItemIterator, QMessageBox, QFileDialog, QComboBox)
from PyQt6.QtCore import Qt, QDate, QRectF
from PyQt6.QtGui import QColor, QBrush, QPen, QFont, QLinearGradient, QPainterPath, QPainter, QPageLayout, QPageSize, QImage
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
        self.gantt_view.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
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

        # Sort certificates by expiration date to ensure they are displayed from top to bottom
        sorted_certs = sorted(self.certificates, key=lambda x: QDate.fromString(x['data_scadenza'], "dd/MM/yyyy"))

        y_pos = header_height
        for cert_data in sorted_certs:
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

        # --- Layout Constants ---
        margin = 50
        header_height = 80
        footer_height = 50
        row_height = 25
        label_area_width_ratio = 0.35

        page_rect = printer.pageRect(QPrinter.Unit.Point)
        content_rect = QRectF(
            page_rect.left() + margin,
            page_rect.top() + margin + header_height,
            page_rect.width() - 2 * margin,
            page_rect.height() - 2 * margin - header_height - footer_height
        )

        # --- Fonts and Pens ---
        font_title = QFont("Arial", 18, QFont.Weight.Bold)
        font_header = QFont("Arial", 10, QFont.Weight.Bold)
        font_body = QFont("Arial", 9)
        font_footer = QFont("Arial", 8)
        pen_default = QPen(Qt.GlobalColor.black)
        pen_light = QPen(QColor("#D3D3D3"))

        # --- Logo ---
        logo_image = QImage("desktop_app/assets/logo.png")

        # --- Data ---
        sorted_certs = sorted(self.certificates, key=lambda x: QDate.fromString(x['data_scadenza'], "dd/MM/yyyy"))
        items_per_page = int(content_rect.height() / row_height)
        if items_per_page <= 0:
            QMessageBox.critical(self, "Errore", "Impossibile calcolare il layout della pagina, l'altezza è troppo piccola.")
            return

        total_pages = max(1, (len(sorted_certs) + items_per_page - 1) // items_per_page)

        # --- Date Range for Gantt ---
        gantt_start_date = self.current_date.addDays(-self.current_date.day() + 1)
        gantt_end_date = gantt_start_date.addMonths(self.zoom_months)
        total_days = gantt_start_date.daysTo(gantt_end_date)
        if total_days <= 0:
            QMessageBox.critical(self, "Errore", "Intervallo di date non valido per il Gantt.")
            return

        # --- Drawing Loop ---
        for page_num in range(total_pages):
            if page_num > 0:
                printer.newPage()

            # --- Header ---
            painter.setFont(font_title)
            painter.drawText(QRectF(page_rect.left(), page_rect.top() + margin, page_rect.width(), 40), Qt.AlignmentFlag.AlignCenter, "Report Scadenzario Certificati")
            if not logo_image.isNull():
                logo_target_rect = QRectF(page_rect.left() + margin, page_rect.top() + margin, 150, 60)
                painter.drawImage(logo_target_rect, logo_image)

            # --- Footer ---
            painter.setFont(font_footer)
            painter.setPen(pen_default)
            footer_text = "Restricted | Internal Use Only"
            painter.drawText(QRectF(page_rect.left(), page_rect.bottom() - margin, page_rect.width(), footer_height), Qt.AlignmentFlag.AlignCenter, footer_text)
            page_text = f"Pagina {page_num + 1} di {total_pages}"
            painter.drawText(QRectF(page_rect.right() - margin - 100, page_rect.bottom() - margin, 100, footer_height), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, page_text)

            # --- Gantt Area ---
            label_area_width = content_rect.width() * label_area_width_ratio
            gantt_area_width = content_rect.width() * (1 - label_area_width_ratio)
            gantt_area_x_start = content_rect.left() + label_area_width
            col_width = gantt_area_width / total_days

            # Draw Month Headers and Grid
            for i in range(total_days + 1):
                date = gantt_start_date.addDays(i)
                x_pos = gantt_area_x_start + i * col_width
                if date.day() == 1:
                    painter.setPen(pen_light)
                    painter.drawLine(int(x_pos), int(content_rect.top()), int(x_pos), int(content_rect.bottom()))
                    painter.setPen(pen_default)
                    painter.setFont(font_header)
                    painter.drawText(int(x_pos + 3), int(content_rect.top() - 5), date.toString("MMM yyyy"))

            # --- Draw Certificate Rows for the current page ---
            start_item_index = page_num * items_per_page
            end_item_index = min(start_item_index + items_per_page, len(sorted_certs))

            for i in range(start_item_index, end_item_index):
                cert_data = sorted_certs[i]
                row_index_on_page = i - start_item_index
                current_y = content_rect.top() + (row_index_on_page * row_height)

                # Draw Text Label
                painter.setFont(font_body)
                painter.setPen(pen_default)
                label = f"{cert_data['nome']} ({cert_data.get('matricola', 'N/A')}) - {cert_data['categoria']}"
                label_rect = QRectF(content_rect.left(), current_y, label_area_width - 10, row_height)
                painter.drawText(label_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextElideRight, label)

                # Draw Gantt Bar
                today = QDate.currentDate()
                expiry_date = QDate.fromString(cert_data['data_scadenza'], "dd/MM/yyyy")
                days_to_expiry = today.daysTo(expiry_date)
                bar_start_date = expiry_date.addDays(-30)

                start_x_offset = gantt_start_date.daysTo(bar_start_date) * col_width
                end_x_offset = gantt_start_date.daysTo(expiry_date) * col_width
                bar_width = max(2, end_x_offset - start_x_offset)

                color = QColor(self.legend_items["Avviso (30-90 gg)"])
                if days_to_expiry < 30: color = QColor(self.legend_items["In scadenza (< 30 gg)"])
                if days_to_expiry < 0: color = QColor(self.legend_items["Scaduto"])

                painter.setBrush(QBrush(color))
                painter.setPen(Qt.PenStyle.NoPen)
                bar_rect = QRectF(gantt_area_x_start + start_x_offset, current_y + 4, bar_width, row_height - 8)
                painter.drawRoundedRect(bar_rect, 4, 4)

        painter.end()
        QMessageBox.information(self, "Esportazione Riuscita", f"Gantt esportato con successo in {path}")
