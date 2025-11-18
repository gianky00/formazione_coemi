
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
                             QSplitter, QTreeWidget, QTreeWidgetItem, QGraphicsRectItem,
                             QGraphicsTextItem, QGraphicsLineItem, QPushButton, QHBoxLayout,
                             QScrollBar, QTreeWidgetItemIterator, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QBrush, QPen, QFont, QLinearGradient, QPainterPath
import requests
from ..api_client import APIClient
from collections import defaultdict
from .gantt_item import GanttBarItem

class ScadenzarioView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10) # Reduced spacing

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2) # Reduced spacing
        title = QLabel("Scadenzario Grafico")
        title.setStyleSheet("font-size: 24px; font-weight: 700;") # Reduced font size
        title_layout.addWidget(title)
        description = QLabel("Timeline interattiva dei certificati in scadenza.")
        description.setStyleSheet("font-size: 14px; color: #6B7280;") # Reduced font size
        title_layout.addWidget(description)
        self.layout.addLayout(title_layout)

        nav_layout = QHBoxLayout()
        self.prev_month_button = QPushButton("< Mese Prec.")
        self.prev_month_button.clicked.connect(self.prev_month)
        nav_layout.addWidget(self.prev_month_button)

        self.next_month_button = QPushButton("Mese Succ. >")
        self.next_month_button.clicked.connect(self.next_month)
        nav_layout.addWidget(self.next_month_button)

        nav_layout.addStretch()

        self.generate_email_button = QPushButton("Genera Email")
        self.generate_email_button.setObjectName("primary")
        self.generate_email_button.clicked.connect(self.generate_email)
        nav_layout.addWidget(self.generate_email_button)

        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.addStretch()
        legend_items = {
            "Scaduto": "#EF4444",
            "In scadenza": "#F97316",
            "Avviso": "#FBBF24"
        }
        for text, color in legend_items.items():
            color_box = QLabel()
            color_box.setFixedSize(15, 15)
            color_box.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
            legend_layout.addWidget(color_box)
            legend_layout.addWidget(QLabel(text))
        nav_layout.addLayout(legend_layout)

        self.layout.addLayout(nav_layout)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.employee_tree = QTreeWidget()
        self.employee_tree.setHeaderLabels(["Dipendenti / Corsi"])
        self.employee_tree.itemExpanded.connect(self.redraw_gantt_scene)
        self.employee_tree.itemCollapsed.connect(self.redraw_gantt_scene)
        self.employee_tree.itemClicked.connect(self._on_tree_item_selected)
        font = QFont()
        font.setPointSize(10) # Smaller font for the tree
        self.employee_tree.setFont(font)
        self.splitter.addWidget(self.employee_tree)

        self.gantt_view = QGraphicsView()
        self.gantt_scene = QGraphicsScene()
        self.gantt_view.setScene(self.gantt_scene)
        self.splitter.addWidget(self.gantt_view)

        self.splitter.setSizes([250, 750])
        self.layout.addWidget(self.splitter)

        self.gantt_view.verticalScrollBar().valueChanged.connect(self.employee_tree.verticalScrollBar().setValue)
        self.employee_tree.verticalScrollBar().valueChanged.connect(self.gantt_view.verticalScrollBar().setValue)

        self.api_client = APIClient()
        self.current_date = QDate.currentDate()
        self.load_data()

    def _on_tree_item_selected(self, item, column):
        course_data = item.data(0, Qt.ItemDataRole.UserRole)
        if course_data == "employee":
            return  # Don't do anything if an employee item is clicked

        # Reset all items to their original state
        for item in self.gantt_scene.items():
            if isinstance(item, GanttBarItem):
                item.setBrush(QBrush(item.color))
                item.setPen(QPen(Qt.PenStyle.NoPen))

        # Find the corresponding bar in the Gantt chart and highlight it
        for rect_item in self.gantt_scene.items():
            if isinstance(rect_item, GanttBarItem):
                if rect_item.data(Qt.ItemDataRole.UserRole) == course_data:
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
            self.data = response.json() if response.status_code == 200 else []
        except requests.exceptions.RequestException:
            self.data = []

        self.populate_tree()

    def populate_tree(self):
        self.employee_tree.clear()
        employee_courses = defaultdict(list)
        for item in self.data:
            employee_courses[item['nome']].append(item)

        for employee, courses in sorted(employee_courses.items()):
            employee_item = QTreeWidgetItem(self.employee_tree, [employee])
            employee_item.setData(0, Qt.ItemDataRole.UserRole, "employee")
            for course in sorted(courses, key=lambda x: x['categoria']):
                course_item = QTreeWidgetItem(employee_item, [course['categoria']])
                course_item.setData(0, Qt.ItemDataRole.UserRole, course)

        self.redraw_gantt_scene()

    def redraw_gantt_scene(self):
        self.gantt_scene.clear()

        row_height = 20 # Reduced row height
        header_height = 30 # Reduced header height

        start_date = self.current_date.addDays(-self.current_date.day() + 1)
        end_date = start_date.addMonths(6)
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

        y_pos = header_height
        total_rows = 0
        root = self.employee_tree.invisibleRootItem()
        for i in range(root.childCount()):
            total_rows += 1
            if root.child(i).isExpanded():
                total_rows += root.child(i).childCount()

        scene_height = header_height + total_rows * row_height
        self.gantt_scene.setSceneRect(0, 0, scene_width, scene_height)

        # Draw Today Line
        today = QDate.currentDate()
        if start_date <= today <= end_date:
            today_x = start_date.daysTo(today) * col_width
            today_line = QGraphicsLineItem(today_x, 0, today_x, scene_height)
            today_line.setPen(QPen(QColor("#1D4ED8"), 2))
            self.gantt_scene.addItem(today_line)

        # Draw Bars
        iterator = QTreeWidgetItemIterator(self.employee_tree)
        while iterator.value():
            item = iterator.value()
            if not item.isHidden():
                if item.parent(): # Is a course
                    employee_name = item.parent().text(0)
                    course_name = item.text(0)

                    course_data = item.data(0, Qt.ItemDataRole.UserRole)
                    if course_data and course_data.get('data_scadenza'):
                        expiry_date = QDate.fromString(course_data['data_scadenza'], "dd/MM/yyyy")
                        days_to_expiry = today.daysTo(expiry_date)

                        if days_to_expiry <= 90:
                            bar_start_date = expiry_date.addDays(-30)

                            start_x = start_date.daysTo(bar_start_date) * col_width
                            end_x = start_date.daysTo(expiry_date) * col_width
                            bar_width = max(2, end_x - start_x)

                            status = "Avviso"
                            color = QColor("#FBBF24")  # Giallo (30-90)
                            if 0 <= days_to_expiry < 30:
                                color = QColor("#F97316")  # Arancione
                                status = "In scadenza"
                            if days_to_expiry < 0:
                                color = QColor("#EF4444")  # Rosso
                                status = "Scaduto"

                            gradient = QLinearGradient(start_x, y_pos, start_x + bar_width, y_pos)
                            gradient.setColorAt(0, color.lighter(120))
                            gradient.setColorAt(1, color)

                            rect = GanttBarItem(start_x, y_pos, bar_width, row_height - 5, QBrush(gradient), color, course_data)
                            self.gantt_scene.addItem(rect)
                y_pos += row_height
            iterator += 1

    def generate_email(self):
        try:
            response = requests.post(f"{self.api_client.base_url}/notifications/send-manual-alert")
            response.raise_for_status()
            QMessageBox.information(self, "Successo", "Richiesta di invio email inviata con successo.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore", f"Impossibile inviare la richiesta: {e}")

    def refresh_data(self):
        self.load_data()
