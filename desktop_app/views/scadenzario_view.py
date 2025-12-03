
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
                             QSplitter, QTreeWidget, QTreeWidgetItem, QGraphicsRectItem,
                             QGraphicsTextItem, QGraphicsLineItem, QPushButton, QHBoxLayout,
                             QScrollBar, QTreeWidgetItemIterator, QFileDialog, QComboBox,
                             QProgressBar)
from PyQt6.QtCore import Qt, QDate, QRectF, QVariantAnimation, QEasingCurve, pyqtSignal, QThreadPool, QLocale
from PyQt6.QtGui import QColor, QBrush, QPen, QFont, QLinearGradient, QPainterPath, QPainter, QPageLayout, QPageSize, QImage
from PyQt6.QtPrintSupport import QPrinter
import requests
from ..api_client import APIClient
from ..components.animated_widgets import AnimatedButton, LoadingOverlay
from ..components.custom_dialog import CustomMessageDialog
from ..workers.data_worker import FetchCertificatesWorker
from ..workers.worker import Worker
from collections import defaultdict
from .gantt_item import GanttBarItem

class ResizingGraphicsView(QGraphicsView):
    resized = pyqtSignal()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit()

class ScadenzarioView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)

        description = QLabel("Timeline interattiva dei certificati in scadenza.")
        description.setStyleSheet("font-size: 14px; color: #6B7280;")
        self.layout.addWidget(description)

        # Toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)

        self.prev_month_button = AnimatedButton("<")
        self.prev_month_button.setFixedSize(30, 30)
        self.prev_month_button.clicked.connect(self.prev_month)
        toolbar_layout.addWidget(self.prev_month_button)

        self.next_month_button = AnimatedButton(">")
        self.next_month_button.setFixedSize(30, 30)
        self.next_month_button.clicked.connect(self.next_month)
        toolbar_layout.addWidget(self.next_month_button)

        toolbar_layout.addSpacing(20)
        zoom_label = QLabel("Zoom:")
        toolbar_layout.addWidget(zoom_label)

        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["3 Mesi", "6 Mesi", "1 Anno"])
        self.zoom_combo.setCurrentIndex(0)
        self.zoom_combo.currentIndexChanged.connect(self.update_zoom_from_combo)
        toolbar_layout.addWidget(self.zoom_combo)

        toolbar_layout.addStretch()

        self.generate_email_button = AnimatedButton("Genera Email")
        self.generate_email_button.clicked.connect(self.generate_email)
        toolbar_layout.addWidget(self.generate_email_button)

        self.export_pdf_button = AnimatedButton("Esporta PDF")
        self.export_pdf_button.set_colors("#FFFFFF", "#F9FAFB", "#F3F4F6", text="#1F2937")
        self.export_pdf_button.clicked.connect(self.export_to_pdf)
        toolbar_layout.addWidget(self.export_pdf_button)

        self.legend_layout = QHBoxLayout()
        self.legend_layout.addStretch()
        toolbar_layout.addLayout(self.legend_layout)

        self.layout.addLayout(toolbar_layout)

        # Loading Bar (for data fetch)
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)
        self.loading_bar.setFixedHeight(4)
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setStyleSheet("QProgressBar { border: none; background: transparent; } QProgressBar::chunk { background: #1D4ED8; border-radius: 2px; }")
        self.loading_bar.hide()
        self.layout.addWidget(self.loading_bar)

        # Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.employee_tree = QTreeWidget()
        self.employee_tree.setHeaderLabels(["Categoria / Dipendenti"])
        self.employee_tree.itemClicked.connect(self._on_tree_item_selected)
        font = QFont()
        font.setPointSize(10)
        self.employee_tree.setFont(font)
        self.splitter.addWidget(self.employee_tree)

        self.gantt_view = ResizingGraphicsView()
        self.gantt_view.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.gantt_view.resized.connect(self.redraw_gantt_scene)
        self.gantt_scene = QGraphicsScene()
        self.gantt_view.setScene(self.gantt_scene)
        self.splitter.addWidget(self.gantt_view)

        self.splitter.setSizes([300, 700])
        self.layout.addWidget(self.splitter)

        self.api_client = APIClient()
        self.threadpool = QThreadPool()
        # Default view: 1 month before today. Total range 3 months covers (-1 to +2).
        self.current_date = QDate.currentDate().addMonths(-1)
        self.zoom_months = 3.0
        self.target_zoom_months = 3.0
        self.certificates = []
        self.category_colors = {}
        self.color_palette = [QColor(c) for c in ["#3b82f6", "#10b981", "#ef4444", "#f97316", "#8b5cf6", "#d946ef", "#14b8a6", "#64748b"]]

        self.zoom_anim = QVariantAnimation(self)
        self.zoom_anim.setDuration(400)
        self.zoom_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.zoom_anim.valueChanged.connect(self._on_zoom_anim_step)

        # Loading Overlay (for PDF/Email actions)
        self.loading_overlay = LoadingOverlay(self)

        self.load_data()

    def update_zoom_from_combo(self, index):
        zoom_map = {0: 3.0, 1: 6.0, 2: 12.0}
        target = zoom_map.get(index, 3.0)
        self.animate_zoom(target)

    def animate_zoom(self, target_months):
        self.zoom_anim.stop()
        self.zoom_anim.setStartValue(self.zoom_months)
        self.zoom_anim.setEndValue(target_months)
        self.zoom_anim.start()

    def _on_zoom_anim_step(self, value):
        self.zoom_months = float(value)
        self.redraw_gantt_scene()

    def _on_tree_item_selected(self, item, column):
        course_data = item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(course_data, dict): return

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

    def prev_month(self):
        self.current_date = self.current_date.addMonths(-1)
        self.redraw_gantt_scene()

    def next_month(self):
        self.current_date = self.current_date.addMonths(1)
        self.redraw_gantt_scene()

    def load_data(self):
        self.loading_bar.show()
        self.splitter.setEnabled(False)
        worker = FetchCertificatesWorker(self.api_client, validated=True)
        worker.signals.result.connect(self._on_data_loaded)
        worker.signals.error.connect(self._on_error)
        worker.signals.finished.connect(self._on_worker_finished)
        self.threadpool.start(worker)

    def _on_worker_finished(self):
        self.loading_bar.hide()
        self.splitter.setEnabled(True)

    def _on_error(self, message):
        self.certificates = []
        self._assign_category_colors()
        self.populate_tree()
        self.redraw_gantt_scene()
        CustomMessageDialog.show_warning(self, "Errore Caricamento", f"Impossibile caricare lo scadenzario:\n{message}")

    def _on_data_loaded(self, all_data):
        if not all_data:
            self.certificates = []
        else:
            excluded_categories = ['ATEX', 'BLSD', 'DIRETTIVA SEVESO', 'DIRIGENTI E FORMATORI', 'H2S', 'MEDICO COMPETENTE', 'HLO']
            filtered_data = [item for item in all_data if item.get('categoria') not in excluded_categories]
            for item in filtered_data:
                item['Dipendente'] = item['nome']
            today = QDate.currentDate()
            self.certificates = sorted([
                item for item in filtered_data
                if 'data_scadenza' in item and item.get('data_scadenza') and today.daysTo(QDate.fromString(item['data_scadenza'], "dd/MM/yyyy")) <= 90
            ], key=lambda x: QDate.fromString(x['data_scadenza'], "dd/MM/yyyy"))

        self._assign_category_colors()
        self.populate_tree()
        self.redraw_gantt_scene()

    def _assign_category_colors(self):
        self.category_colors = {}
        unique_categories = sorted(list(set(cert['categoria'] for cert in self.certificates)))
        for i, category in enumerate(unique_categories):
            self.category_colors[category] = self.color_palette[i % len(self.color_palette)]

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
                    for cert in sorted(statuses[status], key=lambda x: x['Dipendente']):
                        child_item = QTreeWidgetItem(status_item, [f"{cert['Dipendente']} ({cert.get('matricola', 'N/A')})"])
                        child_item.setData(0, Qt.ItemDataRole.UserRole, cert)

    def redraw_gantt_scene(self):
        self.gantt_scene.clear()
        bar_height = 18
        bar_spacing = 4
        row_height = bar_height + bar_spacing
        header_height = 30

        today = QDate.currentDate()
        # Use current_date directly to respect exact "1 month before today" logic
        start_date = self.current_date
        days_total = int(30.44 * self.zoom_months)
        end_date = start_date.addDays(days_total)
        total_days = max(1, start_date.daysTo(end_date))

        scene_width = self.gantt_view.viewport().width()
        if scene_width <= 0: scene_width = 700
        col_width = scene_width / total_days

        zone_definitions = {
            "scaduto": (start_date, today.addDays(-1), QColor(239, 68, 68, 30)),
            "in_scadenza": (today, today.addDays(30), QColor(249, 115, 22, 30)),
            "avviso": (today.addDays(31), today.addDays(90), QColor(251, 191, 36, 30))
        }

        zone_labels = {"scaduto": "SCADUTI", "in_scadenza": "IN SCADENZA", "avviso": "AVVISI"}

        for name, (zone_start, zone_end, color) in zone_definitions.items():
            start_x = max(0, start_date.daysTo(zone_start) * col_width)
            end_x = min(scene_width, start_date.daysTo(zone_end) * col_width)
            if end_x > start_x:
                zone_rect = QGraphicsRectItem(start_x, 0, end_x - start_x, 2000)
                zone_rect.setBrush(QBrush(color))
                zone_rect.setPen(QPen(Qt.PenStyle.NoPen))
                zone_rect.setZValue(-1)
                self.gantt_scene.addItem(zone_rect)

                # Zone Title (Top Right)
                label_text = zone_labels.get(name, name.upper())
                lbl = QGraphicsTextItem(label_text)
                font = QFont()
                font.setBold(True)
                font.setPointSize(12)
                lbl.setFont(font)
                lbl.setDefaultTextColor(QColor(0, 0, 0, 100))

                lbl_width = lbl.boundingRect().width()
                lbl_x = end_x - lbl_width - 10
                if lbl_x < start_x: lbl_x = start_x + 5 # Clamp left

                lbl.setPos(lbl_x, 5) # Top margin
                self.gantt_scene.addItem(lbl)

        current_draw_date = start_date
        while current_draw_date <= end_date:
            # Snap to start of month for labeling, but handle partial first month
            if current_draw_date.day() != 1:
                # If we are inside a month, find the NEXT 1st
                next_month = current_draw_date.addMonths(1)
                next_month.setDate(next_month.year(), next_month.month(), 1)

                # Check if we should label the CURRENT month if it's visible enough?
                # Usually standard Gantt labels 1st of month.
                # If we start on 15 Nov, next 1st is 1 Dec. 15 Nov - 30 Nov is unlabeled?
                # Let's label the *current* month start even if it's before start_date? No.
                # Just draw next month.
                current_draw_date = next_month
                continue

            days_from_start = start_date.daysTo(current_draw_date)
            if days_from_start <= total_days:
                locale = QLocale(QLocale.Language.Italian, QLocale.Country.Italy)
                month_name = locale.toString(current_draw_date, "MMM yyyy").capitalize()
                text = QGraphicsTextItem(month_name)

                # Bold Header
                font = QFont()
                font.setBold(True)
                font.setPointSize(12)
                text.setFont(font)

                text.setPos(days_from_start * col_width, 0)
                self.gantt_scene.addItem(text)
            current_draw_date = current_draw_date.addMonths(1)

        if start_date <= today <= end_date:
            today_x = start_date.daysTo(today) * col_width
            today_line = QGraphicsLineItem(today_x, 0, today_x, 2000)
            today_line.setPen(QPen(QColor("#1D4ED8"), 2))
            self.gantt_scene.addItem(today_line)

        visible_certs = [
            cert for cert in self.certificates
            if (QDate.fromString(cert['data_scadenza'], "dd/MM/yyyy").addDays(-30) <= end_date) and \
               (QDate.fromString(cert['data_scadenza'], "dd/MM/yyyy") >= start_date)
        ]
        sorted_certs = sorted(visible_certs, key=lambda x: QDate.fromString(x['data_scadenza'], "dd/MM/yyyy"))

        y_pos = header_height
        for cert_data in sorted_certs:
            expiry_date = QDate.fromString(cert_data['data_scadenza'], "dd/MM/yyyy")
            days_to_expiry = today.daysTo(expiry_date)
            bar_start_date = expiry_date.addDays(-30)

            start_x = start_date.daysTo(bar_start_date) * col_width
            end_x = start_date.daysTo(expiry_date) * col_width
            bar_width = max(2, end_x - start_x)

            color = self.category_colors.get(cert_data['categoria'], QColor("gray"))
            gradient = QLinearGradient(start_x, y_pos, start_x + bar_width, y_pos)
            gradient.setColorAt(0, color.lighter(120))
            gradient.setColorAt(1, color)

            rect = GanttBarItem(start_x, y_pos, bar_width, bar_height, QBrush(gradient), color, cert_data)
            self.gantt_scene.addItem(rect)
            y_pos += row_height

        total_height = y_pos
        self.gantt_scene.setSceneRect(0, 0, scene_width, total_height)

        for item in self.gantt_scene.items():
            if isinstance(item, QGraphicsRectItem) and item.zValue() == -1:
                item.setRect(item.rect().x(), 0, item.rect().width(), total_height)
            elif isinstance(item, QGraphicsLineItem) and 'today_line' in locals() and item is today_line:
                item.setLine(item.line().x1(), 0, item.line().x2(), total_height)

        self._update_legend(visible_certs)

    def _update_legend(self, visible_certs):
        while self.legend_layout.count() > 1:
            item = self.legend_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        visible_categories = sorted(list(set(cert['categoria'] for cert in visible_certs)))
        for category in visible_categories:
            color = self.category_colors.get(category)
            if color:
                color_box = QLabel()
                color_box.setFixedSize(15, 15)
                color_box.setStyleSheet(f"background-color: {color.name()}; border-radius: 4px;")
                self.legend_layout.insertWidget(0, QLabel(category))
                self.legend_layout.insertWidget(0, color_box)

    def set_read_only(self, is_read_only: bool):
        self.is_read_only = is_read_only
        if is_read_only:
            self.generate_email_button.setEnabled(False)
            self.generate_email_button.setToolTip("Database in sola lettura")
        else:
            self.generate_email_button.setEnabled(True)
            self.generate_email_button.setToolTip("")

    def generate_email(self):
        if getattr(self, 'is_read_only', False): return
        self.loading_overlay.set_text("Invio email in corso...")

        def send():
            return requests.post(f"{self.api_client.base_url}/notifications/send-manual-alert", headers=self.api_client._get_headers(), timeout=60)

        worker = Worker(send)
        worker.signals.result.connect(self._on_email_sent)
        worker.signals.error.connect(lambda err: self._on_generic_error(err, "Errore Invio Email"))
        worker.signals.finished.connect(self.loading_overlay.stop)
        self.threadpool.start(worker)

    def _on_email_sent(self, response):
        if response.status_code == 200:
            CustomMessageDialog.show_info(self, "Successo", "Richiesta di invio email inviata con successo.")
        else:
            error_data = response.json()
            error_detail = error_data.get("detail", "Errore sconosciuto dal server.")
            CustomMessageDialog.show_error(self, "Errore Invio Email", f"Impossibile inviare l'email:\n{error_detail}")

    def refresh_data(self):
        self.load_data()

    def export_to_pdf(self):
        default_filename = f"Report scadenze del {QDate.currentDate().toString('dd_MM_yyyy')}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, "Salva PDF", default_filename, "PDF Files (*.pdf)")
        if not path: return

        self.loading_overlay.set_text("Generazione Report PDF...")

        def download():
            return requests.get(f"{self.api_client.base_url}/notifications/export-report", headers=self.api_client._get_headers(), timeout=60)

        worker = Worker(download)
        worker.signals.result.connect(lambda res: self._on_pdf_downloaded(res, path))
        worker.signals.error.connect(lambda err: self._on_generic_error(err, "Errore Esportazione"))
        worker.signals.finished.connect(self.loading_overlay.stop)
        self.threadpool.start(worker)

    def _on_pdf_downloaded(self, response, path):
        if response.status_code == 200:
            try:
                with open(path, 'wb') as f:
                    f.write(response.content)
                CustomMessageDialog.show_info(self, "Esportazione Riuscita", f"Report esportato con successo in {path}")
            except Exception as e:
                CustomMessageDialog.show_error(self, "Errore", f"Impossibile salvare il file: {e}")
        else:
            CustomMessageDialog.show_error(self, "Errore", f"Errore durante l'esportazione: {response.text}")

    def _on_generic_error(self, error_tuple, title):
        exctype, value, tb = error_tuple
        CustomMessageDialog.show_error(self, title, f"{value}")
