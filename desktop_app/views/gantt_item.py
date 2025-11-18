
from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QColor, QBrush, QPen, QPainterPath
from PyQt6.QtCore import Qt

class GanttBarItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height, brush, color, data):
        super().__init__(x, y, width, height)
        self.color = color
        self.setBrush(brush)
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setData(Qt.ItemDataRole.UserRole, data)

        tooltip_text = f"""
        <b>Dipendente:</b> {data['nome']}<br>
        <b>Matricola:</b> {data['matricola']}<br>
        <b>Data di Nascita:</b> {data['data_nascita']}<br>
        <b>Corso:</b> {data['corso']}<br>
        <b>Categoria:</b> {data['categoria']}<br>
        <b>Scadenza:</b> {data['data_scadenza']}
        """
        self.setToolTip(tooltip_text)

    def paint(self, painter, option, widget):
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 5, 5)
        painter.fillPath(path, self.brush())
