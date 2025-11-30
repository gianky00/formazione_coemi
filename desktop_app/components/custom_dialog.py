from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect,
                             QHBoxLayout, QWidget, QApplication, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont
from desktop_app.components.animated_widgets import AnimatedButton

class CustomMessageDialog(QDialog):
    """
    A custom modal dialog to replace QMessageBox with a SaaS-styled design.
    Features: Frameless, Drop Shadow, Rounded Corners, Custom 'Blue' OK Button.
    Supports: Info, Warning, Error, and Question (Yes/No).
    """
    def __init__(self, title, message, parent=None, is_error=False, is_warning=False, is_question=False):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.is_question = is_question
        self.result_value = False # For Question

        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10) # Margin for shadow

        # Container Card
        self.container = QFrame()
        self.container.setObjectName("dialogContainer")
        self.container.setStyleSheet("""
            QFrame#dialogContainer {
                background-color: #FFFFFF;
                border-radius: 16px;
                border: 1px solid #E5E7EB;
            }
        """)

        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.container.setGraphicsEffect(shadow)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(24, 24, 24, 24)
        self.container_layout.setSpacing(20)

        # Title
        self.title_label = QLabel(title)
        title_color = "#DC2626" if is_error else ("#D97706" if is_warning else "#1F2937")
        self.title_label.setStyleSheet(f"color: {title_color}; font-size: 18px; font-weight: 700;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.container_layout.addWidget(self.title_label)

        # Message
        self.message_label = QLabel(message)
        self.message_label.setStyleSheet("color: #4B5563; font-size: 14px; line-height: 1.5;")
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.container_layout.addWidget(self.message_label)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()

        if is_question:
            # Cancel/No Button
            self.cancel_btn = AnimatedButton("Annulla")
            self.cancel_btn.setFixedSize(100, 40)
            self.cancel_btn.set_colors("#E5E7EB", "#D1D5DB", "#9CA3AF", text="#374151")
            self.cancel_btn.clicked.connect(self.reject)
            self.button_layout.addWidget(self.cancel_btn)

            # Yes Button
            self.yes_btn = AnimatedButton("Sì")
            self.yes_btn.setFixedSize(100, 40)
            self.yes_btn.set_colors("#1E3A8A", "#1E40AF", "#172554", text="#FFFFFF")
            self.yes_btn.clicked.connect(self.accept_question)
            self.button_layout.addWidget(self.yes_btn)
        else:
            # Single OK Button
            self.ok_btn = AnimatedButton("OK")
            self.ok_btn.setFixedSize(100, 40)
            self.ok_btn.set_colors("#1E3A8A", "#1E40AF", "#172554", text="#FFFFFF")
            self.ok_btn.clicked.connect(self.accept)
            self.button_layout.addWidget(self.ok_btn)

        self.container_layout.addLayout(self.button_layout)

        self.main_layout.addWidget(self.container)

        # Determine size
        self.setFixedWidth(400)
        self.adjustSize()

    def accept_question(self):
        self.result_value = True
        self.accept()

    @staticmethod
    def show_info(parent, title, message):
        dialog = CustomMessageDialog(title, message, parent=parent, is_error=False)
        return dialog.exec()

    @staticmethod
    def show_warning(parent, title, message):
        dialog = CustomMessageDialog(title, message, parent=parent, is_warning=True)
        return dialog.exec()

    @staticmethod
    def show_error(parent, title, message):
        dialog = CustomMessageDialog(title, message, parent=parent, is_error=True)
        return dialog.exec()

    @staticmethod
    def show_question(parent, title, message):
        """
        Returns True if user clicked Yes, False otherwise.
        """
        dialog = CustomMessageDialog(title, message, parent=parent, is_question=True)
        result = dialog.exec()
        return dialog.result_value
