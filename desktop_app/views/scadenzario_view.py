
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
                             QSplitter, QTreeWidget, QTreeWidgetItem, QGraphicsRectItem,
                             QGraphicsTextItem, QGraphicsLineItem, QPushButton, QHBoxLayout,
                             QScrollBar, QTreeWidgetItemIterator, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QBrush, QPen, QFont
import requests
from ..api_client import API_URL
from collections import defaultdict

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

        self.layout.addLayout(nav_layout)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.employee_tree = QTreeWidget()
        self.employee_tree.setHeaderLabels(["Dipendenti / Corsi"])
        self.employee_tree.itemExpanded.connect(self.redraw_gantt_scene)
        self.employee_tree.itemCollapsed.connect(self.redraw_gantt_scene)
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

        self.current_date = QDate.currentDate()
        self.load_data()

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
            response = requests.get(f"{API_URL}/certificati/?validated=true")
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
            for course in sorted(courses, key=lambda x: x['categoria']):
                QTreeWidgetItem(employee_item, [course['categoria']])

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

                    course_data = next((c for c in self.data if c['nome'] == employee_name and c['categoria'] == course_name), None)
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

                            rect = QGraphicsRectItem(start_x, y_pos, bar_width, row_height - 5)
                            rect.setBrush(QBrush(color))
                            rect.setToolTip(f"Dipendente: {employee_name}\nCorso: {course_name}\nScadenza: {expiry_date.toString('dd/MM/yyyy')}\nStato: {status}")
                            self.gantt_scene.addItem(rect)
                y_pos += row_height
            iterator += 1

    def generate_email(self):
        try:
            response = requests.post(f"{API_URL}/notifications/send-manual-alert")
            response.raise_for_status()
            QMessageBox.information(self, "Successo", "Richiesta di invio email inviata con successo.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Errore", f"Impossibile inviare la richiesta: {e}")

    def refresh_data(self):
        self.load_data()
